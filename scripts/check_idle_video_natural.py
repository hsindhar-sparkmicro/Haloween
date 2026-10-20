"""Check the real dashboard idle schedule and interruptions with installed media."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://127.0.0.1:8094')
parser.add_argument('--cdp')
parser.add_argument('--output',default='validation/idle-video/natural')
args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp(args.cdp) if args.cdp else p.chromium.launch()
 ctx=b.new_context(viewport={'width':800,'height':480});pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
 # Only interruption cases backdate idle time; the first replay uses the real schedule.
 pg.add_init_script('''{const now=performance.now.bind(performance);window.idleOffset=0;performance.now=()=>now()+window.idleOffset;}''')
 pg.goto(args.url);pg.mouse.move(0,0)
 pg.wait_for_selector('.idle-background-video',state='attached')
 pg.evaluate('''()=>{window.idleSamples={maxOpacity:0,seen:false,completed:false,fadeRemaining:null};
  const sample=()=>{const e=document.querySelector('.idle-background-video'),v=e.querySelector('video');
   if(v){idleSamples.seen=true;idleSamples.maxOpacity=Math.max(idleSamples.maxOpacity,Number(getComputedStyle(e).opacity));
    if(e.dataset.state==='fading'&&idleSamples.fadeRemaining===null)idleSamples.fadeRemaining=v.duration-v.currentTime;
   }else if(idleSamples.seen)idleSamples.completed=true;
   requestAnimationFrame(sample);
  };sample();}''')
 pg.wait_for_function('()=>idleSamples.maxOpacity>.95',timeout=75000)
 data=pg.locator('.idle-background-video').evaluate('(e)=>({id:e.dataset.videoId,opacity:getComputedStyle(e).opacity,muted:e.firstChild.muted,time:e.firstChild.currentTime,duration:e.firstChild.duration,background:document.querySelector(".welcome-backdrop").dataset.backgroundId})')
 assert data['muted'],data
 pg.screenshot(path=str(out/'playing.png'))
 pg.wait_for_function('()=>idleSamples.fadeRemaining!==null',timeout=25000)
 pg.screenshot(path=str(out/'fade-out.png'))
 pg.wait_for_function('()=>idleSamples.completed',timeout=5000)
 samples=pg.evaluate('()=>idleSamples');assert 1.6<=samples['fadeRemaining']<=2.0,samples
 print('Natural dashboard replay passed',flush=True)
 for mode in ['touch','dialog','other-screen','reduced-motion','hidden']:
  pg.emulate_media(reduced_motion='no-preference');pg.goto(args.url);pg.mouse.move(0,0)
  pg.wait_for_timeout(3500);pg.evaluate('()=>window.idleOffset=21000')
  pg.wait_for_function('()=>document.querySelector(".idle-background-video").dataset.state==="playing"',timeout=15000)
  if mode=='touch':pg.locator('.welcome-space').dispatch_event('pointerdown')
  elif mode=='dialog':pg.evaluate('()=>document.querySelector("#settings-dialog").showModal()')
  elif mode=='other-screen':pg.evaluate('()=>document.querySelector("[data-screen=party]").click()')
  elif mode=='reduced-motion':pg.emulate_media(reduced_motion='reduce')
  else:pg.evaluate('()=>{Object.defineProperty(document,"hidden",{value:true,configurable:true});document.dispatchEvent(new Event("visibilitychange"));}')
  pg.wait_for_function('()=>!document.querySelector(".idle-background-video video")',timeout=2500)
  print(mode+' interruption passed',flush=True)
 assert not errors,errors
 (out/'report.json').write_text(json.dumps({'playback':data,'samples':samples,'natural_schedule':True,'interruptions':['touch','dialog','other-screen','reduced-motion','hidden'],'errors':errors},indent=2))
 ctx.close()
 if not args.cdp:b.close()
