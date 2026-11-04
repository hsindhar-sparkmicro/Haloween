import {NightWeather} from './night-weather.js';
import {SneakArrival} from './sneak-arrival.js';
const $ = q => document.querySelector(q);

// One bounded particle canvas, no competing imported-video decoder in this edition.
export class SneakAtmosphere {
  constructor() {
    this.canvas=$('#night-weather-canvas');this.ctx=this.canvas.getContext('2d');
    this.arrival=new SneakArrival();
    this.weather=new NightWeather(this.canvas,{sneakPeek:true});this.settings={};
    this.elapsed=0;this.frame=0;this.last=0;this.width=0;this.height=0;
    this.motion=matchMedia('(prefers-reduced-motion: reduce)');
    this.motion.addEventListener('change',()=>this.refresh());
    new ResizeObserver(()=>this.resize()).observe(this.canvas);
    new MutationObserver(()=>this.refresh()).observe(document.body,{subtree:true,attributes:true,attributeFilter:['class','open']});
    document.addEventListener('visibilitychange',()=>this.refresh());this.resize();
  }
  configure(settings){this.settings=settings;this.arrival.configure(settings);this.refresh();}
  resize(){const r=this.canvas.getBoundingClientRect();this.width=r.width;this.height=r.height;this.canvas.width=r.width;this.canvas.height=r.height;}
  refresh(){
    const active=$('#dashboard').classList.contains('active')&&!document.hidden&&!$('dialog[open]');
    const reduced=this.motion.matches||this.settings.reduced_motion;
    // Weather keeps its own clock and particles across every background-video handoff.
    const paused=!active||reduced;
    if($('#dashboard').classList.contains('atmosphere-paused')!==Boolean(paused))$('#dashboard').classList.toggle('atmosphere-paused',Boolean(paused));
    if(paused){cancelAnimationFrame(this.frame);this.frame=0;this.last=0;this.ctx.clearRect(0,0,this.width,this.height);this.weatherDirty=false;this.weather.describe('still');return;}
    if(this.frame)return;
    const tick=now=>{
      if(!this.last)this.last=now;
      if(now-this.last>=33){this.elapsed+=Math.min(.12,(now-this.last)/1000);this.last=now;
        this.weather.advance(this.elapsed,true,this.settings.quality==='low'||innerWidth<=1000);
        // A transparent, unchanged weather layer needs no full-screen upload.
        const visibleWeather=this.weather.mode!=='calm'&&this.weather.blend>0;
        if(visibleWeather||this.weatherDirty){this.ctx.clearRect(0,0,this.width,this.height);this.weather.draw(this.ctx,this.width,this.height,true);}
        this.weatherDirty=visibleWeather;
      }
      this.frame=requestAnimationFrame(tick);
    };this.frame=requestAnimationFrame(tick);
  }
}

const gifts={
  sr1120:{title:'SPARK SR1120',copy:'A tiny wireless chip, wrapped for a much bigger Christmas adventure.',image:'sr1120-full.png',url:'https://www.sparkmicro.com/products/sr1120/'},
  headset:{title:'A little wireless sound',copy:'The SPARK gaming headset is waiting under the wrapping. More discoveries are coming in the full Christmas house.',image:'headset-full.png',url:'https://www.sparkmicro.com/applications/gaming/#gaming-headset-audio'},
  mouse:{title:'A playful SPARK surprise',copy:'A gaming mouse with a place in the Christmas gift pile. The full reveal is still being wrapped.',image:'mouse-full.png',url:'https://www.sparkmicro.com/applications/gaming/#gaming-mouse'}
};

export class SneakPeek {
  constructor({audio,unlock}){
    this.headlineTick=performance.now();this.headlineElapsed=0;this.headlineTimer=0;this.headlineText="";
    this.audio=audio;this.unlock=unlock;this.enabled=false;this.musicOn=false;this.bellsOn=false;this.timer=0;this.voices=[];this.master=null;
    this.musicEl=$('#christmas-music');this.jingleEl=$('#sleigh-jingle');this.bellsEl=$('#christmas-bells');
    this.button=$('#peek-jingle');
    $('#peek-music').addEventListener('click',()=>this.toggleMusic());
    this.button.addEventListener('click',()=>this.toggleJingle());
    $('#peek-bells').addEventListener('click',()=>this.toggleBells());
    document.querySelectorAll('[data-gift]').forEach(button=>button.addEventListener('click',()=>{
      const gift=gifts[button.dataset.gift];$('#peek-unwrapped').hidden=false;
      $('#peek-product-image').src='/static/assets/spark/'+gift.image;$('#peek-product-image').alt=gift.title;
      $('#peek-product-title').textContent=gift.title;$('#peek-product-copy').textContent=gift.copy;$('#peek-product-link').href=gift.url;
      button.classList.add('unwrapped');button.querySelector('span:last-child').textContent='Opened';
      button.setAttribute('aria-pressed','true');$('#peek-product-title').setAttribute('tabindex','-1');$('#peek-product-title').focus({preventScroll:true});
      $('#peek-unwrapped').scrollIntoView({block:'nearest',behavior:'instant'});
    }));
    this.wasActive=true;
    new MutationObserver(()=>this.activity()).observe(document.body,{subtree:true,attributes:true,attributeFilter:['class','open']});
    document.addEventListener('visibilitychange',()=>this.activity());
    window.addEventListener('pagehide',()=>this.mute());
  }
  active(){return !document.hidden&&$('#dashboard').classList.contains('active')&&!$('dialog[open]');}
  controls(){
    this.button.setAttribute('aria-pressed',String(this.enabled));
    $('#peek-music').setAttribute('aria-pressed',String(this.musicOn));
    $('#peek-bells').setAttribute('aria-pressed',String(this.bellsOn));
  }
  level(){return (this.audio().volume??.4);}
  volumeChanged(){
    const level=this.level();
    if(this.master){const audio=this.audio();if(audio.context)this.master.gain.setTargetAtTime(level*.22,audio.context.currentTime,.03);}
    this.musicEl.volume=Math.min(1,level*.9);
    this.jingleEl.volume=Math.min(1,level*.8);
    this.bellsEl.volume=Math.min(1,level*.75);
  }
  silence(){
    clearTimeout(this.timer);this.timer=0;
    const ctx=this.audio().context;
    if(!ctx){this.voices=[];return;}
    for(const {osc,gain} of this.voices){try{gain.gain.cancelScheduledValues(ctx.currentTime);gain.gain.setTargetAtTime(0,ctx.currentTime,.015);osc.stop(ctx.currentTime+.08);}catch{}}
    this.voices=[];
  }
  stopJingles(){this.enabled=false;this.silence();this.jingleEl.pause();this.controls();}
  mute(){this.musicOn=false;this.bellsOn=false;this.musicEl.pause();this.bellsEl.pause();this.stopJingles();}
  pauseBeds(){this.musicEl.pause();this.bellsEl.pause();this.jingleEl.pause();}
  resumeBeds(){
    if(!this.audio().enabled)return;
    if(this.musicOn)this.musicEl.play().catch(()=>{});
    if(this.bellsOn)this.bellsEl.play().catch(()=>{});
  }
  toggleMusic(){
    if(this.musicOn){this.musicOn=false;this.musicEl.pause();this.controls();return;}
    this.unlock();this.musicOn=true;this.volumeChanged();this.controls();
    this.musicEl.play().catch(()=>{this.musicOn=false;this.controls();});
  }
  toggleBells(){
    if(this.bellsOn){this.bellsOn=false;this.bellsEl.pause();this.controls();return;}
    this.unlock();this.bellsOn=true;this.volumeChanged();this.bellsEl.currentTime=0;this.controls();
    this.bellsEl.play().catch(()=>{this.bellsOn=false;this.controls();});
  }
  toggleJingle(){
    if(this.enabled){this.stopJingles();return;}
    this.unlock();this.enabled=true;this.volumeChanged();this.controls();this.playJingle();
    this.jingleEl.currentTime=0;this.jingleEl.play().catch(()=>{});
  }
  activity(){const active=this.active();if(active===this.wasActive)return;this.wasActive=active;
    if(!active){this.silence();this.pauseBeds();}else{if(this.enabled)this.schedule();this.resumeBeds();}
  }
  schedule(){clearTimeout(this.timer);if(this.enabled&&this.active())this.timer=setTimeout(()=>this.playJingle(),32000+Math.random()*28000);}
  playJingle(){
    const audio=this.audio();if(!this.enabled||!audio.enabled||!this.active()||!audio.context)return;
    const ctx=audio.context;
    if(!this.master){this.master=ctx.createGain();this.master.connect(ctx.destination);}
    this.volumeChanged();this.silence();
    // Original short celesta-like motifs; no sampled artist recording or borrowed song.
    const notes=Math.random()<.5?[784,1046.5,880,1174.66,1046.5]:[659.25,880,987.77,783.99,1046.5];
    notes.forEach((frequency,i)=>{
      for(const harmonic of [1,2.76]){
        const osc=ctx.createOscillator(),gain=ctx.createGain();const start=ctx.currentTime+.035+i*.28;
        osc.type='sine';osc.frequency.value=frequency*harmonic;
        gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(harmonic===1?.24:.035,start+.012);gain.gain.exponentialRampToValueAtTime(.0001,start+1.1);
        osc.connect(gain);gain.connect(this.master);osc.start(start);osc.stop(start+1.2);
        const voice={osc,gain};this.voices.push(voice);osc.onended=()=>{osc.disconnect();gain.disconnect();this.voices=this.voices.filter(v=>v!==voice);};
      }
    });this.schedule();
  }
  rotateHeadline(christmas){
    const now=performance.now();
    const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches||document.body.classList.contains('reduced-motion');
    if(this.active()&&!reduced)this.headlineElapsed+=Math.min(1000,now-this.headlineTick);
    this.headlineTick=now;
    const headlines=[
      'Halloween fades.<br><em>Christmas stirs.</em>',
      'Santa’s on his way.<br><em>With gifts for you.</em>',
      'More festive magic.<br><em>Stay for the reveal.</em>',
      'The Christmas app.<br><em>Arrives December 1.</em>'
    ];
    const text=christmas.phase==='today'?'Christmas is here.<br><em>Let the magic in.</em>':christmas.phase==='past'?'Keep the wonder.<br><em>Christmas lingers.</em>':headlines[Math.floor(this.headlineElapsed/12000)%headlines.length];
    if(text===this.headlineText)return;
    const initial=!this.headlineText;this.headlineText=text;clearTimeout(this.headlineTimer);
    const heading=$('#peek-headline');
    const show=()=>{heading.innerHTML=text;heading.classList.remove('headline-fading');};
    if(initial||reduced)show();else{heading.classList.add('headline-fading');this.headlineTimer=setTimeout(show,350);}
  }
  update(calendar,elapsed=0){
    if(!calendar)return;
    const christmas=calendar.christmas;
    this.rotateHeadline(christmas);
    const percent=calendar.defrost_percent;
    if(this.defrostPercent!==percent){
      this.defrostPercent=percent;
      $('#peek-defrost-value').textContent=percent+'%';$('.peek-meter').setAttribute('aria-valuenow',percent);$('.peek-meter span').style.width=percent+'%';
      $('.peek-defrost h2').textContent=percent===100?'Mariah has defrosted.':'Mariah is defrosting…';
      $('#peek-defrost-caption').textContent=percent===100?'December mode: unlocked':'ready on December 1';
    }
    const party=calendar.spark_party;
    if(party){
      const seconds=Math.max(0,Math.floor(party.seconds-elapsed));
      const values=[Math.floor(seconds/86400),Math.floor(seconds/3600)%24,Math.floor(seconds/60)%60,seconds%60];
      const text=party.phase==='past'?'Thank you for celebrating!':seconds===0?'It’s time to celebrate!':values.map((n,i)=>String(n).padStart(2,'0')+['d','h','m','s'][i]).join(' · ');
      if($('#peek-party-countdown').textContent!==text)$('#peek-party-countdown').textContent=text;
    }
  }
}
