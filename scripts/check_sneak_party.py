"""Verify the event card and every rotating headline at actual responsive sizes."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

out=Path('validation/sneak-peek/party');out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch();page=b.new_page();errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8092/')
    page.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
    assert page.locator('#peek-black-friday,#peek-boxing-day').count()==0
    assert page.locator('#peek-party-date').get_attribute('datetime')=='2026-12-09T17:00:00-05:00'
    assert page.locator('.peek-party strong').inner_text()=='Dîner de fin d’année'
    countdown=page.locator('#peek-party-countdown').inner_text()
    assert 'd · ' in countdown and 's' in countdown,countdown
    page.wait_for_function('(before)=>document.querySelector("#peek-party-countdown").textContent!==before',arg=countdown,timeout=3000)
    headlines=['Halloween fades.','Santa’s on his way.','More festive magic.','The Christmas app.']
    for i,text in enumerate(headlines):
        page.wait_for_function('(s)=>document.querySelector("#peek-headline").textContent.startsWith(s)',arg=text,timeout=16000)
        page.wait_for_timeout(400)
        for w,h in [(800,480),(1280,720),(1920,1080),(390,844)]:
            page.set_viewport_size({'width':w,'height':h})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(text,w)
            assert page.locator('#peek-headline').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),(text,w,'headline overflow')
            overlap=page.evaluate('''()=>{const es=[...document.querySelectorAll('.peek-strip > *, .peek-defrost,.peek-jingle,.welcome-countdown,.welcome-weather')];let bad=[];es.forEach((a,i)=>es.slice(i+1).forEach(b=>{let r=a.getBoundingClientRect(),s=b.getBoundingClientRect();if(Math.min(r.right,s.right)-Math.max(r.left,s.left)>2&&Math.min(r.bottom,s.bottom)-Math.max(r.top,s.top)>2)bad.push([a.className,b.className])}));return bad}''')
            assert not overlap,(text,w,overlap)
            assert page.locator('#peek-gifts').evaluate('e=>e.closest(".peek-strip")!==null')
            page.screenshot(path=str(out/f'headline-{i}-{w}.png'),full_page=True)
    before=page.locator('#peek-headline').inner_text()
    page.emulate_media(reduced_motion='reduce')
    page.wait_for_timeout(12500)
    assert page.locator('#peek-headline').inner_text()==before
    assert not errors,errors
    report={'party':'2026-12-09T17:00:00-05:00','liveCountdown':'pass','headlines':headlines,'layouts':[800,1280,1920,390],'reducedMotion':'pass','pageErrors':errors}
    (out/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));b.close()
