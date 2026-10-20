"""Measure actual detail movement and touch recovery in Pi Chromium."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('validation/pi-overlay-float');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp('http://127.0.0.1:19223');native=b.contexts[0].pages[0];url=native.url
 ctx=b.new_context(viewport={'width':800,'height':480},has_touch=True);pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
 try:
  native.goto('about:blank');pg.goto('http://127.0.0.1:8088');pg.mouse.move(0,0)
  pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
  samples=pg.evaluate('''async()=>{
   const selectors=['.welcome-countdown','.welcome-weather','.welcome-sound','.welcome-countdown .digit','#temperature','#weather-condition','#weather-detail','#weather-location','#weather-status','.welcome-sound-title','.welcome-sound-description','#ambience-toggle'];
   const samples=Object.fromEntries(selectors.map(s=>[s,[]]));
   for(let i=0;i<33;i++){
    for(const s of selectors){const r=document.querySelector(s).getBoundingClientRect();samples[s].push({x:r.x,y:r.y,width:r.width,height:r.height});}
    await new Promise(r=>setTimeout(r,250));
   }
   return samples;
  }''')
  ranges={}
  for selector,points in samples.items():
   dx=max(p['x'] for p in points)-min(p['x'] for p in points);dy=max(p['y'] for p in points)-min(p['y'] for p in points)
   assert max(dx,dy)>8,(selector,dx,dy)
   assert all(p['x']>=0 and p['y']>=0 and p['x']+p['width']<=801 and p['y']+p['height']<=481 for p in points),selector
   ranges[selector]={'horizontal_px':dx,'vertical_px':dy}
  target=pg.locator('#weather-location').bounding_box();pg.touchscreen.tap(target['x']+target['width']/2,target['y']+target['height']/2)
  pg.wait_for_timeout(300);before=pg.locator('.welcome-weather').evaluate('e=>getComputedStyle(e).transform');pg.wait_for_timeout(600)
  assert pg.locator('.welcome-weather').evaluate('e=>getComputedStyle(e).transform')==before
  target=pg.locator('#settings-dialog [data-close]').bounding_box();pg.touchscreen.tap(target['x']+target['width']/2,target['y']+target['height']/2);pg.wait_for_timeout(300)
  assert pg.locator('.welcome-weather').evaluate('e=>getComputedStyle(e).animationPlayState')=='running'
  for w,h in [(800,480),(1280,720),(1920,1080)]:
   pg.set_viewport_size({'width':w,'height':h});pg.screenshot(path=str(out/f'floating-{w}.png'))
  pg.emulate_media(reduced_motion='reduce');pg.wait_for_timeout(200)
  assert pg.locator('.welcome-weather').evaluate('e=>getComputedStyle(e).transform')=='none'
  assert pg.locator('.welcome-countdown .digit').first.evaluate('e=>getComputedStyle(e).transform')=='none'
  assert not errors,errors
  (out/'report.json').write_text(json.dumps({'sample_seconds':8,'detail_movement':ranges,'inside_800x480':True,'touch_resume':True,'dialog_pause':True,'reduced_motion':True,'viewports':[800,1280,1920],'errors':errors},indent=2))
  print('Pi: every detail visibly moved, stayed on-screen, resumed after touch, and respected reduced motion.')
 finally:
  ctx.close();native.goto(url)
