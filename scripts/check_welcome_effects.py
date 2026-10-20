"""Exercise all welcome text effects and randomized selection in Pi Chromium."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('validation/pi-welcome-effects');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp('http://127.0.0.1:19223');native=b.contexts[0].pages[0];url=native.url
 ctx=b.new_context(viewport={'width':800,'height':480});pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
 try:
  native.goto('about:blank');pg.goto('http://127.0.0.1:8088');pg.wait_for_function('()=>!!document.querySelector(".welcome-countdown h1").dataset.textEffect')
  pg.emulate_media(reduced_motion='reduce')
  results=[]
  for w,h in [(800,480),(1280,720),(1920,1080)]:
   pg.set_viewport_size({'width':w,'height':h})
   result=pg.evaluate('''async()=>{
    const {WelcomeMessages}=await import('/static/welcome-messages.js');
    const effects=['ghost','wave','fade','title','typewriter','city'];
    const renderer=new WelcomeMessages();renderer.cycle=0;
    const rows=[];
    for(const effect of effects){for(let index=0;index<8;index++){
     renderer.select(index,effect);renderer.draw(4,true);
     const e=renderer.heading;
     if(e.scrollWidth>e.clientWidth+1)throw Error('Overflow: '+effect+' '+e.textContent);
     if(e.textContent!==e.getAttribute('aria-label'))throw Error('Accessible text mismatch');
     if(renderer.glyphs.some(({element})=>Number(element.style.opacity)<.99))throw Error('Unreadable at hold: '+effect);
     if(effect==='wave'&&!renderer.glyphs.some(({element})=>!element.style.transform.includes('0.00px,0.00px')))throw Error('No wave');
     renderer.draw(.3,true);
     if(effect==='typewriter'&&!renderer.glyphs.some(({element})=>element.style.opacity==='0'))throw Error('No typing');
     renderer.draw(4,false);
     if(renderer.glyphs.some(({element})=>element.style.opacity!=='1'||element.style.filter!=='none'))throw Error('Reduced motion failure');
     rows.push([effect,e.textContent]);
    }}
    // Four complete effect bags and three message bags, no adjacent repeats.
    const random=new WelcomeMessages(),history=[];
    for(let i=0;i<24;i++){random.draw(i*12+4,true);history.push([random.heading.dataset.textEffect,random.heading.textContent]);}
    for(let i=1;i<history.length;i++)if(history[i][0]===history[i-1][0]||history[i][1]===history[i-1][1])throw Error('Adjacent repeat');
    for(let i=0;i<24;i+=6)if(new Set(history.slice(i,i+6).map(row=>row[0])).size!==6)throw Error('Effect bag incomplete');
    for(let i=0;i<24;i+=8)if(new Set(history.slice(i,i+8).map(row=>row[1])).size!==8)throw Error('Message bag incomplete');
    window.effectPreview=new WelcomeMessages();window.effectPreview.cycle=0;
    return {rows:rows.length,history};
   }''')
   results.append({'width':w,**result})
   for effect in ['ghost','wave','fade','title','typewriter','city']:
    pg.evaluate("effect=>{effectPreview.select(6,effect);effectPreview.draw(effect==='typewriter'?1:3,true)}",effect)
    pg.screenshot(path=str(out/f'{effect}-{w}.png'))
  assert not errors,errors
  (out/'report.json').write_text(json.dumps({'matrix':results,'reduced_motion':True,'readable_hold':True,'typewriter_partial_reveal':True,'errors':errors},indent=2))
  print('Pi: all 48 message/effect combinations fit at each of three sizes; shuffle bags and reduced motion passed.')
 finally:
  ctx.close();native.goto(url)
