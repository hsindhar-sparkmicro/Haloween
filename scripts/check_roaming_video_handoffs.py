"""Check opaque edge exits/re-entry with both real background films enabled."""
import argparse
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cdp')
parser.add_argument('--output',default='validation/roaming-handoffs/local')
args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp(args.cdp) if args.cdp else p.chromium.launch(executable_path='/usr/bin/brave-browser')
    page=next(pg for c in browser.contexts for pg in c.pages if 'kiosk=1' in pg.url) if args.cdp else browser.new_page(viewport={'width':800,'height':480})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    if args.cdp:page.goto('http://127.0.0.1:8088?kiosk=1')
    else:page.goto('http://127.0.0.1:8092')
    def wait(expression,timeout=30):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            if page.evaluate(expression):return
            page.wait_for_timeout(50)
        raise AssertionError(expression)
    wait('()=>document.querySelector("#dashboard").dataset.arrival==="playing"')
    start=time.monotonic()
    page.evaluate('''()=>{window.handoffs=[];window.handoffTimer=setInterval(()=>{
      const d=document.querySelector('.roaming-dog'),r=d.getBoundingClientRect(),root=document.querySelector('#dashboard');
      handoffs.push({time:performance.now(),state:d.dataset.state,active:d.dataset.active,clip:root.dataset.arrival,x:r.x,right:r.right,opacity:Number(getComputedStyle(d).opacity)});
    },50);}''')
    dog=page.locator('.roaming-dog')
    wait('()=>document.querySelector(".roaming-dog").dataset.state==="enter"')
    assert dog.evaluate('e=>getComputedStyle(e).transitionDuration')=='0s'
    wait('()=>document.querySelector("#dashboard").dataset.arrival==="dog-playing"')
    assert dog.get_attribute('data-state')=='offstage'
    assert dog.evaluate('e=>{const r=e.getBoundingClientRect();return r.right<0||r.left>innerWidth}')
    assert dog.evaluate('e=>getComputedStyle(e).opacity')=='1'
    assert page.locator('#peek-arrival video').get_attribute('src').endswith('dog-eight-tenths-speed.mp4')
    assert page.locator('#peek-arrival video').evaluate('e=>e.muted&&e.playbackRate===1&&Math.abs(e.duration-12.625)<.1')
    side=dog.evaluate('e=>e.getBoundingClientRect().right<0?"left":"right"')
    wait('()=>document.querySelector(".roaming-dog").dataset.state==="enter"')
    entry=dog.bounding_box()
    assert (entry['x']<100 if side=='left' else entry['x']>600),(side,entry)
    wait('()=>document.querySelector("#dashboard").dataset.arrival==="playing"')
    cadence=time.monotonic()-start;assert 58<cadence<63,cadence
    samples=page.evaluate('()=>{clearInterval(handoffTimer);return handoffs}')
    assert all(s['opacity']==1 for s in samples if s['active']=='true'), 'Dog faded while moving'
    assert {'enter','exit','offstage'}.issubset({s['state'] for s in samples})
    assert all(s['state']=='offstage' for s in samples if s['clip']=='dog-playing')
    print('Both films, opaque exits, same-edge return and minute cadence passed.',flush=True)
    wait('()=>document.querySelector(".roaming-dog").dataset.state==="idle"')
    page.locator('#pumpkin').click()
    wait('()=>["exit","exit-turn"].includes(document.querySelector(".roaming-dog").dataset.state)')
    assert dog.evaluate('e=>getComputedStyle(e).opacity')=='1'
    wait('()=>document.querySelector(".roaming-dog").dataset.state==="offstage"',5)
    assert dog.evaluate('e=>{const r=e.getBoundingClientRect();return r.right<0||r.left>innerWidth}')
    wait('()=>document.querySelector("#dashboard").dataset.arrival==="playing"')
    wait('()=>document.querySelector(".roaming-dog").dataset.state==="enter"')
    page.screenshot(path=str(out/'return-from-edge.png'))
    page.locator('#peek-gifts').click()
    assert dog.get_attribute('data-active')=='false'
    page.keyboard.press('Escape');wait('()=>document.querySelector(".roaming-dog").dataset.active==="true"')
    page.emulate_media(reduced_motion='reduce');wait('()=>document.querySelector(".roaming-dog").dataset.active==="false"')
    page.emulate_media(reduced_motion='no-preference')
    assert not errors,errors
    result={'cadenceSeconds':cadence,'opaqueEdgeExits':'pass','sameEdgeReentry':'pass','dogVideoRestored':'pass','manualReturnExit':'pass','dialogs':'pass','reducedMotion':'pass','pageErrors':errors,'samples':samples}
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='samples'},indent=2),flush=True)
    if not args.cdp:browser.close()
