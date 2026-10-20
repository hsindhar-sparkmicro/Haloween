"""Real cutscene playback/completion, menu transition and cancellation/failure recovery."""
import argparse,json,re
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8093');parser.add_argument('--cdp');parser.add_argument('--output',default='validation/cutscene');args=parser.parse_args();media_route=re.compile(r'/api/cutscene(?:s/[^?]+|/webm)?(?:\?.*)?$');out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp(args.cdp) if args.cdp else p.chromium.launch();ctx=b.new_context(viewport={'width':800,'height':480});pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)));pg.add_init_script("window.cutsceneEnds=[];document.addEventListener('ended',event=>{const v=event.target;if(v.id==='visitor-cutscene-video'){const q=v.getVideoPlaybackQuality?.();window.cutsceneEnds.push({time:v.currentTime,duration:v.duration,frames:q?.totalVideoFrames,dropped:q?.droppedVideoFrames,src:v.currentSrc})}},true)");pg.goto(args.url);pg.bring_to_front();pg.wait_for_function('()=>document.querySelector("#connection").textContent.includes("Connected")')
 def enter():
  pg.wait_for_function('()=>!document.querySelector("#pumpkin").disabled');pg.click('#pumpkin');pg.wait_for_selector('#visitor-cutscene-video');pg.wait_for_function('()=>document.querySelector("#visitor-cutscene-video")?.currentTime>.1&&document.querySelector("#visitor-cutscene-video")?.videoWidth>0')
 def leave():
  pg.click('#visitor-back');pg.wait_for_function('()=>!document.querySelector("#pumpkin").disabled')
 reports=[]
 for w,h in [(800,480),(1280,720),(1920,1080)]:
  pg.set_viewport_size({'width':w,'height':h});enter();assert pg.locator('.reveal-pumpkin').count()==0;assert pg.locator('#visitor-dialog button:visible').count()==1
  info=pg.locator('#visitor-cutscene-video').evaluate('(v)=>({width:v.videoWidth,height:v.videoHeight,duration:v.duration,time:v.currentTime,muted:v.muted,volume:v.volume,rect:{width:v.clientWidth,height:v.clientHeight}})');assert info['width']>0 and info['duration']>1;pg.screenshot(path=str(out/f'video-{w}.png'))
  pg.wait_for_selector('[data-product="sr1120"]',timeout=25000);assert not pg.locator('.spark-notice').count();ended=pg.evaluate('cutsceneEnds.at(-1)');assert ended and ended['time']>=ended['duration']-.1;assert not pg.locator('#visitor-cutscene-video').count();pg.screenshot(path=str(out/f'menu-{w}.png'));reports.append({'viewport':[w,h],'video':info,'real_full_completion':True,'completion':ended});leave()
 # Back while playing releases the media resource and never opens a late menu.
 enter();pg.evaluate('()=>window.oldCutscene=document.querySelector("#visitor-cutscene-video")');leave();assert pg.evaluate('oldCutscene.paused&&!oldCutscene.getAttribute("src")');pg.wait_for_timeout(600);assert not pg.locator('#visitor-dialog').evaluate('(d)=>d.open')
 # A bad/unavailable source must lead to the menu rather than a stuck player.
 pg.route(media_route,lambda route:route.fulfill(status=404,body='Cutscene unavailable'));pg.click('#pumpkin');pg.wait_for_selector('[data-product="mouse"]',timeout=12000);assert pg.locator('.spark-notice').count()==1;leave();pg.unroute(media_route)
 # Browser audio restrictions must still allow the visual intro, muted across polls.
 pg.evaluate("()=>{window.realMediaPlay=HTMLMediaElement.prototype.play;window.blockNextIntro=true;HTMLMediaElement.prototype.play=function(){if(this.tagName==='VIDEO'&&window.blockNextIntro){window.blockNextIntro=false;return Promise.reject(new DOMException('Gesture required','NotAllowedError'));}return window.realMediaPlay.call(this)}}")
 enter();pg.wait_for_timeout(1300);assert pg.locator('#visitor-cutscene-video').evaluate('(v)=>v.muted');leave();pg.evaluate('()=>HTMLMediaElement.prototype.play=window.realMediaPlay')
 # Reduced motion skips the video and spinning reveal.
 pg.evaluate("()=>fetch('/api/settings',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({reduced_motion:true})})");pg.wait_for_timeout(1300);pg.click('#pumpkin');pg.wait_for_selector('[data-product="sr1120"]');assert not pg.locator('#visitor-cutscene-video,.reveal-pumpkin').count();leave();pg.evaluate("()=>fetch('/api/settings',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({reduced_motion:false})})");assert not errors,errors
 (out/'report.json').write_text(json.dumps({'layouts':reports,'back_releases_video':True,'failed_video_menu_fallback':True,'reduced_motion':True,'autoplay_restriction_muted_fallback':True,'errors':errors},indent=2));print(json.dumps({'completed_resolutions':len(reports),'back':True,'failure_recovery':True,'errors':errors}));ctx.close()
 if not args.cdp:b.close()
