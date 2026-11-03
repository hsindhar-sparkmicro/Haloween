const ASSETS='/static/assets/sneak-peek/';
const REPEAT_MS=60000;
const DISSOLVE_MS=4800;
const DOG_DISSOLVE_MS=2400;
const DOG_STILL_MS=5000;
const DOG_WINDOW_MS=18000;

// One muted decoder shared by both films. Their intended speeds are encoded.
export class SneakArrival {
  constructor(){
    this.root=document.querySelector('#dashboard');
    this.layer=document.querySelector('#peek-arrival');
    this.returnLayer=document.querySelector('#peek-halloween-return');
    this.video=this.layer.querySelector('video');
    this.motion=matchMedia('(prefers-reduced-motion: reduce)');
    this.settings={};this.running=false;this.fading=false;this.returning=false;this.generation=0;
    this.timers=[];this.next=0;this.configured=false;this.disposed=false;
    this.kind='arrival';this.dogTimer=0;this.arrivalDue=0;
    this.motion.addEventListener('change',()=>this.check());
    document.addEventListener('visibilitychange',()=>this.check());
    window.addEventListener('pagehide',()=>{this.disposed=true;this.check();});
    window.addEventListener('pageshow',()=>{this.disposed=false;this.check();});
    new MutationObserver(()=>this.check()).observe(document.body,{subtree:true,attributes:true,attributeFilter:['class','open']});
    this.video.addEventListener('error',()=>{if(this.running&&!this.returning)this.finish();});
    this.video.addEventListener('ended',()=>{if(this.running&&!this.returning)this.finish();});
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
    this.arrivalDue=performance.now()+REPEAT_MS;
  }
  clearDog(){clearTimeout(this.dogTimer);this.dogTimer=0;}
  setRoamingDogReady(ready){
    this.roamingDogReady=ready;
    if(ready)this.clearDog();else this.scheduleDog();
  }
  scheduleDog(){
    if(this.roamingDogReady)return;
    if(this.dogTimer||!this.next||!this.eligible()||this.running||this.fading||this.root.dataset.arrival!=='resting')return;
    // Leave a quiet still between clips and enough room before the fixed arrival slot.
    if(this.arrivalDue-performance.now()<DOG_STILL_MS+DOG_WINDOW_MS)return;
    this.dogTimer=setTimeout(()=>{this.dogTimer=0;this.start(false,'dog');},DOG_STILL_MS);
  }
  phase(name){
    this.root.dataset.arrival=this.kind==='dog'&&name!=='resting'?'dog-'+name:name;
  }
  check(){
    if(!this.configured)return;
    if(!this.eligible()){
      clearTimeout(this.next);this.next=0;
      this.clearDog();
      if(this.running||this.fading)this.finish(true);
    }else if(!this.running&&!this.fading){
      if(!this.next)this.schedule();
      this.scheduleDog();
    }
  }
  later(callback,ms){this.timers.push(setTimeout(callback,ms));}
  clearCycle(){this.timers.forEach(clearTimeout);this.timers=[];clearInterval(this.watchdog);}
  async returnToHalloween(){
    if(this.returning||!this.eligible())return;
    clearTimeout(this.next);this.next=0;this.clearDog();this.clearCycle();
    this.kind='arrival';this.root.dataset.backgroundClip='arrival';
    const run=++this.generation;this.running=true;this.fading=false;this.returning=true;
    // Preserve the current picture, even if clicked midway through a dissolve.
    const opacity=getComputedStyle(this.layer).opacity;
    this.layer.style.transition='none';this.layer.style.opacity=opacity;this.video.pause();
    this.root.classList.add('arrival-playing');this.root.dataset.arrival='return-loading';
    const poster=new Image();poster.src=ASSETS+'arrival-start.png';
    this.later(()=>{if(this.returning)this.finish();},10000);
    try{
      await poster.decode();if(run!==this.generation||!this.returning)return;
      this.clearCycle();this.returnLayer.hidden=false;
      this.returnLayer.classList.remove('visible');
      this.returnLayer.getBoundingClientRect(); // Establish the transparent starting frame.
      this.returnLayer.classList.add('visible');this.root.dataset.arrival='returning';
      this.later(()=>{this.running=false;this.returning=false;this.start(true);},DISSOLVE_MS+50);
    }catch{if(run===this.generation)this.finish();}
  }
  async start(fromHalloween=false,kind='arrival'){
    // A late/stalled dog clip must never postpone the main transition.
    if(kind==='arrival'&&this.kind==='dog'&&(this.running||this.fading))this.finish(true);
    if(this.running||this.fading||!this.eligible())return;
    if(kind==='dog'&&(this.roamingDogReady||!this.next||this.root.dataset.arrival!=='resting'||this.arrivalDue-performance.now()<DOG_WINDOW_MS))return;
    this.clearDog();this.clearCycle();
    this.kind=kind;this.root.dataset.backgroundClip=kind;
    if(kind==='arrival')this.schedule();
    const run=++this.generation;this.running=true;
    this.layer.style.removeProperty('opacity');
    this.layer.style.transition=fromHalloween?'none':'';
    this.layer.hidden=false;this.layer.classList.remove('settling','presented');
    this.root.classList.add('arrival-playing');this.phase('loading');
    this.video.muted=true;this.video.playbackRate=1;this.video.loop=false;
    // Keep the stable forest visible until both the still and first video frame are ready.
    const still=new Image();still.src=ASSETS+'forest-preparing.png';
    this.later(()=>{if(this.running)this.finish();},10000);
    try{
      await still.decode();if(run!==this.generation||!this.running)return;
      this.video.src=ASSETS+(kind==='dog'?'dog-eight-tenths-speed.mp4':'arrival-half-speed.mp4');
      await this.video.play();if(run!==this.generation||!this.running)return;
      const present=()=>{
        if(run!==this.generation||!this.running)return;
        // Commit the transparent starting style even when cached media is ready immediately.
        this.layer.getBoundingClientRect();
        this.clearCycle();this.layer.classList.add('presented');this.phase('playing');
        if(kind==='dog')this.later(()=>this.finish(),Math.max(0,this.arrivalDue-performance.now()-DOG_DISSOLVE_MS-150));
        if(fromHalloween){
          // The poster and the first film frame match, so this handoff needs no cut to black.
          this.layer.getBoundingClientRect();this.returnLayer.hidden=true;
          this.returnLayer.classList.remove('visible');this.layer.style.removeProperty('transition');
        }
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
    this.running=false;this.fading=true;this.returning=false;++this.generation;this.clearCycle();this.video.pause();
    this.phase('settling');
    // Keep the last decoded frame until the slow dissolve exposes the forest underneath.
    this.layer.style.removeProperty('opacity');this.layer.style.removeProperty('transition');
    this.layer.classList.add('settling');this.returnLayer.classList.remove('visible');
    const release=()=>{
      this.fading=false;this.layer.hidden=true;this.video.removeAttribute('src');this.video.load();
      this.returnLayer.hidden=true;
      this.root.classList.remove('arrival-playing');this.root.dataset.arrival='resting';
      if(!immediate)this.scheduleDog();
    };
    if(immediate||!this.eligible())release();else this.later(release,(this.kind==='dog'?DOG_DISSOLVE_MS:DISSOLVE_MS)+50);
  }
}
