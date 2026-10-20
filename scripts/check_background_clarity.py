import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
mode=sys.argv[1] if len(sys.argv)>1 else 'after'
out=Path('validation/pi-background-clarity')/mode;out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp('http://127.0.0.1:19223');native=b.contexts[0].pages[0];url=native.url
 ctx=b.new_context(viewport={'width':800,'height':480},reduced_motion='reduce');pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
 try:
  native.goto('about:blank');pg.goto('http://127.0.0.1:8088');pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
  inventory=pg.evaluate('''async()=>{
   const {BackgroundRotation}=await import('/static/background-rotation.js');
   window.preview=new BackgroundRotation();const state=await(await fetch('/api/state')).json();preview.configure(state.backgrounds);
   await Promise.all([...preview.images.values()].map(e=>e.image.decode()));
   await new Promise(r=>setTimeout(r,50));return state.backgrounds;
  }''')
  states=[]
  for i,item in enumerate(inventory):
   details=pg.evaluate('''i=>{preview.draw((i+1)*23+3);const e=document.querySelector('.welcome-backdrop');return {id:e.dataset.backgroundId,opacity:Number(e.style.opacity),image:e.style.backgroundImage,vignette:getComputedStyle(document.querySelector('.welcome-vignette')).opacity}}''',i)
   pg.screenshot(path=str(out/f'{item["id"][:10]}-800.png'));states.append(details)
  if mode=='after':
   assert all(item['opacity']==1 and 'gradient' not in item['image'] and item['vignette']=='0.35' for item in states)
   for w,h in [(1280,720),(1920,1080)]:
    pg.set_viewport_size({'width':w,'height':h});pg.evaluate('()=>preview.draw(preview.ids.size*23+3)');pg.screenshot(path=str(out/f'wide-{w}.png'))
   transition=pg.evaluate("()=>{const result=[];for(const t of [0,20,21.5,22.99,23,23*(preview.ids.size+1)]){preview.draw(t);result.push({time:t,drop:document.querySelector('#dashboard').style.getPropertyValue('--pumpkin-drop'),opacity:Number(document.querySelector('.welcome-backdrop').style.opacity),vignette:getComputedStyle(document.querySelector('.welcome-vignette')).opacity});}return result}")
   assert transition[0]['opacity']==.84 and transition[-1]['opacity']==.84
   assert transition[2]['drop']=='15%' and transition[4]['drop']=='30%' and transition[-1]['drop']=='0%'
   (out/'transition.json').write_text(json.dumps(transition,indent=2))
  assert not errors,errors
  (out/'report.json').write_text(json.dumps({'states':states,'errors':errors},indent=2));print(mode,states)
 finally:ctx.close();native.goto(url)
