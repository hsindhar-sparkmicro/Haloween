"""Exercise the real Pi kiosk over an SSH-forwarded, loopback-only CDP port."""
import argparse
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser()
parser.add_argument('--minutes',type=float,default=60)
parser.add_argument('--cdp',default='http://127.0.0.1:19223')
parser.add_argument('--url',default='http://127.0.0.1:18088')
args=parser.parse_args()
root=Path('validation');root.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp(args.cdp, timeout=15000)
    context=browser.contexts[0]
    pages=[page for page in context.pages if ':8088' in page.url]
    page=pages[0] if pages else context.new_page()
    page.bring_to_front()
    if not pages: page.goto('http://127.0.0.1:8088')
    page.reload()
    page.wait_for_function('() => document.querySelector("#connection").textContent.includes("Connected")')
    page.wait_for_selector('#welcome-atmosphere')
    errors=[]; page.on('pageerror',lambda e:errors.append(str(e)))
    original=context.request.get(args.url+'/api/state').json()['settings']
    context.request.patch(args.url+'/api/settings',data={'rotation':True,'location':{'name':'Toronto','latitude':43.65,'longitude':-79.38}})
    context.request.post(args.url+'/api/scan',data={'active':True})
    page.locator('[data-screen="dashboard"]').click()
    page.locator('#ambience-toggle').click()
    page.wait_for_function('() => !document.querySelector("#ambience-player").paused')
    audio=page.evaluate('() => ({time:document.querySelector("#ambience-player").currentTime,volume:document.querySelector("#ambience-player").volume})')
    fps=page.evaluate('''() => new Promise(resolve=>{const start=performance.now();let frames=0;function tick(){frames++;if(performance.now()-start>=5000)resolve(frames*1000/(performance.now()-start));else requestAnimationFrame(tick);}requestAnimationFrame(tick);})''')
    feedback=page.evaluate('''() => new Promise(resolve=>{const button=document.querySelector('[data-screen="party"]');const start=performance.now();button.click();requestAnimationFrame(()=>resolve({milliseconds:performance.now()-start,screen:document.querySelector('.screen.active').id}));})''')
    page.locator('[data-screen="dashboard"]').click()
    page.evaluate('() => window.__soakStarted=performance.now()')
    started=time.monotonic();screens=set(); failures=0; samples=0
    with (root/'pi-soak.jsonl').open('w') as output:
        try:
            while time.monotonic()-started < args.minutes*60:
                health=context.request.get(args.url+'/api/health',timeout=10000)
                state=context.request.get(args.url+'/api/state',timeout=10000).json()
                screen=page.locator('.screen.active').get_attribute('id');screens.add(screen)
                if health.status!=200: failures+=1
                record={'elapsed_seconds':round(time.monotonic()-started,2),'screen':screen,'health':health.status,'weather':state['weather']['status'],'detections_shown':len(state['detections']),'errors':list(errors)}
                output.write(json.dumps(record)+'\n');output.flush();samples+=1
                if samples%3==1: print(json.dumps(record),flush=True)
                page.wait_for_timeout(20000)
        finally:
            context.request.post(args.url+'/api/scan',data={'active':False})
            context.request.patch(args.url+'/api/settings',data=original)
            page.locator('#sound-toggle').click()
            page.locator('[data-screen="dashboard"]').click()
    summary={'elapsed_seconds':round(time.monotonic()-started,2),'samples':samples,'health_failures':failures,'screens_seen':sorted(screens),'page_errors':errors,'raf_fps':round(fps,1),'navigation_feedback':feedback,'audio_playback':audio,'viewport':page.evaluate('() => ({width:innerWidth,height:innerHeight})')}
    (root/'pi-soak-summary.json').write_text(json.dumps(summary,indent=2))
    page.screenshot(path=str(root/'pi-kiosk.png'))
    print(json.dumps(summary),flush=True)
