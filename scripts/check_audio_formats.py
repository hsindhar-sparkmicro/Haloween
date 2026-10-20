"""Optional codec QA: supply a directory containing check.mp3 and check.ogg."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser()
parser.add_argument('--directory',required=True)
parser.add_argument('--url',default='http://127.0.0.1:8080')
args=parser.parse_args()
files=[Path('halloween_hub/static/assets/whisper.wav'),Path(args.directory)/'check.mp3',Path(args.directory)/'check.ogg']
reports=[]
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page()
    page.goto(args.url)
    page.wait_for_function('() => document.querySelector("#connection").textContent.includes("Connected")')
    page.locator('[data-screen="party"]').click()
    page.locator('[data-open="music-dialog"]').click()
    for file in files:
        page.locator('#music-upload').set_input_files({'name':file.name,'mimeType':'audio/'+file.suffix[1:],'buffer':file.read_bytes()})
        row=page.locator('#track-list .track-row').filter(has_text=file.name)
        row.wait_for()
        row.get_by_role('button',name='Play',exact=True).click()
        page.wait_for_function('() => document.querySelector("#music-player").currentTime > .1')
        result=page.evaluate('() => ({duration:document.querySelector("#music-player").duration,time:document.querySelector("#music-player").currentTime,error:document.querySelector("#music-player").error})')
        assert result['error'] is None and result['duration']>1
        reports.append(dict(filename=file.name,**result))
        row.get_by_role('button',name='Delete '+file.name).click()
        row.wait_for(state='detached')
    browser.close()
Path('validation/audio-formats.json').write_text(json.dumps(reports,indent=2))
print(json.dumps(reports,indent=2))
