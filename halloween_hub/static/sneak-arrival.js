const ASSETS='/static/assets/sneak-peek/';
const REPEAT_MS=60000;
const DISSOLVE_MS=4800;

// One muted background decoder. Half speed is already encoded into the file.
export class SneakArrival {
  constructor(){
    this.root=document.querySelector('#dashboard');
    this.layer=document.querySelector('#peek-arrival');
    this.video=this.layer.querySelector('video');
    this.motion=matchMedia('(prefers-reduced-motion: reduce)');
    this.settings={};this.running=false;this.fading=false;this.generation=0;
    this.timers=[];this.next=0;this.configured=false;this.disposed=false;
    this.motion.addEventListener('change',()=>this.check());
    document.addEventListener('visibilitychange',()=>this.check());
    window.addEventListener('pagehide',()=>{this.disposed=true;this.check();});
    window.addEventListener('pageshow',()=>{this.disposed=false;this.check();});
    new MutationObserver(()=>this.check()).observe(document.body,{subtree:true,attributes:true,attributeFilter:['class','open']});
    this.video.addEventListener('error',()=>{if(this.running)this.finish();});
    this.video.addEventListener('ended',()=>{if(this.running)this.finish();});
  }
  eligible(){
    return !this.disposed&&!document.hidden&&!this.motion.matches&&!this.settings.reduced_motion&&
      this.root.classList.contains('active')&&!document.querySelector('dialog[open]');
  }
  configure(settings){
    this.settings=settings;
    if(this.configured){this.check();return;}
    this.configured=true;
    if(this.eligible())this.start();else this.check();
  }
  schedule(){
    clearTimeout(this.next);
    // Start-to-start cadence. Returning to the dashboard begins a fresh quiet minute.
    this.next=setTimeout(()=>{this.next=0;this.start();},REPEAT_MS);
  }
  check(){
    if(!this.configured)return;
    if(!this.eligible()){
      clearTimeout(this.next);this.next=0;
      if(this.running||this.fading)this.finish(true);
    }else if(!this.next&&!this.running&&!this.fading)this.schedule();
  }
  later(callback,ms){this.timers.push(setTimeout(callback,ms));}
  clearCycle(){this.timers.forEach(clearTimeout);this.timers=[];clearInterval(this.watchdog);}
  async start(){
    if(this.running||this.fading||!this.eligible())return;
    this.clearCycle();this.schedule();
    const run=++this.generation;this.running=true;
    this.layer.hidden=false;this.layer.classList.remove('settling','presented');
    this.root.classList.add('arrival-playing');this.root.dataset.arrival='loading';
    this.video.muted=true;this.video.playbackRate=1;this.video.loop=false;
    // Keep the stable forest visible until both the still and first video frame are ready.
    const still=new Image();still.src=ASSETS+'forest-preparing.png';
    this.later(()=>{if(this.running)this.finish();},10000);
    try{
      await still.decode();if(run!==this.generation||!this.running)return;
      this.video.src=ASSETS+'arrival-half-speed.mp4';
      await this.video.play();if(run!==this.generation||!this.running)return;
      const present=()=>{
        if(run!==this.generation||!this.running)return;
        this.clearCycle();this.layer.classList.add('presented');this.root.dataset.arrival='playing';
        let last=this.video.currentTime,changed=performance.now();
        this.watchdog=setInterval(()=>{
          if(this.video.currentTime>last){last=this.video.currentTime;changed=performance.now();}
          if(performance.now()-changed>4000)this.finish();
        },500);
      };
      if(this.video.requestVideoFrameCallback)this.video.requestVideoFrameCallback(present);
      else {const ready=()=>{if(run!==this.generation||!this.running)return;if(this.video.readyState>=2&&this.video.currentTime>0)present();else requestAnimationFrame(ready);};requestAnimationFrame(ready);}
    }catch{if(run===this.generation&&this.running)this.finish();}
  }
  finish(immediate=false){
    if(!this.running&&!this.fading)return;
    this.running=false;this.fading=true;++this.generation;this.clearCycle();this.video.pause();
    this.root.dataset.arrival='settling';
    // Keep the last decoded frame until the slow dissolve exposes the forest underneath.
    this.layer.classList.add('settling');
    const release=()=>{
      this.fading=false;this.layer.hidden=true;this.video.removeAttribute('src');this.video.load();
      this.root.classList.remove('arrival-playing');this.root.dataset.arrival='resting';
    };
    if(immediate||!this.eligible())release();else this.later(release,DISSOLVE_MS+50);
  }
}
