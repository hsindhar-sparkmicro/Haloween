"""Two effect-shuffle cycles, natural completion, pause, mute and play/pause races."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8093');parser.add_argument('--cdp');parser.add_argument('--output',default='validation/spooky-shuffle.json');args=parser.parse_args()
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp(args.cdp) if args.cdp else p.chromium.launch();ctx=b.new_context(viewport={'width':800,'height':480});pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto(args.url);pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")');state=pg.evaluate("async()=>await(await fetch('/api/state')).json()");expected={'/api/effects/'+str(item['id']) for item in state['effects']};assert len(expected)>1
 def ready():pg.wait_for_function('()=>{const p=document.querySelector("#ambience-player");return !p.paused&&p.currentTime>.05&&p.duration>0&&!p.error}')
 pg.click('#ambience-toggle');ready();sources=[]
 for i in range(len(expected)*2):
  src=pg.locator('#ambience-player').get_attribute('src');sources.append(src);assert src in expected;assert not sources[:-1] or src!=sources[-2];assert not pg.locator('#ambience-player').evaluate('(p)=>p.loop')
  pg.evaluate('()=>document.querySelector("#ambience-player").dispatchEvent(new Event("ended"))');pg.wait_for_function('(old)=>document.querySelector("#ambience-player").getAttribute("src")!==old',arg=src);ready()
 assert set(sources[:len(expected)])==expected and len(set(sources[:len(expected)]))==len(expected)
 assert set(sources[len(expected):])==expected
 before=pg.locator('#ambience-player').get_attribute('src');pg.evaluate('()=>{const p=document.querySelector("#ambience-player");p.currentTime=p.duration-.15}');pg.wait_for_function('(old)=>document.querySelector("#ambience-player").getAttribute("src")!==old',arg=before);ready()
 pg.click('#ambience-toggle');assert pg.locator('#ambience-player').evaluate('(p)=>p.paused');src=pg.locator('#ambience-player').get_attribute('src');pg.evaluate('()=>document.querySelector("#ambience-player").dispatchEvent(new Event("ended"))');pg.wait_for_timeout(350);assert pg.locator('#ambience-player').get_attribute('src')==src
 pg.click('#ambience-toggle');ready();pg.click('#sound-toggle');assert pg.locator('#ambience-player').evaluate('(p)=>p.paused');assert pg.locator('#ambience-toggle').get_attribute('aria-pressed')=='false'
 pg.evaluate('()=>{const b=document.querySelector("#ambience-toggle");b.click();b.click()}');pg.wait_for_timeout(1000);assert pg.locator('#ambience-player').evaluate('(p)=>p.paused');assert pg.locator('#ambience-toggle').get_attribute('aria-pressed')=='false'
 pg.reload();pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")');assert pg.locator('#ambience-player').evaluate('(p)=>p.paused&&!p.loop&&!p.getAttribute("src")');assert not errors,errors
 Path(args.output).write_text(json.dumps({'effects':len(expected),'two_complete_selection_cycles':sources,'ended_events':'Synthetic for cycle coverage; one real seek-to-end completion also verified','no_immediate_repeat':True,'natural_auto_advance':True,'pause':True,'mute':True,'rapid_pause_race':True,'reload_muted':True,'default_loop_absent':True,'errors':errors},indent=2));print(json.dumps({'effects':len(expected),'two_shuffle_cycles':True,'natural_advance':True,'pause_mute':True,'errors':errors}));ctx.close()
 if not args.cdp:b.close()
