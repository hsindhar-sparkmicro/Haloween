"""Shuffle/import integration. Use an isolated test data directory, not the real playlist."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8093');parser.add_argument('--output',default='validation/playlist.json');args=parser.parse_args()
with sync_playwright() as p:
 b=p.chromium.launch();pg=b.new_page(viewport={'width':800,'height':480});errors=[];pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto(args.url);pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")');assert not pg.request.get(args.url+'/api/state').json()['tracks'],'Use an empty isolated test database'
 pg.click('[data-screen="party"]');pg.locator('[data-open="music-dialog"]').click()
 assert pg.locator('.music-source').get_attribute('href')=='https://pixabay.com/music/search/halloween/'
 assert pg.locator('#music-shuffle').is_checked()
 for name in ('quiet-scene.wav','pumpkin-scene.wav','mist-scene.wav'):
  path=Path('halloween_hub/static/assets')/name;pg.locator('#music-upload').set_input_files(str(path));pg.locator('#track-list .track-row').filter(has_text=name).wait_for()
 tracks=pg.request.get(args.url+'/api/state').json()['tracks'];pg.locator('#music-dialog [data-close]').click();pg.click('#play-track');pg.wait_for_function('()=>document.querySelector("#music-player").currentTime>.05');seen=[]
 for _ in range(6):
  before=pg.locator('#music-player').get_attribute('src');pg.click('#next-track');pg.wait_for_function('(old)=>document.querySelector("#music-player").getAttribute("src")!==old',arg=before);seen.append(pg.locator('#music-player').get_attribute('src'))
 before=pg.locator('#music-player').get_attribute('src');pg.evaluate('()=>document.querySelector("#music-player").dispatchEvent(new Event("ended"))');pg.wait_for_function('(old)=>document.querySelector("#music-player").getAttribute("src")!==old',arg=before)
 pg.locator('[data-open="music-dialog"]').click();pg.locator('#music-shuffle').uncheck();pg.wait_for_function('async()=>!(await(await fetch("/api/state")).json()).settings.music_shuffle');pg.reload();pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")');assert pg.locator('#music-player').evaluate('(e)=>e.paused');pg.click('[data-screen="party"]');pg.locator('[data-open="music-dialog"]').click();assert not pg.locator('#music-shuffle').is_checked();pg.locator('#track-list .track-row').first.get_by_role('button',name='Play',exact=True).click();pg.locator('#music-dialog [data-close]').click();pg.click('#next-track');pg.wait_for_function('(id)=>document.querySelector("#music-player").getAttribute("src")==="/api/tracks/"+id',arg=tracks[1]['id']);pg.locator('[data-open="music-dialog"]').click()
 for w,h in ((800,480),(1280,720),(1920,1080)):
  pg.set_viewport_size({'width':w,'height':h});assert pg.locator('.music-source').bounding_box()['height']>=48
 for track in tracks:assert pg.request.delete(args.url+'/api/tracks/'+str(track['id'])).ok
 assert not errors,errors
 Path(args.output).write_text(json.dumps({'three_local_imports':True,'shuffle_next_no_immediate_repeat':True,'auto_advance_shuffle':True,'sequential_mode':True,'setting_survives_reload':True,'restart_playback_muted':True,'resolutions':[800,1280,1920],'errors':errors,'external_downloads':'Blocked by Pixabay HTTP 403; no external tracks imported.'},indent=2));print('Playlist import/shuffle/sequential/persistence checks passed');b.close()
