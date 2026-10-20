"""Visitor UI integration, games, stories, hidden-camera surface and accessibility."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--cdp');parser.add_argument('--url',default='http://127.0.0.1:8080');parser.add_argument('--output',default='validation/visitor');args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp(args.cdp) if args.cdp else p.chromium.launch();ctx=b.new_context(viewport={'width':800,'height':480});pg=ctx.new_page();errors=[];requests=[];pg.on('pageerror',lambda e:errors.append(str(e)));pg.on('request',lambda r:requests.append(r.url));pg.goto(args.url);pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
 def enter():
  pg.wait_for_function('()=>!document.querySelector("#pumpkin").disabled');pg.click('#pumpkin');pg.wait_for_selector('#visitor-dialog[open]');pg.wait_for_selector('[data-choice="play"]')
 def finish():
  pg.click('#visitor-back');pg.wait_for_function('()=>!document.querySelector("#pumpkin").disabled')
 def touch_check():
  checks=pg.locator('#visitor-dialog button:visible').evaluate_all('''els=>els.map(e=>{let r=e.getBoundingClientRect();return {label:e.textContent,w:r.width,h:r.height,x:r.x,y:r.y,right:r.right,bottom:r.bottom};})''')
  for r in checks:assert r['w']>=48 and r['h']>=48 and r['x']>=0 and r['right']<=pg.evaluate('innerWidth')+.5 and r['bottom']<=pg.evaluate('innerHeight')+.5,r
 results=[]
 for w,h in [(800,480),(1280,720),(1920,1080)]:
  pg.set_viewport_size({'width':w,'height':h});enter();touch_check();pg.screenshot(path=str(out/f'lobby-{w}.png'));pg.click('[data-choice="play"]');touch_check()
  for game in ['ghost','paint','quest']:
   pg.click(f'[data-game="{game}"]');touch_check();pg.screenshot(path=str(out/f'{game}-{w}.png'))
   if game=='ghost':
    for i in range(1,4):pg.get_by_role('button',name='Find ghost '+str(i),exact=True).click()
   if game=='paint':
    before=pg.locator('#paint-lantern').inner_html();pg.click('[data-paint="eyes"]');pg.click('[data-paint="color"]');assert pg.locator('#paint-lantern').inner_html()!=before;pg.click('#paint-done')
   if game=='quest':
    for label in pg.locator('[data-answer]').all_text_contents():
     if pg.locator('#reward-again').count():break
     pg.get_by_role('button',name=label,exact=True).click()
   pg.wait_for_selector('#reward-again');touch_check();pg.click('#reward-again');pg.click('[data-choice="play"]')
  pg.click('#visitor-menu-back');pg.click('[data-choice="story"]')
  for i in range(3):
   pg.click(f'[data-story="{i}"]');touch_check();pg.screenshot(path=str(out/f'story-{i}-{w}.png'))
   for _ in range(8):
    if pg.locator('#story-end').count():break
    pg.locator('[data-next]').first.click()
   pg.click('#story-end');pg.click('#reward-again');pg.click('[data-choice="story"]')
  finish();results.append({'resolution':[w,h],'games':3,'stories':3,'touch_targets':True})
 # Choose the deterministic preferred Surprise branch through normal UI until a scene appears.
 pg.set_viewport_size({'width':800,'height':480});scene_seen=False
 for _ in range(12):
  enter();pg.click('[data-choice="surprise"]');pg.wait_for_timeout(250)
  if pg.locator('#scene-dialog').evaluate('(d)=>d.open'):
   scene_seen=True;pg.click('#scene-back');pg.wait_for_function('()=>!document.querySelector("#pumpkin").disabled');break
  finish()
 assert scene_seen,'No scene branch observed'
 # Reduced motion removes spin; keyboard activation still starts an encounter.
 pg.evaluate("()=>fetch('/api/settings',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({reduced_motion:true})})");pg.wait_for_timeout(1100);pg.focus('#pumpkin');pg.keyboard.press('Enter');pg.wait_for_selector('[data-choice="play"]');assert pg.locator('.reveal-pumpkin').count()==0;finish();pg.evaluate("()=>fetch('/api/settings',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({reduced_motion:false})})")
 pg.locator('[data-open="settings-dialog"]').last.click();pg.locator('[data-open="camera-dialog"]').last.click();assert pg.locator('#camera-dialog img,#camera-dialog video,#camera-dialog canvas').count()==0;status=pg.evaluate("async()=>({frame:(await fetch('/api/camera/frame')).status,preview:(await fetch('/api/camera',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'preview'})})).status})");assert status=={'frame':410,'preview':400},status
 pg.locator('#camera-dialog [data-close]').click();pg.locator('#settings-dialog [data-close]').click()
 assert not errors,errors
 assert sum('/api/camera/frame' in r for r in requests)==1,'Unexpected automatic camera frame request'
 (out/'report.json').write_text(json.dumps({'layouts':results,'surprise_scene':scene_seen,'hidden_camera':status,'keyboard':True,'errors':errors},indent=2));print(json.dumps({'layouts':results,'errors':errors}),flush=True);ctx.close()
 if not args.cdp:b.close()
