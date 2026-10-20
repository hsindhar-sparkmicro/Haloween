"""Exercise actual idle clips and crossfades in an isolated browser fixture.

Use a server with the supplied Nun, Dracula and Pumpkin Scare media installed.
The fixture backdates inactivity; video decoding and fades run in real time.
"""
import argparse
import json
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://127.0.0.1:8094')
parser.add_argument('--cdp')
parser.add_argument('--request-url',help='Local tunnel URL for downloading fixture HTML')
parser.add_argument('--output',default='validation/idle-video/checks')
args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
html=urlopen(args.request_url or args.url).read().decode().replace('<script type="module" src="/static/app.js"></script>','')
with sync_playwright() as p:
 browser=p.chromium.connect_over_cdp(args.cdp) if args.cdp else p.chromium.launch()
 ctx=browser.new_context(viewport={'width':800,'height':480});pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
 pg.route('**/idle-video-check',lambda route:route.fulfill(body=html,content_type='text/html'))
 pg.goto(args.url+'/idle-video-check');pg.mouse.move(0,0)
 pg.evaluate('''async()=>{
  const {BackgroundRotation}=await import('/static/background-rotation.js');
  const {IdleBackgroundVideo}=await import('/static/idle-background-video.js');
  const state=await(await fetch('/api/state')).json();
  const backgrounds=new BackgroundRotation();backgrounds.configure(state.backgrounds);
  const idle=new IdleBackgroundVideo(backgrounds);idle.configure(state.cutscene.items);idle.setAllowed(true);
  window.check={backgrounds,idle,state,transitions:[]};
  new MutationObserver(()=>check.transitions.push({state:idle.layer.dataset.state,remaining:idle.video?idle.video.duration-idle.video.currentTime:null})).observe(idle.layer,{attributes:true,attributeFilter:['data-state']});
 }''')
 pg.wait_for_function('()=>[...check.backgrounds.images.values()].every(item=>item.ready)')
 reports=[];stalled=[]
 for index,clip in enumerate(['pumpkin-scare','nun','dracula']):
  pg.evaluate('''index=>{const {backgrounds:b,idle}=check;check.transitions=[];b.hold=false;b.offset=0;b.draw(index*23+5);idle.lastActivity=-1e9;idle.nextDue=0;idle.update();}''',index)
  pg.wait_for_function('clip=>{const e=document.querySelector(".idle-background-video");return e.dataset.videoId===clip&&e.dataset.state==="playing"}',arg=clip)
  pg.wait_for_timeout(1100)
  data=pg.evaluate('''()=>{const {backgrounds:b,idle}=check,v=idle.video,rect=document.querySelector('#pumpkin').getBoundingClientRect();return {id:v.dataset.cutsceneId,muted:v.muted,time:v.currentTime,opacity:Number(getComputedStyle(idle.layer).opacity),held:b.hold,foregroundAboveVideo:document.elementFromPoint(rect.x+rect.width/2,rect.y+rect.height/2).closest('#pumpkin')!==null};}''')
  assert data['muted'] and data['held'] and data['foregroundAboveVideo'] and data['opacity']>0,data
  assert pg.evaluate('''()=>{const b=check.backgrounds,id=b.current.id,phase=b.phase;b.draw(b.lastTime+30);return b.current.id===id&&b.phase===phase;}''')
  pg.screenshot(path=str(out/f'{clip}-fade-in.png'))
  pg.wait_for_function('()=>check.transitions.some(item=>item.state==="fading")',timeout=12000)
  fade=pg.evaluate('()=>check.transitions.find(item=>item.state==="fading")')
  assert fade['remaining']>=1.1,fade
  pg.wait_for_timeout(300)
  pg.screenshot(path=str(out/f'{clip}-fade-out.png'))
  pg.wait_for_function('()=>!check.idle.video',timeout=5000)
  assert pg.evaluate('()=>!check.backgrounds.hold&&check.idle.nextDue-performance.now()>=40000')
  reports.append(data);print(clip+' replay/fade passed',flush=True)
 for w,h in [(800,480),(1280,720),(1920,1080)]:
  pg.set_viewport_size({'width':w,'height':h});pg.screenshot(path=str(out/f'foreground-{w}.png'))
 pg.set_viewport_size({'width':800,'height':480})
 # Recent touch and an unknown background must not start playback.
 pg.evaluate('''()=>{const {backgrounds:b,idle}=check;b.offset=0;b.draw(5);idle.nextDue=0;document.dispatchEvent(new Event('pointerdown'));idle.update();}''')
 assert pg.evaluate('()=>!check.idle.video')
 pg.evaluate('''()=>{const {backgrounds:b,idle}=check;b.current={video_id:null};idle.lastActivity=-1e9;idle.update();}''')
 assert pg.evaluate('()=>!check.idle.video')
 # Touch fades a playing video and releases the decoder; disabling is immediate.
 for mode in ['touch','disabled']:
  pg.evaluate('''()=>{const {backgrounds:b,idle}=check;b.offset=0;b.draw(5);idle.lastActivity=-1e9;idle.nextDue=0;idle.update();}''')
  pg.wait_for_function('()=>check.idle.layer.dataset.state==="playing"');pg.wait_for_timeout(400)
  pg.evaluate("mode=>mode==='touch'?document.dispatchEvent(new Event('pointerdown')):check.idle.setAllowed(false)",mode)
  pg.wait_for_function('()=>!check.idle.video',timeout=2000)
  assert pg.evaluate('()=>!check.backgrounds.hold')
  pg.evaluate('()=>check.idle.setAllowed(true)')
 # Missing and stalled media cannot replace the image or pin rotation forever.
 for mode in ['missing','stalled']:
  if mode=='stalled':pg.route('**/api/cutscenes/stalled.mp4',lambda route:stalled.append(route))
  pg.evaluate('''mode=>{const {idle}=check;idle.start({id:mode,url:'/api/cutscenes/'+mode+'.mp4'});}''',mode)
  assert pg.evaluate('()=>Number(getComputedStyle(check.idle.layer).opacity)===0')
  pg.wait_for_function('()=>!check.idle.video',timeout=16000)
  assert pg.evaluate('()=>!check.backgrounds.hold')
 for route in stalled:route.abort()
 pg.wait_for_timeout(100)
 assert not errors,errors
 (out/'report.json').write_text(json.dumps({'clips':reports,'touch_fade':True,'disabled_release':True,'missing_and_stalled_fallback':True,'cooldown':True,'rotation_frozen_during_video':True,'unknown_image_skipped':True,'viewports':[800,1280,1920],'errors':errors},indent=2))
 print('Idle-video lifecycle checks passed',flush=True);ctx.close()
 if not args.cdp:browser.close()
