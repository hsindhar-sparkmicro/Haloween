"""Pi browser checks for touch-revealed welcome navigation."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('validation/pi-welcome-chrome');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp('http://127.0.0.1:19223');native=b.contexts[0].pages[0];url=native.url
 ctx=b.new_context(viewport={'width':800,'height':480},has_touch=True);pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
 try:
  native.goto('about:blank');pg.goto('http://127.0.0.1:8088');pg.wait_for_function('()=>document.body.classList.contains("welcome-fullscreen")')
  for w,h in [(800,480),(1280,720),(1920,1080)]:
   pg.set_viewport_size({'width':w,'height':h});pg.wait_for_timeout(300)
   assert pg.locator('#dashboard').bounding_box()['height']==h
   assert pg.locator('header').evaluate('e=>e.inert')
   pg.screenshot(path=str(out/f'immersive-{w}.png'))
   pg.touchscreen.tap(12,h/2);pg.wait_for_timeout(350)
   assert pg.locator('header').is_visible() and not pg.locator('nav').evaluate('e=>e.inert')
   assert pg.locator('nav button').first.bounding_box()['height']>=48
   pg.screenshot(path=str(out/f'controls-{w}.png'))
   pg.locator('[data-screen="party"]').click();pg.wait_for_timeout(100)
   assert not pg.locator('body').evaluate('e=>e.classList.contains("welcome-fullscreen")')
   assert pg.locator('nav').is_visible()
   pg.locator('[data-screen="dashboard"]').click();pg.wait_for_timeout(300)
   assert pg.locator('header').evaluate('e=>e.inert')
  pg.set_viewport_size({'width':800,'height':480});pg.touchscreen.tap(12,240)
  pg.wait_for_function('()=>document.querySelector("header").inert',timeout=9500)
  pg.keyboard.press('Tab');assert not pg.locator('header').evaluate('e=>e.inert')
  # Clicking the pumpkin directly must start its adventure, without revealing bars.
  pg.reload();pg.wait_for_function('()=>document.querySelector("header").inert')
  pg.locator('#pumpkin').click();pg.wait_for_function('()=>!!document.querySelector("#visitor-dialog[open]")')
  assert pg.locator('header').evaluate('e=>e.inert')
  assert not errors,errors
  (out/'report.json').write_text(json.dumps({'viewports':[800,1280,1920],'full_height':True,'touch_reveal':True,'seven_second_hide':True,'keyboard_reveal':True,'other_screen_navigation':True,'pumpkin_no_reveal':True,'errors':errors},indent=2))
  print('Pi touch, auto-hide, keyboard, pumpkin and navigation checks passed at all three sizes.')
 finally:
  ctx.close();native.goto(url)
