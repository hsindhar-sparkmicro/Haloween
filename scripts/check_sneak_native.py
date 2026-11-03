"""Measure the actual Pi kiosk through a temporary loopback CDP tunnel.

Observe natural four-minute background cycles, transparent foreground overlays,
and decoder frame counters for at least ten minutes. Leaves the kiosk open.
"""
import argparse
import json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cdp',default='http://127.0.0.1:19223')
parser.add_argument('--output',default='validation/pi-transition')
args=parser.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp(args.cdp)
    page=next(pg for ctx in browser.contexts for pg in ctx.pages if 'kiosk=1' in pg.url)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    def wait_state(state):
        deadline=time.monotonic()+30
        while time.monotonic()<deadline:
            if page.evaluate("() => document.querySelector('#dashboard')?.dataset.arrival")==state:return
            page.wait_for_timeout(200)
        raise AssertionError(state)
    page.reload()
    wait_state("playing")
    page.evaluate('''async()=>{
      window.qualification={cycles:[],states:[],viewport:[innerWidth,innerHeight],start:performance.now(),samples:0,overlayViolations:[],weatherViolations:[],weatherUpdates:{},weatherModes:{},weatherMaxGapMs:0};
      const {NightWeather}=await import('/static/night-weather.js'),advance=NightWeather.prototype.advance;
      let lastWeather=performance.now();
      NightWeather.prototype.advance=function(...args){
        const now=performance.now(),root=document.querySelector('#dashboard'),kind=root.classList.contains('arrival-playing')?root.dataset.backgroundClip:'still';
        qualification.weatherMaxGapMs=Math.max(qualification.weatherMaxGapMs,now-lastWeather);lastWeather=now;
        qualification.weatherUpdates[kind]=(qualification.weatherUpdates[kind]||0)+1;
        const result=advance.apply(this,args);
        qualification.weatherModes[this.mode]=(qualification.weatherModes[this.mode]||0)+1;
        return result;
      };
      let prev='',cycle=null;
      window.qualificationTimer=setInterval(()=>{
        const state=document.querySelector('#dashboard').dataset.arrival,v=document.querySelector('#peek-arrival video'),now=performance.now();
        const q=v.getVideoPlaybackQuality();
        if(document.querySelector('#dashboard').classList.contains('atmosphere-paused')||document.querySelector('#night-weather-canvas').dataset.weather==='still')qualification.weatherViolations.push({state,seconds:(now-qualification.start)/1000});
        if(state!==prev){qualification.states.push({state,seconds:(now-qualification.start)/1000});
          if(state==='playing'||state.endsWith('-playing')){cycle={kind:document.querySelector('#dashboard').dataset.backgroundClip,duration:v.duration,start:now,total:0,dropped:0,baseline:null,maxTime:0,rate:v.playbackRate,muted:v.muted,fadeDuration:getComputedStyle(document.querySelector("#peek-arrival")).transitionDuration,fadeSamples:[]};qualification.cycles.push(cycle);}prev=state;}
        if(cycle&&v.hasAttribute('src')&&!state.endsWith('loading')){cycle.total=Math.max(cycle.total,q.totalVideoFrames);cycle.dropped=Math.max(cycle.dropped,q.droppedVideoFrames);cycle.maxTime=Math.max(cycle.maxTime,v.currentTime);
          if(!cycle.baseline&&v.currentTime>=1)cycle.baseline={total:q.totalVideoFrames,dropped:q.droppedVideoFrames};}
        if(state.startsWith('dog-')||state.startsWith('grinch-')||['loading','playing','settling','returning'].includes(state)){
          for(const selector of ['.welcome-countdown','#peek-headline','.welcome-weather','.peek-strip','.peek-defrost','.peek-jingle']){
            const el=document.querySelector(selector),style=getComputedStyle(el);
            if(style.display==='none'||style.visibility==='hidden'||Number(style.opacity)<.99)qualification.overlayViolations.push({selector,state,opacity:style.opacity});
          }
        }
        if(cycle&&(state==='playing'||state.endsWith('-playing'))&&now-cycle.start<6000){
          cycle.fadeSamples.push({elapsed:(now-cycle.start)/1000,opacity:Number(getComputedStyle(document.querySelector('#peek-arrival')).opacity)});
        }
        qualification.samples++;
      },100);
    }''')
    page.wait_for_timeout(3500);page.screenshot(path=str(out/'native-playing.png'))
    wait_state("resting")
    page.screenshot(path=str(out/'native-resting.png'))
    while page.evaluate('performance.now()-qualification.start')<600000:
        page.wait_for_timeout(30000)
        result=page.evaluate('qualification')
        print(json.dumps({'elapsed':round(page.evaluate('(performance.now()-qualification.start)/1000')),'cycles':len(result['cycles']),'frames':sum(c['total'] for c in result['cycles']),'dropped':sum(c['dropped'] for c in result['cycles'])}),flush=True)
    result=page.evaluate('()=>{clearInterval(qualificationTimer);return qualification}')
    result['durationSeconds']=page.evaluate('(performance.now()-qualification.start)/1000')
    result['pageErrors']=errors
    finished=[c for c in result['cycles'] if c['maxTime']>=c['duration']-.1]
    result['completeCycles']=len(finished)
    arrivals=[c for c in result['cycles'] if c['kind']=='arrival']
    result['completeMainCycles']=sum(c['kind']=='arrival' for c in finished)
    result['completeDogCycles']=sum(c['kind']=='dog' for c in finished)
    result['completeGrinchCycles']=sum(c['kind']=='grinch' for c in finished)
    all_total=sum(c['total'] for c in finished)
    all_dropped=sum(c['dropped'] for c in finished)
    # Exclude only the first second after page load, not startup on each repeat.
    baseline=finished[0]['baseline'] if finished else {'total':0,'dropped':0}
    total=all_total-baseline['total'];dropped=all_dropped-baseline['dropped']
    result['includingStartup']={'totalFrames':all_total,'droppedFrames':all_dropped,'percent':100*all_dropped/all_total if all_total else None}
    result['afterInitialStartup']={'totalFrames':total,'droppedFrames':dropped,'percent':100*dropped/total if total else None}
    steady_total=sum(c['total']-c['baseline']['total'] for c in finished if c['baseline'])
    steady_dropped=sum(c['dropped']-c['baseline']['dropped'] for c in finished if c['baseline'])
    result['afterClipStartup']={'excludedSecondsPerClip':1,'totalFrames':steady_total,'droppedFrames':steady_dropped,'percent':100*steady_dropped/steady_total if steady_total else None}
    result['cadenceSeconds']=[(b['start']-a['start'])/1000 for a,b in zip(arrivals,arrivals[1:])]
    (out/'native-ten-minute.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['cycles','states']}),flush=True)
    assert result['viewport']==[800,480],result['viewport']
    assert result['durationSeconds']>=600 and result['completeMainCycles']>=3,result
    assert steady_total>0 and result['afterClipStartup']['percent']<1,result['afterClipStartup']
    assert all(238<=t<=242 for t in result['cadenceSeconds']),result['cadenceSeconds']
    assert all(c['rate']==1 and c['muted'] for c in finished),finished
    assert not result['overlayViolations'],result['overlayViolations']
    assert not result['weatherViolations'],result['weatherViolations']
    assert all(result['weatherUpdates'].get(kind,0)>0 for kind in ['arrival','dog','grinch','still']),result['weatherUpdates']
    assert not errors,errors
    assert all(c['fadeDuration']=={'dog':'0s','grinch':'2.4s','arrival':'4.8s'}[c['kind']] for c in finished),finished
    assert all((all(s['opacity']==1 for s in c['fadeSamples']) if c['kind']=='dog' else any(.1<s['opacity']<.9 for s in c['fadeSamples'])) and any(s['opacity']>.99 for s in c['fadeSamples']) for c in finished),finished
