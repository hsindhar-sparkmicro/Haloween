"""Check the SPARK showcase on the existing native Pi kiosk, with real intro completion."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cdp',default='http://127.0.0.1:19223');parser.add_argument('--output',default='validation/spark-showcase/native');args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.connect_over_cdp(args.cdp);pg=next(page for ctx in browser.contexts for page in ctx.pages if 'kiosk=1' in page.url);pg.reload();errors=[];external=[];pg.on('pageerror',lambda e:errors.append(str(e)));pg.on('request',lambda r:external.append(r.url) if 'sparkmicro.com' in r.url else None)
 pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")');pg.wait_for_function('()=>!document.querySelector("#pumpkin").disabled');pg.click('#pumpkin');pg.wait_for_selector('[data-product="sr1120"]',timeout=35000)
 pg.wait_for_function('()=>[...document.querySelectorAll("#visitor-content img")].every(i=>i.complete&&i.naturalWidth>0)');assert pg.locator('[data-product]').count()==4;pg.screenshot(path=str(out/'overview.png'))
 products=[]
 for product in ['sr1120','mouse','keyboard','headset']:
  pg.click(f'[data-product="{product}"]');pg.wait_for_function('()=>[...document.querySelectorAll("#visitor-content img")].every(i=>i.complete&&i.naturalWidth>0)');assert pg.locator('.spark-facts dd').count()==2
  info=pg.locator('#visitor-content').evaluate('e=>({title:e.querySelector("h1").textContent,scroll:e.scrollHeight>e.clientHeight+1,images:[...e.querySelectorAll("img")].map(i=>({src:i.getAttribute("src"),width:i.naturalWidth,height:i.naturalHeight})),facts:[...e.querySelectorAll("dd")].map(e=>e.textContent)})');assert not info['scroll'],info
  pg.screenshot(path=str(out/f'{product}.png'));products.append(info);pg.click('.spark-all-products')
 pg.click('#visitor-back');pg.wait_for_function('()=>!document.querySelector("#pumpkin").disabled');state=pg.evaluate('async()=>{const s=await(await fetch("/api/state")).json();return {welcome:s.welcome.active,music:s.tracks.length,effects:s.effects.length,camera:s.camera.armed};}');assert not state['welcome'];assert not errors and not external,(errors,external)
 (out/'report.json').write_text(json.dumps({'native_viewport':pg.viewport_size or pg.evaluate('({width:innerWidth,height:innerHeight})'),'real_intro_completion':True,'products':products,'after_exit':state,'external_asset_requests':external,'errors':errors},indent=2));print('Native Pi SPARK showcase: intro, four products, images, detail/return and clean exit passed',flush=True)
