"""Observe the actual Pi kiosk page through a temporary loopback CDP connection.

Unlike the fixture/headless checks, this uses the existing native kiosk tab and
waits for its unmodified idle schedule. Reloads the page to begin a fresh run.
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cdp',default='http://127.0.0.1:19223')
parser.add_argument('--output',default='validation/idle-video/native-fix')
args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.connect_over_cdp(args.cdp)
 page=next(pg for ctx in browser.contexts for pg in ctx.pages if 'kiosk=1' in pg.url)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.reload()
 page.wait_for_selector('.idle-background-video',state='attached')
 page.evaluate('''()=>{window.nativeIdle={maxOpacity:0,minArtwork:1,events:[],samples:[],completed:false,seen:false};
  for(const name of ['pointerdown','pointermove','keydown','wheel'])document.addEventListener(name,e=>nativeIdle.events.push({name,trusted:e.isTrusted,time:performance.now()}),{passive:true});
  let last=0;const sample=()=>{const layer=document.querySelector('.idle-background-video'),video=layer.querySelector('video');
   if(video){nativeIdle.seen=true;const opacity=Number(getComputedStyle(layer).opacity),artwork=Number(getComputedStyle(document.querySelector('.pumpkin-artwork')).opacity);
    nativeIdle.maxOpacity=Math.max(nativeIdle.maxOpacity,opacity);nativeIdle.minArtwork=Math.min(nativeIdle.minArtwork,artwork);
    if(performance.now()-last>150){last=performance.now();const q=video.getVideoPlaybackQuality();nativeIdle.samples.push({state:layer.dataset.state,opacity,artwork,time:video.currentTime,duration:video.duration,id:video.dataset.cutsceneId,decoded:q.totalVideoFrames,dropped:q.droppedVideoFrames});}
   }else if(nativeIdle.seen)nativeIdle.completed=true;
   requestAnimationFrame(sample);
  };sample();}''')
 page.wait_for_function('()=>nativeIdle.maxOpacity>.95&&nativeIdle.minArtwork<.05',timeout=60000)
 page.screenshot(path=str(out/'native-playing.png'))
 page.wait_for_function('()=>nativeIdle.completed',timeout=15000)
 report=page.evaluate('()=>nativeIdle');report['errors']=errors
 frames=[s for s in report['samples'] if s['decoded']>0]
 assert len(frames)>3 and frames[-1]['decoded']>frames[0]['decoded'],report
 assert any(s['opacity']>.95 and s['time']>3 for s in frames),report
 assert page.locator('.pumpkin-artwork').evaluate('e=>Number(getComputedStyle(e).opacity)')>.95
 assert not errors,errors
 (out/'report.json').write_text(json.dumps(report,indent=2));print('Actual native kiosk: video frames advance, artwork fades, dashboard stays available, image returns.',flush=True)
