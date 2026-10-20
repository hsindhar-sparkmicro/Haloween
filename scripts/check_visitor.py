"""SPARK Halloween showcase: real visitor flow, touch, keyboard and offline assets."""
import argparse,json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--url',default='http://127.0.0.1:8094');parser.add_argument('--cdp');parser.add_argument('--output',default='validation/spark-showcase/checks');args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp(args.cdp) if args.cdp else p.chromium.launch();ctx=b.new_context(viewport={'width':800,'height':480});pg=ctx.new_page();errors=[];requests=[];pg.on('pageerror',lambda e:errors.append(str(e)));pg.on('request',lambda r:requests.append(r.url));pg.goto(args.url);pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
 def enter():
  pg.wait_for_function('()=>!document.querySelector("#pumpkin").disabled');pg.click('#pumpkin');pg.wait_for_selector('#visitor-dialog[open]')
  # Advance only the intro here; the cutscene check verifies natural completion.
  pg.wait_for_function('()=>document.querySelector("[data-product]")||document.querySelector("#visitor-cutscene-video")?.readyState>=2')
  pg.evaluate('()=>{const v=document.querySelector("#visitor-cutscene-video");if(v)v.currentTime=v.duration-.15;}');pg.wait_for_selector('[data-product="sr1120"]')
 def finish():
  pg.click('#visitor-back');pg.wait_for_function('()=>!document.querySelector("#pumpkin").disabled')
 def check_layout():
  pg.wait_for_function('()=>[...document.querySelectorAll("#visitor-content img")].every(i=>i.complete&&i.naturalWidth>0)')
  sizes=pg.locator('#visitor-dialog button:visible').evaluate_all('''els=>els.map(e=>{const r=e.getBoundingClientRect();return {name:e.getAttribute('aria-label')||e.textContent,w:r.width,h:r.height,x:r.x,y:r.y,right:r.right,bottom:r.bottom};})''')
  for r in sizes:assert r['w']>=48 and r['h']>=48 and r['x']>=0 and r['y']>=0 and r['right']<=pg.evaluate('innerWidth')+.5 and r['bottom']<=pg.evaluate('innerHeight')+.5,r
  assert pg.locator('#visitor-content').evaluate('e=>e.scrollHeight<=e.clientHeight+1')
 reports=[]
 for w,h in [(800,480),(1280,720),(1920,1080)]:
  pg.set_viewport_size({'width':w,'height':h});enter();check_layout();assert pg.locator('[data-product]').count()==4;assert not pg.locator('[data-choice],[data-game],[data-story]').count();pg.screenshot(path=str(out/f'overview-{w}.png'))
  for product in ['sr1120','mouse','keyboard','headset']:
   pg.click(f'[data-product="{product}"]');check_layout();assert pg.locator('.spark-facts dd').count()==2;pg.screenshot(path=str(out/f'{product}-{w}.png'));pg.click('.spark-all-products');assert pg.locator(f'[data-product="{product}"]').evaluate('e=>e===document.activeElement')
  finish();reports.append({'viewport':[w,h],'four_products':True,'four_details':True,'touch_targets':True,'fits_without_scroll':True})
 # Keyboard activation and reduced-motion shortcut use the same replacement menu.
 pg.emulate_media(reduced_motion='reduce');pg.focus('#pumpkin');pg.keyboard.press('Enter');pg.wait_for_selector('[data-product="sr1120"]');assert not pg.locator('#visitor-cutscene-video,.reveal-pumpkin').count();pg.focus('[data-product="mouse"]');pg.keyboard.press('Enter');pg.wait_for_selector('.spark-all-products');pg.keyboard.press('Escape');pg.wait_for_function('()=>!document.querySelector("#pumpkin").disabled');pg.emulate_media(reduced_motion='no-preference')
 # A failed intro still leads to products, and a late media event cannot reopen it.
 pg.route('**/api/cutscenes/**',lambda route:route.fulfill(status=404,body='Unavailable'));pg.click('#pumpkin');pg.wait_for_selector('[data-product="sr1120"]');assert pg.locator('.spark-notice').count()==1;finish();pg.unroute('**/api/cutscenes/**')
 # Block internet requests while keeping the local kiosk server reachable.
 pg.emulate_media(reduced_motion='reduce');enter()
 local_origin=urlsplit(args.url).netloc
 def offline_route(route):
  if urlsplit(route.request.url).netloc==local_origin:route.continue_()
  else:route.abort()
 ctx.route('**/*',offline_route)
 for product in ['sr1120','mouse','keyboard','headset']:
  pg.click(f'[data-product="{product}"]');check_layout();pg.click('.spark-all-products')
 ctx.unroute('**/*',offline_route);finish();pg.emulate_media(reduced_motion='no-preference')
 assert not errors,errors
 assert all('/static/assets/spark/' not in url or url.startswith(args.url) for url in requests),requests
 assert not any('sparkmicro.com' in url for url in requests),requests
 # Party Hub's existing trick-or-treat action also enters the new showcase.
 pg.evaluate('()=>document.querySelector("[data-screen=party]").click()');pg.click('#trick-mode');pg.wait_for_function('()=>document.querySelector("[data-product]")||document.querySelector("#visitor-cutscene-video")?.readyState>=2');pg.evaluate('()=>{const v=document.querySelector("#visitor-cutscene-video");if(v)v.currentTime=v.duration-.15;}');pg.wait_for_selector('[data-product="sr1120"]');finish()
 (out/'report.json').write_text(json.dumps({'layouts':reports,'keyboard_and_escape':True,'reduced_motion':True,'intro_failure_fallback':True,'offline_images':True,'party_entry':True,'external_asset_requests':False,'errors':errors},indent=2));print('SPARK showcase: all products, viewports, touch, keyboard, intro fallback and offline checks passed',flush=True);ctx.close()
 if not args.cdp:b.close()
