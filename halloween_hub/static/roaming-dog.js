const ASSETS='/static/assets/sneak-peek/';
const random=(lo,hi)=>lo+Math.random()*(hi-lo);
const clamp=(v,lo=0,hi=1)=>Math.max(lo,Math.min(hi,v));
const smooth=t=>{t=clamp(t);return t*t*(3-2*t);};

// A single small canvas; movement is tied to footfall distance, not a sliding GIF.
export class RoamingDog {
  constructor(root,arrival){
    this.root=root;this.arrival=arrival;this.scene=root.querySelector('.welcome-space');
    this.canvas=document.createElement('canvas');this.canvas.className='roaming-dog';
    this.canvas.width=this.canvas.height=256;this.canvas.setAttribute('aria-hidden','true');
    this.scene.append(this.canvas);this.ctx=this.canvas.getContext('2d');
    this.shadow=document.createElement('canvas');this.shadow.width=this.shadow.height=256;
    const shadow=this.shadow.getContext('2d');shadow.translate(128,222);shadow.scale(1,.12);
    const gradient=shadow.createRadialGradient(0,0,0,0,0,72);gradient.addColorStop(0,'rgba(8,14,25,.33)');gradient.addColorStop(1,'rgba(8,14,25,0)');
    shadow.fillStyle=gradient;shadow.fillRect(-72,-72,144,144);
    this.settings={};this.ready=false;this.visible=false;this.frame=0;this.last=0;
    this.facing=1;this.position=null;this.offstage=true;this.walkPhase=0;this.events=[];this.draws=0;
    this.mode=new URLSearchParams(location.search).get('dog')||'both';
    this.motion=matchMedia('(prefers-reduced-motion: reduce)');
    this.motion.addEventListener('change',()=>this.refresh());
    document.addEventListener('visibilitychange',()=>this.refresh());
    window.addEventListener('pagehide',()=>this.pause());
    window.addEventListener('pageshow',()=>this.refresh());
    new MutationObserver(()=>this.refresh()).observe(document.body,{subtree:true,attributes:true,attributeFilter:['class','open','data-arrival']});
    new ResizeObserver(()=>this.resize()).observe(this.scene);
    this.resize();this.setState('idle',1.2);
    if(this.mode!=='video')this.load();
  }
  async load(){
    try{
      this.atlases=await Promise.all(['roaming-dog-atlas-v1','roaming-dog-turns-v2'].map(async name=>{
        const response=await fetch(ASSETS+name+'.json');if(!response.ok)throw Error('Dog atlas unavailable');
        const data=await response.json(),image=new Image();image.src=ASSETS+data.image;await image.decode();
        if(image.naturalWidth!==data.width||image.naturalHeight!==data.height||!data.frames?.length)throw Error('Invalid dog atlas');
        return {...data,image};
      }));
      this.cachePoses();
      this.ready=true;this.canvas.dataset.asset='ready';
      this.arrival.setRoamingDogReady(true,this.mode!=='roaming');
      this.refresh();
    }catch{this.canvas.dataset.asset='unavailable';this.pause();}
  }
  cachePoses(){
    if(!this.width||!this.height)return;
    // Match the backing surface to the displayed dog, including pixel density.
    // The Pi needs 160 square pixels, not a 256-square filtered layer each frame.
    const raster=Math.min(256,Math.ceil(this.size({y:this.floor[1]})*256/194*(devicePixelRatio||1)/32)*32);
    if(raster===this.rasterSize)return;
    this.rasterSize=raster;this.canvas.width=this.canvas.height=raster;
    this.ctx.setTransform(raster/256,0,0,raster/256,0,0);
    // Scale, tint and anchor once. The animation only blends cached surfaces.
    this.poseCache=this.atlases.map((atlas,atlasIndex)=>atlas.frames.map(f=>[1,-1].map(facing=>{
      const canvas=document.createElement('canvas');canvas.width=canvas.height=raster;
      const c=canvas.getContext('2d'),scale=atlasIndex===0?226/f.w:157/(f.bounds[3]-f.bounds[1]);
      c.scale(raster/256,raster/256);c.translate(128,220);c.scale(facing,1);
      c.filter='brightness(.88) saturate(.84)';
      c.drawImage(atlas.image,f.x,f.y,f.w,f.h,-f.anchorX*scale,-f.anchorY*scale,f.w*scale,f.h*scale);
      return canvas;
    })));
  }
  configure(settings){this.settings=settings;this.refresh();}
  eligible(){
    return this.ready&&!!this.poseCache&&!this.arrival.disposed&&!document.hidden&&!this.motion.matches&&!this.settings.reduced_motion&&
      this.root.classList.contains('active')&&!document.querySelector('dialog[open]');
  }
  resting(){
    const due=[this.arrival.arrivalDue,this.arrival.dogDue].filter(t=>t>0);
    return this.root.dataset.arrival==='resting'&&!this.arrival.running&&!this.arrival.fading&&
      (!due.length||Math.min(...due)-performance.now()>4000);
  }
  pause(reset=true){
    cancelAnimationFrame(this.frame);this.frame=0;this.last=0;this.visible=false;
    if(reset){this.position=null;this.offstage=true;this.canvas.style.opacity='0';}
    this.canvas.dataset.active='false';
  }
  enter(){
    this.displayedPoses=[];this.position=null;this.place();if(!this.position)return false;
    const to={...this.position},side=this.exitSide||(Math.random()<.5?-1:1);
    const from={x:side<0?-this.size(to)*1.5:this.width+this.size(to)*1.5,y:to.y};
    this.facing=-side;this.position=from;this.offstage=false;
    const distance=Math.abs(to.x-from.x);
    this.path={from,to,distance,duration:distance/(this.size(to)*2.8),facing:this.facing};
    this.setState('enter',this.path.duration);return true;
  }
  leave(){
    const from={...this.position},side=from.x<this.width/2?-1:1;
    this.exitSide=side;
    const to={x:side<0?-this.size(from)*1.5:this.width+this.size(from)*1.5,y:from.y};
    const distance=Math.abs(to.x-from.x);
    this.path={from,to,distance,duration:Math.max(.25,distance/(this.size(from)*2.8)),facing:side};
    this.setState(this.facing===side?'exit':'exit-turn',this.facing===side?this.path.duration:.45);
  }
  refresh(){
    if(!this.eligible()){this.pause();return;}
    if(this.offstage){if(!this.resting()||!this.enter())return;}
    else if(!this.resting()&&!['exit','exit-turn'].includes(this.state))this.leave();
    if(this.frame)return;
    this.visible=true;this.canvas.dataset.active='true';this.canvas.style.opacity='1';
    const tick=now=>{
      if(!this.eligible()){this.pause();return;}
      if(!this.resting()&&!['exit','exit-turn'].includes(this.state))this.leave();
      // Present on every display refresh. A 24 fps timer on a 60 Hz panel
      // alternates long/short holds even when the browser has no dropped frames.
      const dt=this.last?Math.min(.05,(now-this.last)/1000):0;this.last=now;
      this.advance(dt);this.draw();
      // Keep the dog opaque beyond the edge rather than dissolving it away.
      if(this.offstage){this.pause(false);return;}
      this.frame=requestAnimationFrame(tick);
    };this.frame=requestAnimationFrame(tick);
  }
  resize(){
    const box=this.scene.getBoundingClientRect();this.width=box.width;this.height=box.height;this.phone=box.width<=600;
    // The real snow plane is below the gift pile. Footer text stays above the dog.
    this.floor=this.phone?[535,550]:[this.height*.89,this.height*.97];
    if(this.atlases)this.cachePoses();
    this.measure();this.position=null;this.pause();this.refresh();
  }
  measure(){
    const origin=this.scene.getBoundingClientRect();
    const selectors='.welcome-countdown,.welcome-weather,.peek-defrost,.peek-jingle'+(this.phone?'':',#pumpkin');
    this.obstacles=[...this.root.querySelectorAll(selectors)].map(e=>{
      const b=e.getBoundingClientRect();return {left:b.left-origin.left-6,right:b.right-origin.left+6,top:b.top-origin.top-6,bottom:b.bottom-origin.top+6};
    });
  }
  size(point){return clamp(this.width*.12,78,150)*(.92+.14*clamp((point.y-this.floor[0])/(this.floor[1]-this.floor[0])));}
  bounds(point){const w=this.size(point);return {left:point.x-w*.60,right:point.x+w*.60,top:point.y-w*.91,bottom:point.y+w*.08};}
  safe(point){
    const b=this.bounds(point);
    return b.left>8&&b.right<this.width-8&&b.top>=0&&b.bottom<this.height&&
      !this.obstacles.some(o=>b.left<o.right&&b.right>o.left&&b.top<o.bottom&&b.bottom>o.top);
  }
  place(){
    this.measure();
    for(const fraction of [.49,.42,.57,.34,.65,.25,.75]){
      const p={x:this.width*fraction,y:this.floor[1]-8};
      if(this.safe(p)){this.position=p;this.setState('idle',1.2);return;}
    }
    this.canvas.dataset.state='no-space';
  }
  plan(){
    this.measure();
    const from={...this.position},minDistance=this.size(from)*.55;
    for(let i=0;i<48;i++){
      const to={x:clamp(from.x+random(-1,1)*this.size(from)*1.9,20,this.width-20),y:clamp(from.y+random(-14,14),...this.floor)};
      const distance=Math.hypot(to.x-from.x,to.y-from.y);
      if(distance<minDistance||!Array.from({length:13},(_,j)=>({x:from.x+(to.x-from.x)*j/12,y:from.y+(to.y-from.y)*j/12})).every(p=>this.safe(p)))continue;
      this.path={from,to,distance,duration:distance/(26*this.size(from)/96),facing:to.x>=from.x?1:-1};
      if(this.path.facing!==this.facing)this.setState('turn',1.25);else this.setState('walk',this.path.duration);
      return;
    }
    this.setState('idle',random(1.5,3));
  }
  setState(state,duration){
    // Carry the actual blended silhouette across state boundaries, including
    // mid-stride stops and turns. Never snap to an arbitrary integer pose.
    this.blendFrom=this.displayedPoses||[];
    this.blendDuration=Math.min(.3,duration);
    this.state=state;this.age=0;this.duration=duration;this.canvas.dataset.state=state;
    this.events.push(state);if(this.events.length>64)this.events.shift();
  }
  advance(dt){
    this.age+=dt;
    if(['walk','enter','exit'].includes(this.state)){
      const t=smooth(this.age/this.duration),p=this.path;
      const next={x:p.from.x+(p.to.x-p.from.x)*t,y:p.from.y+(p.to.y-p.from.y)*t};
      const stride=this.state==='walk'?.32:.9;
      this.walkPhase=(this.walkPhase+Math.hypot(next.x-this.position.x,next.y-this.position.y)/(this.size(next)*stride)*8)%8;
      this.position=next;
    }
    if(this.age<this.duration)return;
    if(this.state==='idle')this.plan();
    else if(this.state==='exit-turn'){this.facing=this.path.facing;this.setState('exit',this.path.duration);}
    else if(this.state==='exit'){this.offstage=true;this.setState('offstage',Infinity);}
    else if(this.state==='enter')this.setState('idle',.8);
    else if(this.state==='turn'){this.facing=this.path.facing;this.setState('walk',this.path.duration);}
    else if(this.state==='walk')this.setState('settle',.35);
    else if(this.state==='settle')this.setState('lower',.75);
    else if(this.state==='lower')this.setState('sniff',random(2.3,4));
    else if(this.state==='sniff')this.setState('raise',.75);
    else this.setState('idle',random(1.5,3.5));
  }
  poses(){
    const normal=(index,facing=this.facing)=>({atlas:0,index,facing});
    let sequence,phase;
    if(['walk','enter','exit'].includes(this.state)){sequence=Array.from({length:8},(_,i)=>normal(i));phase=this.walkPhase%8;}
    else if(this.state==='settle'){return [normal(8),normal(8),0];}
    else if(this.state==='lower'||this.state==='raise'){
      sequence=(this.state==='lower'?[8,9,10]:[10,9,8]).map(i=>normal(i));phase=clamp(this.age/this.duration)*2;
    }else if(this.state==='sniff'){sequence=[normal(10),normal(11)];phase=(this.age*2.2)%2;}
    else if(this.state==='turn'||this.state==='exit-turn'){
      const middle=this.facing===1?[1,2,3]:[3,2,1];
      sequence=[normal(8),...middle.map(index=>({atlas:1,index,facing:1})),normal(8,this.path.facing)];phase=clamp(this.age/this.duration)*4;
    }else{sequence=[12,13,14,15].map(i=>normal(i));phase=(this.age*.9)%4;}
    const i=Math.floor(phase);return [sequence[i%sequence.length],sequence[(i+1)%sequence.length],phase-i];
  }
  paint(pose,opacity){
    if(opacity<.001)return;
    this.ctx.globalAlpha=opacity;
    this.ctx.drawImage(this.poseCache[pose.atlas][pose.index][pose.facing===1?0:1],0,0,256,256);
  }
  draw(){
    if(!this.position)return;
    const c=this.ctx;c.clearRect(0,0,256,256);
    const [a,b,t]=this.poses(),mix=this.blendFrom.length?smooth(this.age/this.blendDuration):1;
    const poses=[{pose:a,weight:(1-t)*mix},{pose:b,weight:t*mix}];
    if(mix<1)for(const {pose,weight} of this.blendFrom)poses.push({pose,weight:weight*(1-mix)});
    else this.blendFrom=[];
    this.displayedPoses=poses.filter(p=>p.weight>=.001);
    c.globalCompositeOperation='lighter';
    for(const {pose,weight} of this.displayedPoses)this.paint(pose,weight);
    c.globalAlpha=1;
    c.globalCompositeOperation='destination-over';c.drawImage(this.shadow,0,0);c.globalCompositeOperation='source-over';
    const size=this.size(this.position)*256/194;
    this.canvas.style.transform=`translate3d(${this.position.x-size/2}px,${this.position.y-size*220/256}px,0) scale(${size/256})`;
    this.draws++;
  }
}
