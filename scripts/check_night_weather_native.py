"""Observe natural weather changes, frame pacing and pause behavior on the native Pi."""
import argparse,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cdp',default='http://127.0.0.1:19223');parser.add_argument('--output',default='validation/night-weather/native');args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.connect_over_cdp(args.cdp);page=next(pg for ctx in browser.contexts for pg in ctx.pages if 'kiosk=1' in pg.url);page.reload();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
 page.evaluate('''()=>{window.weatherMeter={frames:0,leaves:0,snow:0,peak:0,current:0};const c=document.querySelector('#welcome-atmosphere').getContext('2d'),w=document.querySelector('#night-weather-canvas').getContext('2d');window.originalWeather={c,w,clear:c.clearRect,weatherClear:w.clearRect,image:w.drawImage};c.clearRect=function(...a){weatherMeter.frames++;return originalWeather.clear.apply(this,a);};w.clearRect=function(...a){weatherMeter.peak=Math.max(weatherMeter.peak,weatherMeter.current);weatherMeter.current=0;return originalWeather.weatherClear.apply(this,a);};w.drawImage=function(...a){weatherMeter.current++;if(a[0].width===128)weatherMeter.leaves++;if(a[0].width===48)weatherMeter.snow++;return originalWeather.image.apply(this,a);};}''')
 def measure(seconds):
  start=page.evaluate('()=>({frames:weatherMeter.frames,t:performance.now()})');page.wait_for_timeout(seconds*1000);end=page.evaluate('()=>({frames:weatherMeter.frames,t:performance.now(),leaves:weatherMeter.leaves,snow:weatherMeter.snow,peak:weatherMeter.peak})');return {'fps':round((end['frames']-start['frames'])*1000/(end['t']-start['t']),2),'seconds':round((end['t']-start['t'])/1000,2),**{k:end[k] for k in ['leaves','snow','peak']}}
 report={'baseline':measure(2)}
 for mode in ['leaves','snow']:
  page.wait_for_function('mode=>document.querySelector("#night-weather-canvas").dataset.weather===mode',arg=mode,timeout=65000);page.wait_for_timeout(4000 if mode=='leaves' else 6000);report[mode]=measure(6);assert report[mode]['fps']>=8,report
  assert report[mode][mode]>0,report
  page.screenshot(path=str(out/f'{mode}.png'));print(mode+': '+json.dumps(report[mode]),flush=True)
 page.evaluate('()=>document.querySelector("#settings-dialog").showModal()');page.wait_for_timeout(250);frames=page.evaluate('()=>weatherMeter.frames');page.wait_for_timeout(1000);assert page.evaluate('()=>weatherMeter.frames')==frames;page.evaluate('()=>document.querySelector("#settings-dialog").close()');page.wait_for_timeout(300)
 page.emulate_media(reduced_motion='reduce');page.wait_for_function('()=>document.querySelector("#night-weather-canvas").dataset.weather==="still"');page.wait_for_timeout(200);frames=page.evaluate('()=>weatherMeter.frames');page.wait_for_timeout(1000);assert page.evaluate('()=>weatherMeter.frames')==frames;page.emulate_media(reduced_motion='no-preference');page.wait_for_timeout(300)
 page.evaluate('()=>document.querySelector("[data-screen=party]").click()');page.wait_for_timeout(250);frames=page.evaluate('()=>weatherMeter.frames');page.wait_for_timeout(1000);assert page.evaluate('()=>weatherMeter.frames')==frames;page.evaluate('()=>document.querySelector("[data-screen=dashboard]").click()');page.wait_for_timeout(300)
 hit=page.locator('#pumpkin').evaluate('e=>{const r=e.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)?.closest("#pumpkin")===e;}');assert hit
 state=page.evaluate('async()=>{const s=await(await fetch("/api/state")).json();return {location:s.settings.location,music:s.tracks.length,effects:s.effects.length,camera:s.camera.armed};}')
 page.evaluate('()=>{const o=originalWeather;o.c.clearRect=o.clear;o.w.clearRect=o.weatherClear;o.w.drawImage=o.image;}');assert not errors,errors
 report.update({'modal_paused':True,'reduced_motion':True,'offscreen_paused':True,'touch_target_clear':True,'after':state,'errors':errors});(out/'report.json').write_text(json.dumps(report,indent=2));print('Native weather modes, frame pacing, pause and touch checks passed',flush=True)
