"""Inspect effective touch areas, including clipping by tile ancestors."""
import json
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8080')
parser.add_argument('--cdp')
parser.add_argument('--output',default='validation/clipping-report.json')
args=parser.parse_args()
reports=[]
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp(args.cdp) if args.cdp else p.chromium.launch()
    context=browser.new_context()
    page=context.new_page()
    for width,height in [(800,480),(1280,720),(1920,1080)]:
        page.set_viewport_size({'width':width,'height':height})
        page.goto(args.url)
        page.wait_for_function('() => document.querySelector("#connection").textContent.includes("Connected")')
        for screen in ['dashboard','haunt','party','detector']:
            page.locator(f'[data-screen="{screen}"]').click()
            controls=page.evaluate('''() => [...document.querySelector('.screen.active').querySelectorAll('button,input,select,a')].filter(e=>e.getBoundingClientRect().height>0).map(e=>{const r=e.getBoundingClientRect();let left=r.left,right=r.right,top=r.top,bottom=r.bottom;for(let parent=e.parentElement;parent;parent=parent.parentElement){const style=getComputedStyle(parent),rect=parent.getBoundingClientRect();if(/hidden|clip|auto|scroll/.test(style.overflowX)){left=Math.max(left,rect.left+parent.clientLeft);right=Math.min(right,rect.left+parent.clientLeft+parent.clientWidth);}if(/hidden|clip|auto|scroll/.test(style.overflowY)){top=Math.max(top,rect.top+parent.clientTop);bottom=Math.min(bottom,rect.top+parent.clientTop+parent.clientHeight);}}return {label:e.getAttribute('aria-label')||e.textContent.trim(),width:r.width,height:r.height,effective_width:right-left,effective_height:bottom-top};})''')
            reports.append(dict(screen=screen,width=width,height=height,controls=controls))
    context.close()
    if not args.cdp:browser.close()
Path(args.output).write_text(json.dumps(reports,indent=2))
issues=[dict(screen=r['screen'],width=r['width'],control=c) for r in reports for c in r['controls'] if c['effective_width']<47.9 or c['effective_height']<47.9]
print(json.dumps(issues,indent=2))
assert not issues, 'Clipped touch targets; see validation/clipping-report.json'
