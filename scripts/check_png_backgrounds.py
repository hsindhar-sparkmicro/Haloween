"""Verify PNG-only routes, full-size browser decode and natural Pi rotation."""
import hashlib,json,time,urllib.request,urllib.error
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('validation/pi-png-backgrounds');out.mkdir(parents=True,exist_ok=True)
state=json.load(urllib.request.urlopen('http://127.0.0.1:18088/api/state'));items=state['backgrounds'];assert len(items)==2 and all(i['url'].endswith('.png') for i in items)
for item in items:
 with urllib.request.urlopen('http://127.0.0.1:18088'+item['url']) as r:
  assert r.headers.get_content_type()=='image/png';assert hashlib.sha256(r.read()).hexdigest()==item['id']
try:urllib.request.urlopen('http://127.0.0.1:18088/api/backgrounds/e1f74636887d5cf15670dbb1f544136faeab822a80f13381ceaa742831eec195.webp');raise AssertionError('Old WebP still served')
except urllib.error.HTTPError as e:assert e.code==404
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp('http://127.0.0.1:19223');native=b.contexts[0].pages[0];url=native.url
 ctx=b.new_context(viewport={'width':800,'height':480});pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
 try:
  native.goto('about:blank');pg.goto('http://127.0.0.1:8088');pg.mouse.move(0,0)
  decoded=pg.evaluate('''async()=>{const state=await(await fetch('/api/state')).json();return await Promise.all(state.backgrounds.map(async item=>{const image=new Image();image.src=item.url;await image.decode();return {id:item.id,width:image.naturalWidth,height:image.naturalHeight}}))}''')
  assert all(i['width']>=1200 and i['height']>=700 for i in decoded)
  pg.wait_for_function('()=>document.querySelector(".welcome-backdrop-next").dataset.backgroundId&&document.querySelector(".welcome-backdrop-next").dataset.backgroundId!=="original"')
  started=time.monotonic();seen=[{'id':'original','elapsed':0}]
  for index in range(3):
   pg.wait_for_function('previous=>{const e=document.querySelector(".welcome-backdrop");return e.dataset.backgroundId!==previous&&Number(e.style.opacity)>.83}',arg=seen[-1]['id'],timeout=29000)
   current=pg.locator('.welcome-backdrop').first.get_attribute('data-background-id');seen.append({'id':current,'elapsed':round(time.monotonic()-started,2)})
   if current!='original':
    assert pg.locator('.welcome-backdrop').first.evaluate('e=>Number(e.style.opacity)')==1
    for w,h in [(800,480),(1280,720),(1920,1080)]:
     pg.set_viewport_size({'width':w,'height':h});pg.screenshot(path=str(out/f'{current[:10]}-{w}.png'))
    pg.set_viewport_size({'width':800,'height':480})
   print('PNG rotation:',current,flush=True)
  assert seen[-1]['id']=='original' and len({s['id'] for s in seen})==3
  assert not errors,errors
  report={'png_only':True,'png_mime_and_hashes':True,'webp_route_404':True,'decoded_dimensions':decoded,'natural_full_cycle':seen,'viewports':[800,1280,1920],'cutscene_ids':[i['id'] for i in state['cutscene']['items']],'music_tracks':len(state['tracks']),'sound_effects':len(state['effects']),'camera_armed':state['camera']['armed'],'errors':errors}
  (out/'report.json').write_text(json.dumps(report,indent=2));print('PNG background checks passed.',flush=True)
 finally:ctx.close();native.goto(url)
