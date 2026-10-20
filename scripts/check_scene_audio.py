"""Codec and random-scene audio checks on a populated isolated test server."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8093');parser.add_argument('--cdp');parser.add_argument('--output',default='validation/scene-audio.json');args=parser.parse_args()
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp(args.cdp) if args.cdp else p.chromium.launch();ctx=b.new_context(viewport={'width':800,'height':480});pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto(args.url);pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")');state=pg.evaluate("async()=>await(await fetch('/api/state')).json()");assert len(state['tracks'])==6 and len(state['effects'])==10
 pg.click('[data-screen="party"]');pg.locator('[data-open="music-dialog"]').click();decoded=[]
 for kind,container,player,button in [('tracks','#track-list','#music-player','Play'),('effects','#effect-list','#cue-player','Listen')]:
  for item in state[kind]:
   row=pg.locator(container+' .track-row').filter(has_text=item['name']);row.get_by_role('button',name=button,exact=True).click();pg.wait_for_function('(q)=>{const p=document.querySelector(q);return p.currentTime>.05&&p.duration>0&&!p.error}',arg=player);decoded.append({'library':kind,'name':item['name'],'duration':pg.locator(player).evaluate('(p)=>p.duration')})
   pg.evaluate('(q)=>document.querySelector(q).pause()',player)
 for w,h in [(800,480),(1280,720),(1920,1080)]:
  pg.set_viewport_size({'width':w,'height':h});last=pg.locator('#effect-list button').last;last.scroll_into_view_if_needed();assert last.bounding_box()['height']>=48
 pg.set_viewport_size({'width':800,'height':480});pg.locator('#music-dialog [data-close]').click();pg.click('[data-screen="haunt"]');sources=[]
 for _ in range(4):
  pg.click('#activate-haunt');pg.wait_for_selector('#scene-dialog[open]');pg.wait_for_function('()=>{const p=document.querySelector("#cue-player");return !p.paused&&p.currentTime>.05}');source=pg.locator('#cue-player').get_attribute('src');assert source.startswith('/api/effects/');assert not sources or source!=sources[-1];sources.append(source)
  if len(sources)==1:
   pg.evaluate('()=>document.querySelector("#cue-player").dispatchEvent(new Event("ended"))');pg.wait_for_function('(old)=>document.querySelector("#cue-player").getAttribute("src")!==old',arg=source,timeout=7000)
  pg.click('#scene-back');assert pg.locator('#cue-player').evaluate('(p)=>p.paused');pg.wait_for_function('()=>!document.querySelector("#activate-haunt").disabled')
 pg.click('#activate-haunt');pg.wait_for_selector('#scene-dialog[open]');pg.wait_for_function('()=>!document.querySelector("#cue-player").paused');pg.evaluate('()=>document.querySelector("#sound-toggle").click()');assert pg.locator('#cue-player').evaluate('(p)=>p.paused');pg.wait_for_timeout(4300);assert pg.locator('#cue-player').evaluate('(p)=>p.paused');pg.click('#scene-back');pg.wait_for_function('()=>!document.querySelector("#activate-haunt").disabled');pg.reload();pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")');assert pg.locator('#music-player').evaluate('(p)=>p.paused') and pg.locator('#cue-player').evaluate('(p)=>p.paused');assert not errors,errors
 Path(args.output).write_text(json.dumps({'decoded':decoded,'random_sources':sources,'stop_immediate':True,'mute_cancels_future_cues':True,'restarts_muted':True,'errors':errors},indent=2));print(json.dumps({'decoded':len(decoded),'random_scene_runs':len(sources),'stop':True,'mute':True,'errors':errors}));ctx.close()
 if not args.cdp:b.close()
