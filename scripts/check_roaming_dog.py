"""Observe roaming behaviour, main-video priority, input and motion safeguards."""
import argparse
import json
import time
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cdp')
parser.add_argument('--url',default='http://127.0.0.1:8092')
parser.add_argument('--output',default='validation/roaming-dog/local')
parser.add_argument('--fallback-only',action='store_true')
args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
if args.cdp and args.fallback_only:parser.error('fault injection uses an isolated local browser')
with sync_playwright() as p:
    b=p.chromium.connect_over_cdp(args.cdp) if args.cdp else p.chromium.launch(executable_path='/usr/bin/brave-browser')
    page=next(pg for c in b.contexts for pg in c.pages if 'kiosk=1' in pg.url) if args.cdp else b.new_page(viewport={'width':800,'height':480})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    original_url=page.url if args.cdp else args.url
    parts=urlsplit(original_url);query=dict(parse_qsl(parts.query));query['dog']='roaming'
    roaming_url=urlunsplit(parts._replace(query=urlencode(query)))
    page.add_init_script('''(()=>{window.dogDrawTimes=[];let segment=0;
      new MutationObserver(records=>{for(const r of records)if(r.target.className==='roaming-dog'&&r.attributeName==='data-active')segment++;}).observe(document,{subtree:true,attributes:true,attributeFilter:['data-active']});
      const clear=CanvasRenderingContext2D.prototype.clearRect;
      CanvasRenderingContext2D.prototype.clearRect=function(...args){if(this.canvas.className==='roaming-dog'&&dogDrawTimes.length<10000)dogDrawTimes.push({time:performance.now(),vsync:document.timeline.currentTime,segment});return clear.apply(this,args);};})();''')
    if args.fallback_only:page.route('**/roaming-dog-atlas-v1.png',lambda r:r.abort())
    page.goto(roaming_url)
    def wait(expression,timeout=30):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            if page.evaluate(expression):return
            page.wait_for_timeout(100)
        raise AssertionError(expression)
    if args.fallback_only:
        wait('()=>document.querySelector("#dashboard").dataset.arrival==="dog-playing"')
        assert page.locator('.roaming-dog').get_attribute('data-asset')=='unavailable'
        assert page.locator('#peek-arrival video').get_attribute('src').endswith('dog-eight-tenths-speed.mp4')
        assert not errors,errors
        (out/'fallback.json').write_text(json.dumps({'missingAtlasVideoFallback':'pass','pageErrors':errors},indent=2)+'\n')
        b.close();print('Missing atlas uses the existing dog film.');raise SystemExit(0)
    wait('()=>document.querySelector("#dashboard").dataset.arrival==="playing"');start=time.monotonic()
    wait('()=>document.querySelector(".roaming-dog").dataset.active==="true"')
    dog=page.locator('.roaming-dog');assert dog.get_attribute('data-asset')=='ready'
    assert dog.evaluate('e=>getComputedStyle(e).pointerEvents')=='none'
    page.evaluate('''()=>{window.roamingCheck={states:[],positions:[],clips:[]};let last='';
      window.roamingCheckTimer=setInterval(()=>{const dog=document.querySelector('.roaming-dog'),state=dog.dataset.state,clip=document.querySelector('#dashboard').dataset.arrival;
        if(state!==last){roamingCheck.states.push(state);last=state;}
        roamingCheck.clips.push(clip);if(dog.dataset.active==='true'&&state==='walk'){const b=dog.getBoundingClientRect();roamingCheck.positions.push([b.x,b.y]);}
      },100);}''')
    wait('()=>document.querySelector(".roaming-dog").dataset.state==="sniff"',20)
    before=dog.evaluate('e=>getComputedStyle(e).transform');page.wait_for_timeout(600)
    assert dog.evaluate('e=>getComputedStyle(e).transform')==before
    page.screenshot(path=str(out/'sniff.png'))
    wait('()=>document.querySelector("#dashboard").dataset.arrival==="playing"',55)
    cadence=time.monotonic()-start;assert 58<cadence<63,cadence
    page.wait_for_timeout(600)
    assert dog.get_attribute('data-active')=='false'
    assert dog.evaluate('e=>{const r=e.getBoundingClientRect();return r.right<0||r.left>innerWidth}')
    assert dog.evaluate('e=>Number(getComputedStyle(e).opacity)')==1
    frozen=dog.evaluate('e=>e.toDataURL()');page.wait_for_timeout(400)
    assert dog.evaluate('e=>e.toDataURL()')==frozen
    report=page.evaluate('()=>{clearInterval(roamingCheckTimer);return roamingCheck}')
    assert 'walk' in report['states'] and 'sniff' in report['states'] and 'idle' in report['states'],report['states']
    assert max(x[0] for x in report['positions'])-min(x[0] for x in report['positions'])>20
    assert not any(s.startswith('dog-') for s in report['clips'])
    print('Natural walk/sniff/idle and unchanged minute transition passed.',flush=True)
    wait('()=>document.querySelector(".roaming-dog").dataset.active==="true"')
    page.locator('#peek-gifts').click();wait('()=>document.querySelector(".roaming-dog").dataset.active==="false"')
    assert page.locator('#peek-gift-dialog').is_visible();page.keyboard.press('Escape')
    wait('()=>document.querySelector(".roaming-dog").dataset.active==="true"')
    page.emulate_media(reduced_motion='reduce');wait('()=>document.querySelector(".roaming-dog").dataset.active==="false"')
    assert not dog.is_visible();page.emulate_media(reduced_motion='no-preference')
    wait('()=>document.querySelector(".roaming-dog").dataset.active==="true"')
    page.keyboard.press('Tab');page.locator('nav [data-screen="haunt"]').click()
    wait('()=>document.querySelector(".roaming-dog").dataset.active==="false"')
    page.locator('nav [data-screen="dashboard"]').click()
    wait('()=>document.querySelector(".roaming-dog").dataset.active==="true"')
    assert dog.evaluate('e=>e.width>=Math.min(256,e.getBoundingClientRect().width*devicePixelRatio)')
    if not args.cdp:
        for w,h in [(1280,720),(1920,1080),(390,844)]:
            page.set_viewport_size({'width':w,'height':h});wait('()=>document.querySelector(".roaming-dog").dataset.active==="true"')
            page.wait_for_timeout(700);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(out/f'layout-{w}.png'))
    assert not errors,errors
    times=page.evaluate('dogDrawTimes');pairs=[(a,z) for a,z in zip(times,times[1:]) if a['segment']==z['segment']]
    intervals=[z['vsync']-a['vsync'] for a,z in pairs if z['vsync']>a['vsync']]
    report['activeDrawFps']=1000/(sum(intervals)/len(intervals)) if intervals else None
    ordered=sorted(intervals)
    report['framePacing']={'samples':len(intervals),'p50Ms':ordered[int(len(ordered)*.5)],'p95Ms':ordered[int(len(ordered)*.95)],'p99Ms':ordered[int(len(ordered)*.99)],'maxMs':max(intervals),'over25Ms':sum(t>25 for t in intervals),'over50Ms':sum(t>50 for t in intervals),'measurement':'Browser animation timestamps during active segments; not physical panel scanout'}
    report.update({'mainCadenceSeconds':cadence,'sniffFeetStationary':'pass','videoPauseAndNoDuplicateDog':'pass','foregroundInput':'pass','reducedMotion':'pass','screenNavigation':'pass','pageErrors':errors,'nativePi':bool(args.cdp)})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['positions','clips']},indent=2),flush=True)
    if args.cdp:page.goto(original_url)
    else:b.close()
