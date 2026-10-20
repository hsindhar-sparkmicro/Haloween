"""Pi playback and complete natural rotation of the expanded supplied gallery."""
import json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('validation/pi-dracula-gallery');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp('http://127.0.0.1:19223');native=b.contexts[0].pages[0];url=native.url
 ctx=b.new_context(viewport={'width':800,'height':480});pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
 pg.add_init_script("localStorage.setItem('halloween.last-intro','welcome');window.videoEnds=[];document.addEventListener('ended',e=>{if(e.target.id==='visitor-cutscene-video'){const v=e.target,q=v.getVideoPlaybackQuality();videoEnds.push({time:v.currentTime,duration:v.duration,src:v.currentSrc,frames:q.totalVideoFrames,dropped:q.droppedVideoFrames})}},true)")
 try:
  native.goto('about:blank');pg.goto('http://127.0.0.1:8088');pg.bring_to_front();pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
  state=pg.request.get('http://127.0.0.1:18088/api/state').json();assert len(state['backgrounds'])==4
  assert [item['id'] for item in state['cutscene']['items']]==['welcome','dracula','nun','pumpkin-scare']
  ranges={}
  for resource in ['/api/cutscenes/dracula.mp4','/api/cutscenes/dracula.webm']:
   response=pg.request.get('http://127.0.0.1:18088'+resource,headers={'Range':'bytes=0-31'});assert response.status==206 and len(response.body())==32;ranges[resource]=response.headers.get('content-range')
  videos=[]
  for w,h in [(800,480),(1280,720),(1920,1080)]:
   pg.set_viewport_size({'width':w,'height':h});pg.reload();pg.wait_for_function('()=>!document.querySelector("#pumpkin").disabled');pg.locator('#pumpkin').click()
   pg.wait_for_function('()=>document.querySelector("#visitor-cutscene-video")?.videoWidth>0&&document.querySelector("#visitor-cutscene-video").currentTime>.2')
   assert pg.locator('#visitor-cutscene-video').evaluate('v=>v.currentSrc.includes("dracula.mp4")')
   assert pg.locator('#visitor-dialog button:visible').count()==1
   pg.screenshot(path=str(out/f'dracula-{w}.png'));pg.wait_for_selector('[data-choice="play"]',timeout=15000)
   ended=pg.evaluate('videoEnds.at(-1)');assert ended['time']>=ended['duration']-.1;videos.append({'viewport':[w,h],**ended})
   pg.locator('#visitor-back').click();pg.wait_for_function('()=>!document.querySelector("#pumpkin").disabled')
   print('Dracula naturally completed at',w,flush=True)
  # The original plus all four imported backgrounds must appear in a complete real cycle.
  pg.set_viewport_size({'width':800,'height':480});pg.reload();pg.mouse.move(0,0)
  pg.wait_for_function('()=>document.querySelector(".welcome-backdrop-next").dataset.backgroundId&&document.querySelector(".welcome-backdrop-next").dataset.backgroundId!=="original"')
  seen=[];started=time.monotonic()
  for index in range(6):
   if index:
    pg.wait_for_function('previous=>{const e=document.querySelector(".welcome-backdrop");return e.dataset.backgroundId!==previous&&Number(e.style.opacity)>.83}',arg=seen[-1]['id'],timeout=29000)
   current=pg.locator('.welcome-backdrop').first.get_attribute('data-background-id');seen.append({'id':current,'elapsed':round(time.monotonic()-started,2)})
   pg.screenshot(path=str(out/f'background-{index}-{current[:10]}.png'))
   print('Background',index,current,flush=True)
  assert seen[0]['id']=='original' and seen[-1]['id']=='original' and len({item['id'] for item in seen})==5
  final=pg.request.get('http://127.0.0.1:18088/api/state').json()
  assert len(final['effects'])==len(state['effects']) and len(final['tracks'])==len(state['tracks'])
  assert not errors,errors
  (out/'report.json').write_text(json.dumps({'backgrounds_including_original':5,'cutscene_ids':[item['id'] for item in state['cutscene']['items']],'dracula_full_playback':videos,'natural_background_cycle':seen,'byte_ranges':ranges,'effects_preserved':len(final['effects']),'tracks_preserved':len(final['tracks']),'errors':errors},indent=2))
  print('Expanded Pi gallery checks passed.',flush=True)
 finally:
  ctx.close();native.goto(url)
