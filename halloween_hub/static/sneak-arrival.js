const KEY='spark-sneak-arrival-v1';
const ASSETS='/static/assets/sneak-peek/';

// Half speed is encoded into the file: one decoder, normal browser playback rate.
export class SneakArrival {
  constructor(){
    this.root=document.querySelector('#dashboard');
    this.layer=document.querySelector('#peek-arrival');
    this.video=this.layer.querySelector('video');
    this.status=this.layer.querySelector('[role=status]');
    this.skip=document.querySelector('#peek-arrival-skip');
    this.replay=document.querySelector('#peek-arrival-replay');
    this.restart=document.querySelector('#peek-arrival-restart');
    this.restart.addEventListener('click',()=>{
      if(this.running)this.finish(false,true);
      this.start();
    });
    this.motion=matchMedia('(prefers-reduced-motion: reduce)');
    this.settings={};this.running=false;this.generation=0;this.timers=[];
    this.skip.addEventListener('click',()=>this.finish(true));
    this.replay.addEventListener('click',()=>{
      document.querySelector('#peek-full-dialog').close();this.start();
    });
    this.motion.addEventListener('change',()=>this.check());
    document.addEventListener('visibilitychange',()=>this.check());
    window.addEventListener('pagehide',()=>this.finish(false,true));
    new MutationObserver(()=>this.check()).observe(document.body,{subtree:true,attributes:true,attributeFilter:['class','open']});
    this.video.addEventListener('error',()=>{if(this.running)this.finish(false);});
    this.video.addEventListener('ended',()=>{if(this.running)this.finish(true);});
  }
  reduced(){return this.motion.matches||this.settings.reduced_motion;}
  eligible(){return !document.hidden&&this.root.classList.contains('active')&&!document.querySelector('dialog[open]');}
  configure(settings){
    this.settings=settings;this.check();
    if(this.configured)return;this.configured=true;
    let seen=false;try{seen=localStorage.getItem(KEY)==='done';}catch{}
    if(!seen&&this.eligible()&&!this.reduced())this.start();
  }
  check(){
    for(const button of [this.replay,this.restart]){
      button.disabled=Boolean(this.reduced());
      button.title=this.reduced()?'Turn off reduced motion to watch the transition':'';
    }
    if(this.running&&(!this.eligible()||this.reduced()))this.finish(false,true);
  }
  later(callback,ms){this.timers.push(setTimeout(callback,ms));}
  clear(){this.timers.forEach(clearTimeout);this.timers=[];clearInterval(this.watchdog);}
  async start(){
    if(this.running||!this.eligible()||this.reduced())return;
    this.clear();const run=++this.generation;this.running=true;
    this.layer.hidden=false;this.layer.classList.remove('settling','presented');
    this.root.classList.add('arrival-playing');this.root.dataset.arrival='loading';
    this.status.textContent='Halloween is making way… · ½ speed · muted';
    this.skip.focus({preventScroll:true});
    this.video.muted=true;this.video.playbackRate=1;this.video.loop=false;
    // Decode the final still before any transition can expose it.
    const still=new Image();still.src=ASSETS+'forest-preparing.png';
    this.later(()=>{if(this.running)this.finish(false);},10000);
    try{
      await still.decode();if(run!==this.generation||!this.running)return;
      this.video.src=ASSETS+'arrival-half-speed.mp4';
      await this.video.play();if(run!==this.generation||!this.running)return;
      const present=()=>{
        if(run!==this.generation||!this.running)return;
        this.clear();this.layer.classList.add('presented');this.root.dataset.arrival='playing';
        let last=this.video.currentTime,changed=performance.now();
        this.watchdog=setInterval(()=>{
          if(this.video.currentTime>last){last=this.video.currentTime;changed=performance.now();}
          if(performance.now()-changed>4000)this.finish(false);
        },500);
      };
      if(this.video.requestVideoFrameCallback)this.video.requestVideoFrameCallback(present);
      else {const ready=()=>{if(run!==this.generation||!this.running)return;if(this.video.readyState>=2&&this.video.currentTime>0)present();else requestAnimationFrame(ready);};requestAnimationFrame(ready);}
    }catch{if(run===this.generation&&this.running)this.finish(false);}
  }
  finish(remember,immediate=false){
    if(!this.running)return;
    this.running=false;++this.generation;this.clear();this.video.pause();
    if(remember){try{localStorage.setItem(KEY,'done');}catch{}}
    this.root.dataset.arrival='settling';
    // Leave the last decoded frame in place until the still underneath is exposed.
    this.layer.classList.add('settling');
    const release=()=>{
      this.layer.hidden=true;this.video.removeAttribute('src');this.video.load();
      this.root.classList.remove('arrival-playing');this.root.dataset.arrival='resting';
      if(document.activeElement===this.skip)document.querySelector('#peek-gifts').focus({preventScroll:true});
    };
    if(immediate||this.reduced())release();else this.later(release,4850);
  }
}
