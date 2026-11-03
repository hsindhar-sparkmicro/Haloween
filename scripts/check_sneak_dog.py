"""Check alternating dog/Grinch films and the real two-minute main-film cadence."""
import argparse
import json
import time
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--browser',default='/usr/bin/brave-browser')
parser.add_argument('--url',default='http://127.0.0.1:8092')
parser.add_argument('--cdp')
parser.add_argument('--faults-only',action='store_true',help='Only the local stalled/missing dog-media checks')
parser.add_argument('--output',default='validation/dog-loop/local')
args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
if args.faults_only and args.cdp:parser.error('--faults-only uses an isolated local browser')
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp(args.cdp) if args.cdp else p.chromium.launch(executable_path=args.browser)
    page=next(pg for ctx in browser.contexts for pg in ctx.pages if 'kiosk=1' in pg.url) if args.cdp else browser.new_page(viewport={'width':800,'height':480})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    original_url=page.url if args.cdp else args.url
    parts=urlsplit(original_url);query=dict(parse_qsl(parts.query));query['dog']='video'
    page.goto(urlunsplit(parts._replace(query=urlencode(query))))
    def wait_state(state,timeout=30):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            if page.evaluate('()=>document.querySelector("#dashboard")?.dataset.arrival')==state:return
            page.wait_for_timeout(100)
        raise AssertionError(state)
    def still():
        wait_state('resting')
        assert page.locator('#peek-arrival video').get_attribute('src') is None
        assert page.locator('.welcome-backdrop:not(.welcome-backdrop-next)').evaluate('e=>getComputedStyle(e).backgroundImage.includes("forest-preparing.png")&&getComputedStyle(e).opacity==="1"')
    if args.faults_only:
        wait_state('grinch-playing',60)
        page.locator('#peek-arrival video').evaluate('v=>v.pause()');still()
        page.route('**/grinch-eight-tenths-speed.mp4',lambda r:r.abort())
        wait_state('dog-playing');still()
        page.wait_for_timeout(9000)
        assert page.locator('#peek-arrival').is_hidden()
        assert page.locator('#peek-arrival video').get_attribute('src') is None
        assert not errors,errors
        wait_state('dog-playing')
        report={'stalledGrinch':'pass','missingGrinch':'pass','dogContinuesAfterGrinchFailure':'pass','sameStillFallback':'pass','pageErrors':errors}
        (out/'faults.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
        browser.close();raise SystemExit(0)
    wait_state('playing');start=time.monotonic()
    page.evaluate('''()=>{
      window.dogCheck={events:[],violations:[],cycles:[]};let previous='',cycle=null;
      window.dogCheckTimer=setInterval(()=>{
        const root=document.querySelector('#dashboard'),state=root.dataset.arrival,v=document.querySelector('#peek-arrival video'),q=v.getVideoPlaybackQuality();
        if(state!==previous){dogCheck.events.push({state,time:performance.now()});
          if(state==='playing'||state.endsWith('-playing')){cycle={kind:root.dataset.backgroundClip,total:0,dropped:0,duration:v.duration,rate:v.playbackRate,muted:v.muted,fade:getComputedStyle(v.parentElement).transitionDuration};dogCheck.cycles.push(cycle);}previous=state;}
        if(cycle&&v.hasAttribute('src')&&!state.endsWith('loading')){cycle.total=Math.max(cycle.total,q.totalVideoFrames);cycle.dropped=Math.max(cycle.dropped,q.droppedVideoFrames);}
        if(state.includes('playing')||state.includes('settling'))for(const selector of ['.welcome-countdown','#peek-headline','.welcome-weather','.peek-strip','.peek-defrost','.peek-jingle']){
          const s=getComputedStyle(document.querySelector(selector));if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)<.99)dogCheck.violations.push({selector,state});}
      },100);
    }''')
    still();rest=time.monotonic()
    wait_state('dog-playing');assert time.monotonic()-rest>=4.5
    assert page.locator('#peek-arrival video').count()==1
    assert page.locator('#peek-arrival video').get_attribute('src').endswith('dog-eight-tenths-speed.mp4')
    page.wait_for_timeout(3000);page.screenshot(path=str(out/'dog-playing.png'))
    still();page.screenshot(path=str(out/'same-still.png'))
    wait_state('grinch-playing')
    assert page.locator('#peek-arrival video').get_attribute('src').endswith('grinch-eight-tenths-speed.mp4')
    assert page.locator('.roaming-dog').count()==0
    page.wait_for_timeout(3000);page.screenshot(path=str(out/'grinch-playing.png'));still()
    wait_state('playing',timeout=85);cadence=time.monotonic()-start
    assert 118<=cadence<=123,cadence
    report=page.evaluate('()=>{clearInterval(dogCheckTimer);return dogCheck}')
    assert not report['violations'],report['violations']
    alternatives=[c for c in report['cycles'] if c['kind']!='arrival']
    assert len(alternatives)>=4 and [c['kind'] for c in alternatives]==['dog' if i%2==0 else 'grinch' for i in range(len(alternatives))],alternatives
    assert all(12.3<c['duration']<12.8 and c['rate']==1 and c['muted'] and c['fade']=='2.4s' for c in alternatives),alternatives
    report['mainCadenceSeconds']=cadence
    print('Dog/Grinch alternation and the real two-minute repeat passed.',flush=True)
    still();wait_state('dog-playing')
    page.locator('#peek-gifts').click();still()
    assert page.locator('#peek-gift-dialog').is_visible()
    page.keyboard.press('Escape');page.wait_for_timeout(1000)
    assert page.locator('#peek-arrival').is_hidden()
    wait_state('dog-playing')
    page.locator('#pumpkin').click();wait_state('returning');wait_state('playing')
    assert page.locator('#peek-arrival video').get_attribute('src').endswith('arrival-half-speed.mp4')
    still();wait_state('dog-playing')
    page.emulate_media(reduced_motion='reduce');still()
    page.wait_for_timeout(5500)
    assert page.locator('#peek-arrival').is_hidden()
    page.emulate_media(reduced_motion='no-preference')
    assert not errors,errors
    report.update({'dialogs':'pass','manualHalloweenPriority':'pass','reducedMotion':'pass','pageErrors':errors,'nativePi':bool(args.cdp)})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
    if args.cdp:page.goto(original_url)
    else:browser.close()
