import json
from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp('http://127.0.0.1:19223');ctx=b.new_context(viewport={'width':800,'height':480});pg=ctx.new_page();pg.goto('http://127.0.0.1:8090');pg.wait_for_function('() => document.querySelector("#connection").textContent.includes("Connected")');pg.click('[data-screen="haunt"]');report=[]
 for name in pg.locator('#haunt-scene option').all_text_contents():
  pg.select_option('#haunt-scene',name);pg.wait_for_selector('#scene-dialog[open]');pg.wait_for_timeout(1000)
  pg.evaluate('''() => {window.draws=0;window.started=performance.now();const c=document.querySelector('#scene-canvas').getContext('2d');c.original ||= c.setTransform.bind(c);c.setTransform=(...args)=>{window.draws++;c.original(...args);};}''')
  pg.wait_for_timeout(5000);report.append(pg.evaluate('() => ({frames:draws,seconds:(performance.now()-started)/1000,fps:draws*1000/(performance.now()-started)})')|{'scene':name});pg.click('#scene-back')
 ctx.close();Path('validation/pi-immersive-fps.json').write_text(json.dumps({'pixel_readback':False,'scenes':report},indent=2));print(json.dumps(report))
