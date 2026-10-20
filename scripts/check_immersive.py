"""Immersive scenes: pixels, distinct settings, seed variation and lifecycle."""
import argparse
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--cdp');parser.add_argument('--url',default='http://127.0.0.1:8080');parser.add_argument('--cycles',action='store_true');parser.add_argument('--output',default='validation/immersive-scenes');args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp(args.cdp) if args.cdp else p.chromium.launch();ctx=b.new_context(viewport={'width':800,'height':480});page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(args.url);page.wait_for_function('() => document.querySelector("#connection").textContent.includes("Connected")');page.click('[data-screen="haunt"]');names=page.locator('#haunt-scene option').all_text_contents();assert len(names)==8
 signature='''() => {const c=document.querySelector('#scene-canvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let h=2166136261;for(let i=0;i<d.length;i+=64)h=Math.imul(h^d[i],16777619);return h>>>0;}'''
 results=[]
 for name in names:
  page.select_option('#haunt-scene',name);page.wait_for_selector('#scene-dialog[open]');page.wait_for_timeout(800)
  assert page.locator('#scene-dialog button:visible').count()==1
  rect=page.locator('#scene-canvas').bounding_box();assert rect['x']==0 and rect['y']==0 and rect['width']==800 and rect['height']==480,rect
  back=page.locator('#scene-back').bounding_box();assert back['width']>=48 and back['height']>=48
  initial=page.evaluate(signature);page.wait_for_timeout(700);assert page.evaluate(signature)!=initial,name
  phases={page.locator('#haunt-stage').inner_text()};start=time.monotonic();captured=False
  while args.cycles and time.monotonic()-start<24:
   phases.add(page.locator('#haunt-stage').inner_text())
   if time.monotonic()-start>10 and not captured:
    page.screenshot(path=str(out/(name.replace(' ','-')+'.png')));captured=True
   if not page.locator('#activate-haunt').is_disabled():break
   page.wait_for_timeout(500)
  if args.cycles:
   assert 'Complete' in page.locator('#haunt-stage').inner_text(),phases
   assert len(phases)==5,phases
   assert not page.locator('#scene-dialog').evaluate('(d)=>d.open')
  else:
   page.screenshot(path=str(out/(name.replace(' ','-')+'.png')));page.click('#scene-back');page.wait_for_function('() => !document.querySelector("#activate-haunt").disabled')
  results.append({'scene':name,'canvas_motion':True,'only_back_overlay':True,'phases':sorted(phases),'automatic_return':args.cycles});print(name+' passed',flush=True)
 # Seeded variation, reduced motion, Escape and multiple resolutions.
 seeds=[]
 for _ in range(2):
  page.select_option('#haunt-scene','Purple mist');page.wait_for_selector('#scene-dialog[open]');page.wait_for_timeout(150);seeds.append(page.locator('#scene-canvas').get_attribute('data-seed'));page.keyboard.press('Escape');page.wait_for_function('() => !document.querySelector("#activate-haunt").disabled')
 assert seeds[0]!=seeds[1]
 for w,h in [(1280,720),(1920,1080)]:
  page.set_viewport_size({'width':w,'height':h});page.click('#activate-haunt');page.wait_for_selector('#scene-dialog[open]');page.wait_for_timeout(200);r=page.locator('#scene-canvas').bounding_box();assert r['width']==w and r['height']==h;r=page.locator('#scene-back').bounding_box();assert r['width']>=48 and r['height']>=48;page.click('#scene-back');page.wait_for_function('() => !document.querySelector("#activate-haunt").disabled')
 page.set_viewport_size({'width':800,'height':480});page.evaluate("() => fetch('/api/settings',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({reduced_motion:true})})");page.wait_for_timeout(1100);page.click('#activate-haunt');page.wait_for_selector('#scene-dialog[open]');page.wait_for_timeout(500);first=page.evaluate(signature);page.wait_for_timeout(600);assert page.evaluate(signature)==first;page.click('#scene-back');page.evaluate("() => fetch('/api/settings',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({reduced_motion:false})})")
 assert not errors,errors
 (out/'report.json').write_text(json.dumps({'scenes':results,'seed_variation':seeds,'reduced_motion':True,'escape_stops':True,'resolutions':[[800,480],[1280,720],[1920,1080]],'errors':errors},indent=2));ctx.close()
 if not args.cdp:b.close()
