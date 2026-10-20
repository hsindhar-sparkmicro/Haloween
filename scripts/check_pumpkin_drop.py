"""Verify measured pumpkin movement through a natural background rotation on Pi."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path('validation/pi-pumpkin-drop')
out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:19223')
    native = browser.contexts[0].pages[0]
    native_url = native.url
    context = browser.new_context(viewport={'width': 800, 'height': 480})
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    def geometry():
        return page.evaluate('''() => {
            const rect = selector => {
                const r = document.querySelector(selector).getBoundingClientRect();
                return {x:r.x,y:r.y,width:r.width,height:r.height};
            };
            return {art:rect('.pumpkin-art'),face:rect('.pumpkin-face'),
                button:rect('#pumpkin'),caption:rect('.pumpkin-caption')};
        }''')
    try:
        native.goto('about:blank')
        page.goto('http://127.0.0.1:8088')
        page.wait_for_function('()=>document.querySelector(".welcome-backdrop-next").dataset.backgroundId && document.querySelector(".welcome-backdrop-next").dataset.backgroundId !== "original"')
        originals = {}
        for width, height in [(800,480),(1280,720),(1920,1080)]:
            page.set_viewport_size({'width':width,'height':height})
            page.wait_for_timeout(150)
            originals[width] = geometry()
        page.wait_for_function('()=>parseFloat(document.querySelector("#dashboard").style.getPropertyValue("--pumpkin-drop")) > 5', timeout=27000)
        mid = float(page.locator('#dashboard').evaluate('(el)=>parseFloat(el.style.getPropertyValue("--pumpkin-drop"))'))
        assert 0 < mid < 50, mid
        page.wait_for_function('()=>document.querySelector("#dashboard").style.getPropertyValue("--pumpkin-drop") === "30%"', timeout=6000)
        measurements = {}
        for width, height in [(800,480),(1280,720),(1920,1080)]:
            page.set_viewport_size({'width':width,'height':height})
            page.wait_for_timeout(150)
            current = geometry()
            for part in ('art','face'):
                delta = current[part]['y'] - originals[width][part]['y']
                assert abs(delta - current[part]['height'] * .3) < 1, (width,part,delta)
            for part in ('button','caption'):
                assert current[part] == originals[width][part], (width,part)
            assert page.locator('#pumpkin').evaluate('''el=>{
                const r=el.getBoundingClientRect();
                return el.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height*.85));
            }''')
            measurements[width] = {'original':originals[width],'lowered':current}
            page.screenshot(path=str(out/f'lowered-{width}.png'))
        page.set_viewport_size({'width':800,'height':480})
        page.wait_for_function('()=>document.querySelector(".welcome-backdrop").dataset.backgroundId === "original" && document.querySelector("#dashboard").style.getPropertyValue("--pumpkin-drop") === "0%"', timeout=80000)
        assert abs(geometry()['art']['y'] - originals[800]['art']['y']) < 1
        page.screenshot(path=str(out/'returned-800.png'))
        assert not errors, errors
        (out/'report.json').write_text(json.dumps({'natural_two_way_cycle':True,'intermediate_drop_percent':mid,'measurements':measurements,'touch_hit_test':True,'errors':errors},indent=2))
        print('Pi: 30%-height displacement, synchronized fade, return, and touch hit tests passed at three sizes.')
    finally:
        context.close()
        native.goto(native_url)
