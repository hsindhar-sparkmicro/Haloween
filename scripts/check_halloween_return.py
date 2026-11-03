"""Check the adventure link's slow return and seamless replay behind the dashboard."""
import argparse
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser()
parser.add_argument('--browser',required=True)
parser.add_argument('--url',default='http://127.0.0.1:8092')
args=parser.parse_args()
out=Path('validation/sneak-peek/return');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=args.browser)
    page=b.new_page(viewport={'width':1280,'height':720})
    errors=[];encounters=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:encounters.append(r.url) if '/api/encounter' in r.url and r.method=='POST' else None)
    def state(s,timeout=25000):
        page.wait_for_function('(s)=>document.querySelector("#dashboard").dataset.arrival===s',arg=s,timeout=timeout)
    page.goto(args.url);state('resting')
    page.locator('#pumpkin').click();state('returning');start=time.monotonic()
    assert page.locator('#peek-halloween-return').evaluate('e=>getComputedStyle(e).transitionDuration')=='4.8s'
    page.wait_for_timeout(1700)
    assert page.locator('#dashboard').get_attribute('data-arrival')=='returning'
    opacity=page.locator('#peek-halloween-return').evaluate('e=>Number(getComputedStyle(e).opacity)')
    assert .1<opacity<1,opacity
    page.screenshot(path=str(out/'slow-return.png'))
    page.locator('#pumpkin').click()  # Must not restart the fade or queue another film.
    state('playing');elapsed=time.monotonic()-start
    assert 4.7<elapsed<6.5,elapsed
    assert page.locator('#peek-arrival video').evaluate('v=>v.currentTime')<.6
    assert page.locator('#peek-halloween-return').is_hidden()
    assert page.locator('#pumpkin').evaluate('e=>document.activeElement===e')
    assert page.locator('#peek-arrival video').evaluate('v=>v.muted')
    # The adventure click reveals the navigation overlay for seven seconds.
    page.locator('#app>nav').wait_for(state='hidden',timeout=8500)
    for w,h in [(800,480),(1280,720),(1920,1080),(390,844)]:
        page.set_viewport_size({'width':w,'height':h})
        if w==390:
            page.locator('#peek-gifts').scroll_into_view_if_needed()
        assert page.locator('#peek-gifts').evaluate('e=>{let r=e.getBoundingClientRect();return e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))}')
        assert page.locator('.peek-strip').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.set_viewport_size({'width':1280,'height':720})
    # Mid-film return keeps one paused decoder, then starts from zero again.
    page.locator('#pumpkin').click();state('returning')
    assert page.locator('#peek-arrival video').evaluate('v=>v.paused')
    state('playing')
    assert page.locator('#peek-arrival video').evaluate('v=>v.currentTime')<.6
    state('resting')
    assert page.locator('#peek-arrival video').get_attribute('src') is None
    page.locator('#pumpkin').click();state('returning')
    page.locator('#peek-gifts').click();state('resting')
    assert page.locator('#peek-halloween-return').is_hidden()
    page.keyboard.press('Escape')
    page.locator('#pumpkin').click();state('returning')
    page.emulate_media(reduced_motion='reduce');state('resting')
    assert page.locator('#peek-halloween-return').is_hidden()
    page.locator('#pumpkin').click()
    assert page.locator('#dashboard').get_attribute('data-arrival')=='resting'
    assert not errors,errors
    assert not encounters,encounters
    report={'returnSeconds':round(elapsed,3),'fadeMidpointOpacity':round(opacity,3),'restingAndMidFilmReturn':'pass','repeatClicks':'pass','foregroundAndFocus':'pass','dialogAndReducedMotion':'pass','encounterRequests':encounters,'pageErrors':errors}
    (out/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    b.close()
