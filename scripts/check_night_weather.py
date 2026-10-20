"""Accelerated seasonal-physics checks and screenshots; no app settings are changed."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--url',default='http://127.0.0.1:8094');parser.add_argument('--output',default='validation/night-weather/local');args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch();context=browser.new_context(reduced_motion='reduce');page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));reports=[]
 for width,height in [(800,480),(1920,1080),(3840,2160)]:
  page.set_viewport_size({'width':width,'height':height});page.goto(args.url);page.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
  page.evaluate('''async()=>{const {NightWeather}=await import('/static/night-weather.js');const canvas=document.querySelector('#night-weather-canvas');window.weatherCheck={renderer:new NightWeather(canvas),time:0,canvas,ctx:canvas.getContext('2d')};}''')
  row={'viewport':[width,height]}
  for mode in ['leaves','snow']:
   result=page.evaluate('''mode=>{const f=weatherCheck,r=f.renderer,low=innerWidth<=1000;let previous=r.blend,maxJump=0,steps=0;
    while(!(r.mode===mode&&f.time-r.started>11&&r.particles.length>10)&&steps++<6000){f.time+=1/30;r.advance(f.time,true,low);maxJump=Math.max(maxJump,Math.abs(r.blend-previous));previous=r.blend;}
    if(steps>=6000)throw Error('No weather mode '+mode);
    const before=r.particles.map(p=>[p.x,p.y]);const count=r.particles.length;
    for(let i=0;i<30;i++){f.time+=1/30;r.advance(f.time,true,low);}
    const moving=r.particles.some((p,i)=>before[i]&&Math.hypot(p.x-before[i][0],p.y-before[i][1])>.001);
    f.ctx.clearRect(0,0,innerWidth,innerHeight);r.draw(f.ctx,innerWidth,innerHeight,true);
    return {mode:r.mode,particles:r.particles.length,countBefore:count,moving,blend:r.blend,maxJump,winter:r.winter,low};}''',mode)
   assert result['moving'] and result['blend']>.9 and result['maxJump']<.05,result
   limit=(28 if width<=1000 else 54) if mode=='leaves' else (90 if width<=1000 else 180)
   assert result['particles']<=limit,result
   page.screenshot(path=str(out/f'{mode}-{width}.png'));row[mode]=result
  pause=page.evaluate('''()=>{const f=weatherCheck,r=f.renderer,before=JSON.stringify(r.particles);r.advance(f.time,false,innerWidth<=1000);f.ctx.clearRect(0,0,innerWidth,innerHeight);r.draw(f.ctx,innerWidth,innerHeight,false);const a=f.ctx.getImageData(0,0,f.canvas.width,f.canvas.height).data;return {unchanged:before===JSON.stringify(r.particles),clear:!a.some(v=>v!==0),label:f.canvas.dataset.weather,pointerEvents:getComputedStyle(f.canvas).pointerEvents};}''')
  assert pause=={'unchanged':True,'clear':True,'label':'still','pointerEvents':'none'},pause
  row['reduced_motion']=pause;reports.append(row)
 assert not errors,errors
 (out/'report.json').write_text(json.dumps({'layouts':reports,'smooth_weather_envelopes':True,'bounded_particles':True,'errors':errors},indent=2));print('Night weather: leaves, flurries, movement, fades, bounds and reduced motion passed at all sizes',flush=True);context.close();browser.close()
