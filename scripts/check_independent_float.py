"""Verify independent line motion/fades in the actual Pi browser."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('validation/pi-independent-float');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp('http://127.0.0.1:19223');native=b.contexts[0].pages[0];url=native.url
 ctx=b.new_context(viewport={'width':800,'height':480},has_touch=True);pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
 try:
  native.goto('about:blank');pg.goto('http://127.0.0.1:8088');pg.mouse.move(0,0)
  pg.wait_for_function('()=>document.querySelector("#temperature").hasAttribute("data-float-mode")')
  first=pg.locator('#temperature').evaluate('e=>e.style.translate');pg.wait_for_timeout(2500)
  assert pg.locator('#temperature').evaluate('e=>e.style.translate')!=first
  # Freeze the live controller, then inspect long lifecycle behavior with an accelerated clock.
  pg.emulate_media(reduced_motion='reduce');pg.wait_for_timeout(200)
  result=pg.evaluate('''async()=>{
   const {WelcomeFloat}=await import('/static/welcome-float.js');
   const float=new WelcomeFloat(),snapshots=[],transitions=new Set();
   for(let t=0;t<=240;t+=.5){
    float.draw(t,true);
    const rows=float.lines.filter(l=>l.element).map(l=>({selector:l.selector,translate:l.element.style.translate,opacity:Number(l.element.style.opacity),transition:l.element.dataset.floatTransition}));
    rows.forEach(r=>{if(r.transition)transitions.add(r.transition)});
    snapshots.push(rows);
   }
   if(transitions.size<3)throw Error('Insufficient re-entry variety');
   const mixed=snapshots.filter(rows=>rows.some(r=>r.opacity<.1)&&rows.some(r=>r.opacity>.99));
   if(mixed.length<10)throw Error('Fades not staggered');
   const last=snapshots.at(-1);
   if(new Set(last.map(r=>r.translate)).size<12)throw Error('Lines move together');
   if(snapshots.some(rows=>rows.some(r=>['#weather-location','#ambience-toggle'].includes(r.selector)&&r.opacity!==1)))throw Error('Control faded');
   if(float.lines.some(l=>l.duration<28||l.duration>50))throw Error('Fast drift route');
   float.draw(241,false);
   if(float.lines.some(l=>l.element&&(l.element.style.opacity!=='1'||l.element.style.translate.split(' ').some(v=>parseFloat(v)!==0)||l.element.style.filter!=='none')))throw Error('Reduced motion');
   window.floatPreview=float;
   return {lines:last.length,unique_positions:new Set(last.map(r=>r.translate)).size,transition_types:[...transitions],mixed_fade_samples:mixed.length,drift_durations:float.lines.map(l=>l.duration),lifecycle_simulated_seconds:240};
  }''')
  for w,h in [(800,480),(1280,720),(1920,1080)]:
   pg.set_viewport_size({'width':w,'height':h});pg.evaluate('()=>floatPreview.draw(245,true)');pg.screenshot(path=str(out/f'independent-{w}.png'))
   assert pg.evaluate('''()=>floatPreview.lines.filter(l=>l.element&&l.element.getBoundingClientRect().width).every(l=>{const r=l.element.getBoundingClientRect();return r.x>=-1&&r.y>=-1&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1})''')
  # Resume production motion and verify a dialog freezes it.
  pg.reload();pg.wait_for_function('()=>document.querySelector("#temperature").hasAttribute("data-float-mode")');pg.emulate_media(reduced_motion='no-preference')
  target=pg.locator('#weather-location').bounding_box();pg.touchscreen.tap(target['x']+target['width']/2,target['y']+target['height']/2);pg.wait_for_timeout(300)
  paused=pg.locator('#temperature').evaluate('e=>e.style.translate');pg.wait_for_timeout(600);assert pg.locator('#temperature').evaluate('e=>e.style.translate')==paused
  assert not errors,errors
  (out/'report.json').write_text(json.dumps({**result,'natural_movement':True,'dialog_pause':True,'reduced_motion':True,'controls_remain_visible':True,'viewports':[800,1280,1920],'errors':errors},indent=2))
  print('Pi: independent slow lines, asynchronous fades, varied re-entry, visible controls, pause and reduced motion passed.')
 finally:
  ctx.close();native.goto(url)
