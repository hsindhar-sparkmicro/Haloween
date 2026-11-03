"""Real encoded-media lifecycle checks; physical Pi qualification remains separate."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path('validation/sneak-peek/arrival')
OUT.mkdir(parents=True, exist_ok=True)
parser=argparse.ArgumentParser()
parser.add_argument('--browser', help='H.264-capable Chromium/Chrome/Brave executable')
parser.add_argument('--url',default='http://127.0.0.1:8092')
args=parser.parse_args()
URL=args.url
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=args.browser)
    context = browser.new_context(viewport={'width':1280,'height':720})
    tab = context.new_page()
    errors = []
    tab.on('pageerror', lambda e: errors.append(str(e)))
    def state(value):
        tab.wait_for_function('(s)=>document.querySelector("#dashboard").dataset.arrival===s', arg=value, timeout=20000)
    def replay():
        tab.locator('.peek-full').click()
        tab.locator('#peek-arrival-replay').click()
        state('playing')
    tab.goto(URL)
    state('playing')
    info=tab.locator('#peek-arrival video').evaluate('(v)=>({duration:v.duration,rate:v.playbackRate,muted:v.muted,loop:v.loop,width:v.videoWidth,height:v.videoHeight})')
    assert 12 <= info['duration'] <= 12.4 and info['rate']==1 and info['muted'] and not info['loop'], info
    assert tab.locator('#night-weather-canvas').get_attribute('data-weather')=='still'
    tab.wait_for_timeout(5000)
    tab.screenshot(path=str(OUT/'mid-film.png'))
    state('settling')
    quality=tab.locator('#peek-arrival video').evaluate('(v)=>{let q=v.getVideoPlaybackQuality();return {total:q.totalVideoFrames,dropped:q.droppedVideoFrames,time:v.currentTime}}')
    tab.screenshot(path=str(OUT/'dissolve.png'))
    state('resting')
    assert tab.locator('#peek-arrival video').get_attribute('src') is None
    assert tab.evaluate("localStorage.getItem('spark-sneak-arrival-v1')")=='done'
    for w,h in [(800,480),(1280,720),(1920,1080),(390,844)]:
        tab.set_viewport_size({'width':w,'height':h})
        tab.screenshot(path=str(OUT/f'resting-{w}.png'),full_page=True)
        assert tab.evaluate('document.documentElement.scrollWidth<=innerWidth')
    tab.reload()
    tab.wait_for_timeout(1200)
    assert tab.locator('#peek-arrival').is_hidden()
    tab.set_viewport_size({'width':1280,'height':720})
    replay()
    tab.locator('#peek-arrival-skip').click()
    state('resting')
    replay()
    tab.evaluate('''() => {Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'));}''')
    state('resting')
    assert tab.locator('#peek-arrival video').get_attribute('src') is None
    tab.evaluate("() => {delete document.hidden;document.dispatchEvent(new Event('visibilitychange'));}")
    replay()
    tab.evaluate("document.querySelector('#peek-gift-dialog').showModal()")
    state('resting')
    tab.keyboard.press('Escape')
    replay()
    tab.locator('[data-screen="party"]').click()
    state('resting')
    tab.locator('[data-screen="dashboard"]').click()
    replay()
    tab.locator('#peek-arrival video').evaluate('(v)=>v.pause()')
    state('resting')  # A stalled stream falls back after four seconds.
    tab.route('**/arrival-half-speed.mp4', lambda route: route.abort())
    tab.locator('.peek-full').click()
    tab.locator('#peek-arrival-replay').click()
    state('resting')
    tab.unroute('**/arrival-half-speed.mp4')
    context.close()
    for options in [{'reduced_motion':'reduce'}, {}]:
        ctx=browser.new_context(**options)
        page=ctx.new_page()
        if not options:
            # Offline source is unavailable; local assets remain served by kiosk.
            page.route('**/arrival-half-speed.mp4',lambda route:route.abort())
        page.goto(URL)
        page.wait_for_timeout(2500)
        assert page.locator('#peek-arrival').is_hidden()
        assert page.evaluate("localStorage.getItem('spark-sneak-arrival-v1')") is None
        assert page.locator('#peek-gifts').is_visible()
        ctx.close()
    assert not errors, errors
    report={'encodedMedia':info,'naturalPlayback':quality,'completionReloadSkipReplay':'pass','hiddenDialogNavigation':'pass','stallMissingMediaReducedMotion':'pass','pageErrors':errors,'physicalPi':'pending'}
    (OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    browser.close()
