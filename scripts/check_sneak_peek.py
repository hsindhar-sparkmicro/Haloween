"""Exercise the real sneak-peek app; screenshots and findings stay in validation/."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8092')
args = parser.parse_args()
out = Path('validation/sneak-peek')
out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    context.add_init_script('''(() => {
      localStorage.setItem('spark-sneak-arrival-v1','done');
      const Base=window.AudioContext; window.audioProbe={starts:0,ends:0};
      window.AudioContext=class extends Base {createOscillator(){const osc=super.createOscillator();
        const start=osc.start.bind(osc);osc.start=(...args)=>{audioProbe.starts++;return start(...args)};
        osc.addEventListener('ended',()=>audioProbe.ends++);return osc;}};
    })();''')
    tab = context.new_page()
    errors = []
    tab.on('pageerror', lambda e: errors.append(str(e)))
    views = []
    for w, h in [(800,480),(1280,720),(1920,1080),(390,844)]:
        tab.set_viewport_size({'width':w,'height':h})
        tab.goto(args.url)
        tab.wait_for_function('() => document.querySelector("#connection").textContent.includes("Connected")')
        tab.evaluate('document.fonts.ready')
        tab.evaluate('async()=>{let i=new Image();i.src="/static/assets/sneak-peek/forest-preparing.png";await i.decode()}')
        assert tab.evaluate('document.documentElement.scrollWidth<=innerWidth')
        if w > 600:
            assert tab.evaluate('document.documentElement.scrollHeight<=innerHeight')
            # The new action controls and seasonal cards must not overlap each other.
            overlaps=tab.evaluate('''() => {
              const els=[...document.querySelectorAll('.peek-gifts,.peek-defrost,.peek-jingle,.peek-strip,.welcome-countdown,.welcome-weather')];
              let bad=[];els.forEach((a,i)=>els.slice(i+1).forEach(b=>{let r=a.getBoundingClientRect(),s=b.getBoundingClientRect();
                if(Math.min(r.right,s.right)-Math.max(r.left,s.left)>2 && Math.min(r.bottom,s.bottom)-Math.max(r.top,s.top)>2)bad.push([a.className,b.className]);}));return bad;}''')
            assert not overlaps, (w, overlaps)
        assert tab.evaluate('audioProbe.starts') == 0
        tab.screenshot(path=str(out/f'dashboard-{w}.png'),full_page=True)
        tab.locator('#peek-gifts').click()
        for name in ['sr1120','headset','mouse']:
            tab.locator(f'[data-gift="{name}"]').click()
            tab.locator('#peek-product-image').evaluate('(i)=>i.decode()')
            assert tab.locator('#peek-product-link').get_attribute('href').startswith('https://www.sparkmicro.com/')
        if w == 800: tab.screenshot(path=str(out/'gifts-800.png'))
        tab.keyboard.press('Escape')
        assert tab.locator('#peek-gifts').evaluate('(e)=>document.activeElement===e')
        tab.locator('.peek-full').click()
        for image in tab.locator('.peek-gallery img').all(): image.evaluate('(i)=>i.decode()')
        if w == 1920: tab.screenshot(path=str(out/'full-preview-1920.png'))
        tab.keyboard.press('Escape')
        views.append({'width':w,'height':h,'giftReveals':3,'gallery':'pass','horizontalOverflow':False})
    tab.set_viewport_size({'width':1280,'height':720})
    tab.goto(args.url)
    tab.wait_for_function('() => document.querySelector("#connection").textContent.includes("Connected")')
    tab.wait_for_function('() => document.querySelector("#night-weather-canvas").dataset.weather==="snow"',timeout=16000)
    tab.wait_for_timeout(2200)
    assert tab.locator('#night-weather-canvas').evaluate('(e)=>e.getContext("2d").getImageData(0,0,e.width,e.height).data.some((v,i)=>i%4===3&&v>0)')
    tab.screenshot(path=str(out/'flurries-1280.png'))
    tab.locator('#peek-jingle').click()
    assert tab.locator('#peek-jingle').get_attribute('aria-pressed') == 'true'
    assert tab.evaluate('audioProbe.starts') == 10
    # Simulate the visibility event without weakening production CSP or autoplay rules.
    tab.evaluate('''() => {Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'));}''')
    tab.wait_for_function('() => document.querySelector("#night-weather-canvas").dataset.weather==="still"')
    tab.wait_for_function('() => audioProbe.ends===audioProbe.starts')
    tab.evaluate('''() => {delete document.hidden;document.dispatchEvent(new Event('visibilitychange'));}''')
    tab.locator('#peek-gifts').click()
    tab.wait_for_function('() => document.querySelector("#night-weather-canvas").dataset.weather==="still"')
    tab.wait_for_function('() => audioProbe.ends===audioProbe.starts')
    tab.keyboard.press('Escape')
    tab.locator('#sound-toggle').click()
    assert tab.locator('#peek-jingle').get_attribute('aria-pressed') == 'false'
    tab.emulate_media(reduced_motion='reduce')
    tab.wait_for_function('() => document.querySelector("#night-weather-canvas").dataset.weather==="still"')
    assert tab.locator('#night-weather-canvas').evaluate('(e)=>!e.getContext("2d").getImageData(0,0,e.width,e.height).data.some((v,i)=>i%4===3&&v>0)')
    tab.emulate_media(reduced_motion='no-preference')
    for screen in ['haunt','party','detector','dashboard']:
        tab.locator(f'[data-screen="{screen}"]').click()
        assert tab.locator('#'+screen).evaluate('(e)=>e.classList.contains("active")')
    # Reload preserves opt-in silence, even after an enabled audio session.
    tab.reload()
    tab.wait_for_function('() => document.querySelector("#connection").textContent.includes("Connected")')
    assert tab.evaluate('audioProbe.starts') == 0
    assert tab.locator('#peek-jingle').get_attribute('aria-pressed') == 'false'
    assert not errors, errors
    report={'views':views,'randomFlurries':'pass','dialogPause':'pass','simulatedVisibilityPause':'pass','audioOptInAndMute':'pass','reducedMotion':'pass','fourScreens':'pass','reloadMuted':'pass','pageErrors':errors,'hardwareQualification':'pending'}
    (out/'browser-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    browser.close()
