"""Check real background video, a real one-minute repeat, and interruption recovery."""
import argparse
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser()
parser.add_argument('--browser',help='H.264-capable Chromium/Chrome/Brave executable')
parser.add_argument('--url',default='http://127.0.0.1:8092')
args=parser.parse_args()
OUT=Path('validation/sneak-peek/arrival')
OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=args.browser)
    ctx=browser.new_context(viewport={'width':1280,'height':720})
    # Previous versions remembered completion. That must no longer suppress the film.
    ctx.add_init_script("localStorage.setItem('spark-sneak-arrival-v1','done')")
    tab=ctx.new_page()
    errors=[]
    tab.on('pageerror',lambda e:errors.append(str(e)))
    def state(value,timeout=20000):
        tab.wait_for_function('(s)=>document.querySelector("#dashboard").dataset.arrival===s',arg=value,timeout=timeout)
    def start():
        tab.goto(args.url)
        state('playing')
    def still():
        state('resting')
        assert tab.locator('#peek-arrival video').get_attribute('src') is None
    start()
    started=time.monotonic()
    info=tab.locator('#peek-arrival video').evaluate('(v)=>({duration:v.duration,rate:v.playbackRate,muted:v.muted,loop:v.loop})')
    assert 10.2 <= info['duration'] < 10.4 and info['rate']==1 and info['muted'] and not info['loop'],info
    assert tab.locator('#peek-arrival').evaluate('e=>getComputedStyle(e).transitionDuration')=='4.8s'
    tab.wait_for_timeout(1600)
    assert tab.locator('#peek-arrival').evaluate('e=>{const opacity=Number(getComputedStyle(e).opacity);return opacity>0&&opacity<.9}')
    assert tab.locator('#peek-arrival button,#peek-arrival-restart,#peek-arrival-replay').count()==0
    assert 'old magic is still here' not in tab.locator('body').inner_text().lower()
    assert tab.evaluate('document.activeElement===document.body')
    for w,h in [(800,480),(1280,720),(1920,1080),(390,844)]:
        tab.set_viewport_size({'width':w,'height':h})
        for selector in ['.welcome-countdown','.welcome-weather','.peek-strip','#peek-gifts','.peek-defrost']:
            assert tab.locator(selector).is_visible(),(w,selector)
        if w==390:
            tab.locator('#peek-gifts').scroll_into_view_if_needed()
        assert tab.locator('#peek-gifts').evaluate('e=>{let r=e.getBoundingClientRect();return e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))}')
        assert tab.evaluate('document.documentElement.scrollWidth<=innerWidth')
        tab.screenshot(path=str(OUT/f'foreground-playing-{w}.png'),full_page=True)
    tab.set_viewport_size({'width':1280,'height':720})
    tab.locator('#peek-jingle').click()
    assert tab.locator('#peek-jingle').get_attribute('aria-pressed')=='true'
    state('settling')
    quality=tab.locator('#peek-arrival video').evaluate('(v)=>{let q=v.getVideoPlaybackQuality();return {total:q.totalVideoFrames,dropped:q.droppedVideoFrames}}')
    assert tab.locator('#peek-arrival').evaluate('e=>getComputedStyle(e).transitionDuration')=='4.8s'
    tab.wait_for_timeout(2600)
    assert tab.locator('#peek-arrival').is_visible()
    still()
    assert tab.locator('#peek-jingle').get_attribute('aria-pressed')=='true'
    assert tab.locator('#peek-jingle').evaluate('e=>document.activeElement===e')
    print('First cycle, foreground controls and slow dissolve passed; waiting for the real minute repeat.',flush=True)
    state('playing',timeout=65000)
    cadence=time.monotonic()-started
    assert 58 <= cadence <= 63,cadence
    tab.locator('#peek-gifts').click()  # Usable while the video is playing.
    still()
    assert tab.locator('#peek-gift-dialog').is_visible()
    tab.keyboard.press('Escape')
    tab.wait_for_timeout(1200)
    assert tab.locator('#peek-arrival').is_hidden()  # No immediate catch-up.
    start()
    tab.evaluate("() => {Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'));}")
    still()
    tab.evaluate("() => {delete document.hidden;document.dispatchEvent(new Event('visibilitychange'));}")
    tab.wait_for_timeout(800)
    assert tab.locator('#peek-arrival').is_hidden()
    start()
    tab.keyboard.press('Escape')
    tab.locator('[data-screen="party"]').click()
    still()
    tab.keyboard.press('Escape')
    tab.locator('[data-screen="dashboard"]').click()
    assert tab.locator('#peek-arrival').is_hidden()
    start()
    tab.emulate_media(reduced_motion='reduce')
    still()
    tab.emulate_media(reduced_motion='no-preference')
    assert tab.locator('#peek-arrival').is_hidden()
    start()
    tab.locator('#peek-arrival video').evaluate('v=>v.pause()')
    still()  # Four-second stall watchdog plus dissolve.
    tab.route('**/arrival-half-speed.mp4',lambda r:r.abort())
    tab.reload()
    still()
    assert tab.locator('#peek-gifts').is_visible()
    ctx.close()
    ctx=browser.new_context(reduced_motion='reduce')
    page=ctx.new_page();page.goto(args.url)
    page.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
    assert page.locator('#peek-arrival').is_hidden()
    assert page.locator('#peek-arrival video').get_attribute('src') is None
    ctx.close()
    assert not errors,errors
    report={'media':info,'naturalPlayback':quality,'startToStartSeconds':round(cadence,3),'foregroundAndFocus':'pass','dialogsHiddenNavigationReducedMotion':'pass','stallMissingMedia':'pass','pageErrors':errors,'physicalPi':'pending'}
    (OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    browser.close()
