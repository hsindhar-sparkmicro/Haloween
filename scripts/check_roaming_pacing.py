"""Measure native roaming render cadence without screenshots or per-frame CDP traffic."""
import argparse
import json
import math
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cdp',required=True)
parser.add_argument('--seconds',type=int,default=600)
parser.add_argument('--output',default='validation/roaming-smooth/pi/pacing.json')
args=parser.parse_args()
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp(args.cdp)
    page=next(pg for c in browser.contexts for pg in c.pages if 'kiosk=1' in pg.url)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.reload()
    deadline=time.monotonic()+30
    while not page.evaluate('()=>document.querySelector(".roaming-dog")?.dataset.active==="true"'):
        if time.monotonic()>deadline:raise AssertionError('Roaming dog did not activate')
        page.wait_for_timeout(100)
    page.evaluate("""async()=>{
      const {RoamingDog}=await import('/static/roaming-dog.js');
      const draw=RoamingDog.prototype.draw,pause=RoamingDog.prototype.pause;
      window.dogPacing={frames:[],boundaries:[],segment:0,films:[],completedFilms:[]};
      const video=document.querySelector('#peek-arrival video');
      const playing=()=>dogPacing.films.push({kind:document.querySelector('#dashboard').dataset.backgroundClip,time:performance.now()});
      const ended=()=>{const q=video.getVideoPlaybackQuality();dogPacing.completedFilms.push({kind:document.querySelector('#dashboard').dataset.backgroundClip,total:q.totalVideoFrames,dropped:q.droppedVideoFrames,muted:video.muted,rate:video.playbackRate});};
      video.addEventListener('playing',playing);video.addEventListener('ended',ended);
      let previous=null;
      RoamingDog.prototype.pause=function(...args){if(this.visible)dogPacing.segment++;return pause.apply(this,args);};
      RoamingDog.prototype.draw=function(...args){
        const begin=performance.now();const result=draw.apply(this,args);
        const item={t:this.last,cost:performance.now()-begin,state:this.state,segment:dogPacing.segment,x:this.position.x,y:this.position.y,weather:document.querySelector('#night-weather-canvas').dataset.weather};
        if(dogPacing.frames.length<100000)dogPacing.frames.push(item);
        if(previous&&previous.state!==this.state&&previous.segment===item.segment){
          const weights=list=>{const m={};for(const p of list){const k=[p.pose.atlas,p.pose.index,p.pose.facing].join(':');m[k]=(m[k]||0)+p.weight;}return m;};
          const a=weights(previous.poses),b=weights(this.displayedPoses);
          dogPacing.boundaries.push({from:previous.state,to:this.state,poseWeightChange:[...new Set([...Object.keys(a),...Object.keys(b)])].reduce((n,k)=>n+Math.abs((a[k]||0)-(b[k]||0)),0),positionJump:Math.hypot(previous.x-item.x,previous.y-item.y)});
        }
        previous={...item,poses:this.displayedPoses};return result;
      };
      window.stopDogPacing=()=>{RoamingDog.prototype.draw=draw;RoamingDog.prototype.pause=pause;video.removeEventListener('playing',playing);video.removeEventListener('ended',ended);};
    }""")
    start=time.monotonic()
    try:
        while time.monotonic()-start<args.seconds:
            page.wait_for_timeout(min(30000,max(1,(args.seconds-(time.monotonic()-start))*1000)))
            print(json.dumps(page.evaluate('()=>({frames:dogPacing.frames.length,state:document.querySelector(".roaming-dog").dataset.state,active:document.querySelector(".roaming-dog").dataset.active})')),flush=True)
        data=page.evaluate('dogPacing')
    finally:
        if not page.is_closed():page.evaluate('()=>window.stopDogPacing?.()')
    frames=data.pop('frames')
    intervals=[b['t']-a['t'] for a,b in zip(frames,frames[1:]) if a['segment']==b['segment'] and b['t']>a['t']]
    def percentile(values,fraction):
        return sorted(values)[min(len(values)-1,math.floor(len(values)*fraction))]
    period=percentile(intervals,.5)
    missed=sum(max(0,round(dt/period)-1) for dt in intervals)
    arrivals=[f['time'] for f in data['films'] if f['kind']=='arrival']
    report={
        'seconds':args.seconds,'activeFrames':len(frames),'activeDrawFps':1000*len(intervals)/sum(intervals),
        'intervalMs':{'p50':period,'p95':percentile(intervals,.95),'p99':percentile(intervals,.99),'max':max(intervals)},
        'over25Ms':sum(dt>25 for dt in intervals),'over50Ms':sum(dt>50 for dt in intervals),
        'estimatedMissedRefreshPercent':100*missed/(len(intervals)+missed),
        'drawCostMs':{'p95':percentile([f['cost'] for f in frames],.95),'max':max(f['cost'] for f in frames)},
        'states':sorted({f['state'] for f in frames}),'boundaries':data['boundaries'],
        'films':data['films'],'completedFilms':data['completedFilms'],'mainCadenceSeconds':[(b-a)/1000 for a,b in zip(arrivals,arrivals[1:])],'pageErrors':errors,
        'weather':{weather:{'samples':len(group),'over25Ms':sum(dt>25 for dt in group)} for weather in {f['weather'] for f in frames} if (group:=[b['t']-a['t'] for a,b in zip(frames,frames[1:]) if a['segment']==b['segment'] and b['weather']==weather])},
        'measurement':'Native Chromium requestAnimationFrame timestamps and JS canvas submission cost; excludes intentional pauses. Does not measure panel scanout or GPU completion.',
    }
    target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='boundaries'},indent=2),flush=True)
    assert len(frames)>args.seconds*15, 'Insufficient active observations'
    assert report['activeDrawFps']>55,report
    assert report['estimatedMissedRefreshPercent']<1,report
    assert not errors,errors
    assert len(arrivals)>=args.seconds//60,arrivals
    assert all(58<t<62 for t in report['mainCadenceSeconds']),report['mainCadenceSeconds']
    # Timer/manual exits can begin between vsyncs; allow the first small blend
    # step, but reject a hard pose replacement (weight distance near two).
    assert all(b['poseWeightChange']<.2 for b in report['boundaries']),report['boundaries']
    assert all(b['positionJump']<2 for b in report['boundaries']),report['boundaries']
