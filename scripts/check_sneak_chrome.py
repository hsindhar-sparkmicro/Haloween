"""Validate immersive dashboard bars, input, focus, and phone scroll reachability."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('validation/sneak-peek/chrome');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch();page=b.new_page();errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    for w,h in [(800,480),(1280,720),(1920,1080),(390,844)]:
        page.set_viewport_size({'width':w,'height':h});page.goto('http://127.0.0.1:8092/')
        page.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
        page.locator('#app>header').wait_for(state='hidden')
        page.locator('#app>nav').wait_for(state='hidden')
        assert page.locator('#app>nav').evaluate('e=>e.inert')
        box=page.locator('#dashboard').bounding_box()
        assert abs(box['y'])<1 and abs(box['height']-h)<1,(w,box)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(out/f'immersive-{w}.png'))
        page.mouse.click(w*.5, min(h*.35,300))
        page.locator('#app>nav').wait_for(state='visible')
        assert page.locator('#app>header').is_visible()
        assert page.locator('#dashboard').bounding_box()==box  # Overlays must not resize the scene.
        page.locator('[data-screen="party"]').click()
        assert page.locator('#app>nav').is_visible()
        page.locator('[data-screen="dashboard"]').click()
        page.locator('#app>nav').wait_for(state='hidden')
        if w==390:
            page.locator('#peek-gifts').click()
            assert page.locator('#peek-gift-dialog').is_visible()
            page.keyboard.press('Escape')
            page.locator('.peek-party').scroll_into_view_if_needed()
            assert page.locator('.peek-party').evaluate('e=>{let r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}')
            assert page.locator('#dashboard').evaluate('e=>e.scrollTop>0')
    page.set_viewport_size({'width':800,'height':480});page.reload()
    page.locator('#pumpkin').click()  # Any scene click, including the adventure link, reveals the bars.
    page.locator('#app>nav').wait_for(state='visible')
    page.locator('#app>nav').wait_for(state='hidden',timeout=8500)
    page.keyboard.press('Tab')
    page.locator('#app>header').wait_for(state='visible')
    for _ in range(8):
        if page.locator('#app>header').evaluate('e=>e.contains(document.activeElement)'): break
        page.keyboard.press('Shift+Tab')
    assert page.locator('#app>header').evaluate('e=>e.contains(document.activeElement)')
    page.wait_for_timeout(7500)
    assert page.locator('#app>header').is_visible()  # Do not hide a keyboard-focused control.
    assert not errors,errors
    report={'views':[800,1280,1920,390],'fullViewport':'pass','clickRevealAndSevenSecondHide':'pass','keyboardFocus':'pass','navigation':'pass','phoneCardsReachable':'pass','pageErrors':errors}
    (out/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));b.close()
