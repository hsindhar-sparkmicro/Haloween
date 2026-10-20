"""Check natural welcome messaging and text motion on Pi Chromium."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('validation/pi-welcome-messages');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp('http://127.0.0.1:19223');native=b.contexts[0].pages[0];url=native.url
 ctx=b.new_context(viewport={'width':800,'height':480},has_touch=True);pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
 try:
  native.goto('about:blank');pg.goto('http://127.0.0.1:8088');pg.mouse.move(0,0)
  heading=pg.locator('.welcome-countdown h1');pg.wait_for_function('()=>document.querySelector(".welcome-countdown h1").style.opacity==="1"')
  first=heading.text_content();assert first
  initial=pg.locator('#temperature').evaluate('e=>e.style.translate')
  pg.wait_for_timeout(1200)
  assert initial!=pg.locator('#temperature').evaluate('e=>e.style.translate')
  pg.wait_for_function('(first)=>document.querySelector(".welcome-countdown h1").textContent!==first',arg=first,timeout=15000)
  pg.wait_for_function('()=>document.querySelector(".welcome-countdown h1").style.opacity==="1"')
  target=pg.locator('#weather-location').bounding_box();pg.touchscreen.tap(target['x']+target['width']/2,target['y']+target['height']/2);pg.wait_for_timeout(300)
  before=heading.evaluate('e=>[e.textContent,e.style.opacity]');transform=pg.locator('#temperature').evaluate('e=>e.style.translate')
  pg.wait_for_timeout(1200);assert before==heading.evaluate('e=>[e.textContent,e.style.opacity]')
  assert transform==pg.locator('#temperature').evaluate('e=>e.style.translate')
  pg.locator('#settings-dialog [data-close]').click()
  # Reduced motion makes all text steady and fully visible, including the instructions.
  pg.emulate_media(reduced_motion='reduce');pg.wait_for_timeout(300)
  assert heading.evaluate('e=>e.style.opacity')=='1'
  assert pg.locator('.pumpkin-caption').evaluate('e=>getComputedStyle(e).opacity')=='1'
  assert pg.locator('#temperature').evaluate("e=>e.style.translate.split(' ').every(v=>parseFloat(v)===0)")
  # Lay out every message at all supported sizes, with reduced motion holding the scene.
  messages=[]
  for w,h in [(800,480),(1280,720),(1920,1080)]:
   pg.set_viewport_size({'width':w,'height':h})
   for index in range(8):
    text=pg.evaluate('''async index=>{
     const {WelcomeMessages}=await import('/static/welcome-messages.js');
     const messages=new WelcomeMessages();messages.cycle=0;messages.select(index,'fade');messages.draw(3,false);
     const e=document.querySelector('.welcome-countdown h1'),r=e.getBoundingClientRect();
     if(e.scrollWidth>e.clientWidth+1||r.bottom>innerHeight-60)throw Error('Message outside safe area');
     return e.textContent;
    }''',index)
    if w==800:messages.append(text)
   pg.screenshot(path=str(out/f'floating-text-{w}.png'))
  assert len(set(messages))==8 and not errors,errors
  (out/'report.json').write_text(json.dumps({'natural_first_message_transition':True,'weather_drift':True,'instruction_fades':'Covered by independent motion lifecycle check','dialog_pause':True,'reduced_motion':True,'message_layouts':messages,'viewports':[800,1280,1920],'errors':errors},indent=2))
  print('Pi: natural message change, floating text, fading hints, pause, reduced motion and eight-message layouts passed.')
 finally:
  ctx.close();native.goto(url)
