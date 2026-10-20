"""Check sharp local images and responsive layout through 4K and high-DPI displays."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--url',default='http://127.0.0.1:8094');parser.add_argument('--output',default='validation/spark-showcase/high-resolution/checks');args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch();reports=[];errors=[]
 for w,h,dpr in [(800,480,1),(1920,1080,1),(2560,1440,1),(3840,2160,1),(1920,1080,2)]:
  context=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr,reduced_motion='reduce');page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(args.url);page.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")');page.click('#pumpkin');page.wait_for_selector('[data-product="sr1120"]')
  def images():
   page.wait_for_function('()=>[...document.querySelectorAll("#visitor-content img")].every(i=>i.complete&&i.naturalWidth>0)')
   values=page.locator('#visitor-content img').evaluate_all('''async elements=>Promise.all(elements.map(async img=>{const raw=new Image();raw.src=img.currentSrc;await raw.decode();const r=img.getBoundingClientRect(),scale=Math.min(r.width/raw.naturalWidth,r.height/raw.naturalHeight);return {src:img.currentSrc.split('/').pop(),source:[raw.naturalWidth,raw.naturalHeight],box:[r.width,r.height],dpr:devicePixelRatio,physicalPixelScale:scale*devicePixelRatio};}))''')
   for item in values:assert item['physicalPixelScale']<=1.02,item
   assert page.locator('#visitor-content').evaluate('e=>e.scrollHeight<=e.clientHeight+1')
   return values
  row={'viewport':[w,h],'dpr':dpr,'physical_output':[w*dpr,h*dpr],'overview':images(),'details':[]}
  page.screenshot(path=str(out/f'overview-{w}-{dpr}x.png'))
  for product in ['sr1120','mouse','keyboard','headset']:
   page.click(f'[data-product="{product}"]');row['details'].append({'id':product,'images':images()})
   if product in ['sr1120','mouse']:page.screenshot(path=str(out/f'{product}-{w}-{dpr}x.png'))
   page.click('.spark-all-products')
  if dpr==2:
   assert all(item['images'][-1]['src'].endswith('-full.png') for item in row['details']),row
  # A monitor-density change on the same page updates pixel caps and source selection.
  if w==1920 and dpr==1:
   session=context.new_cdp_session(page);session.send('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':2,'mobile':False});page.wait_for_function('()=>document.querySelector("#visitor-content").style.getPropertyValue("--spark-pixel-ratio")==="2"');page.click('[data-product="mouse"]');row['density_switch']=images();page.click('.spark-all-products');session.detach()
  page.click('#visitor-back');page.wait_for_function('()=>!document.querySelector("#pumpkin").disabled');reports.append(row);print(f'{w}x{h} @ {dpr}x: native image detail and layout passed',flush=True);context.close()
 assert not errors,errors
 (out/'report.json').write_text(json.dumps({'layouts':reports,'no_raster_upscaling':True,'density_change':True,'errors':errors},indent=2));browser.close()
