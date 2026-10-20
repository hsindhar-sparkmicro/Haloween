// Official SPARK imagery is bundled locally; Halloween decoration stays in CSS.
const asset=name=>`/static/assets/spark/${name}.png`;
export const products=[
 {id:'sr1120',name:'SR1120',kind:'LE-UWB TRANSCEIVER',spell:'The heart of the spell.',teaser:'Tiny silicon. Extraordinary possibilities.',image:'sr1120',alt:'SPARK SR1120 wireless transceiver chip',description:'Meet the second-generation SPARK LE-UWB transceiver: a compact foundation for responsive wireless devices, gaming and audio.',facts:[['6.2–9.5 GHz','Frequency band'],['4 × 4 mm','QFN32 package']],source:'https://www.sparkmicro.com/products/sr1120/'},
 {id:'mouse',name:'Gaming mouse',kind:'REFERENCE DESIGN',spell:'Faster than a fright.',teaser:'Make every move count.',image:'mouse',alt:'Gaming mouse application image from SPARK Microsystems',description:'A SPARK SR1120-based mouse reference design brings precise wireless input to your next gaming creation.',facts:[['8 kHz','Sustained polling'],['≤150 µs','Latency in 8 kHz mode']],source:'https://www.sparkmicro.com/applications/gaming/'},
 {id:'keyboard',name:'Gaming keyboard',kind:'REFERENCE DESIGN',spell:'Every key casts a spell.',teaser:'A little magic at your fingertips.',image:'keyboard',alt:'Gaming keyboard application image from SPARK Microsystems',description:'Explore the SR1120-based keyboard reference design, combining responsive wireless keystrokes with RGB lighting.',facts:[['8 kHz','Polling rate'],['RGB','Auxiliary channel']],source:'https://www.sparkmicro.com/reference-designs/'},
 {id:'headset',name:'Wireless headset',kind:'AUDIO DEMO',spell:'Sound from the shadows.',teaser:'Hear every whisper. Lose the wires.',image:'headset',alt:'Gaming headset application image from SPARK Microsystems',description:'Discover the SPARK headset demo for uncompressed wireless stereo audio, with a USB-C dongle and dual-receiver robustness.',facts:[['96 kHz / 24-bit','Up to · stereo audio'],['5 ms','Stereo main-channel latency']],source:'https://www.sparkmicro.com/reference-designs/'},
];
const web='<svg class="spark-web" viewBox="0 0 160 160" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width=".7"><path d="M160 0H0M160 0V160M160 0 0 160M160 0 80 160M160 0 0 80M120 0Q122 20 140 20Q140 38 160 40M80 0Q83 40 120 40Q120 77 160 80M40 0Q46 60 100 60Q100 114 160 120M0 0Q8 80 80 80Q80 152 160 160"/></g></svg>';
// Width descriptors let Chromium choose a local thumbnail or the original PNG.
function productImage(product,detail=false){
 const chip=product.id==='sr1120',width=chip?1254:1672,height=chip?1254:941;
 const sizes=detail?'(max-width: 700px) calc(100vw - 48px), 53vw':'(max-width: 700px) 48vw, 24vw';
 return `<img src="${asset(product.image)}" srcset="${asset(product.image)} ${chip?768:1024}w, ${asset(product.image+'-full')} ${width}w" sizes="${sizes}" alt="${product.alt}" width="${width}" height="${height}" style="--spark-native-width:${width}px;--spark-native-height:${height}px">`;
}
const masthead=()=>`<div class="spark-masthead"><div class="spark-logo"><img src="${asset('spark-logo')}" alt="SPARK Microsystems" width="250" height="75"></div><span class="spark-edition">HALLOWEEN <b>2026</b></span></div>`;
const footer='<div class="spark-footer"><span>LE-UWB · WIRELESS WITCHCRAFT</span><span>sparkmicro.com</span></div>';
export class SparkShowcase {
 constructor(content){
  this.content=content;
  this.updateDensity=()=>{
   this.densityQuery?.removeEventListener('change',this.updateDensity);
   const density=Math.max(1,devicePixelRatio||1);this.content.style.setProperty('--spark-pixel-ratio',String(density));
   this.densityQuery=matchMedia(`(resolution: ${devicePixelRatio||1}dppx)`);
   this.densityQuery.addEventListener('change',this.updateDensity,{once:true});
  };
  this.updateDensity();window.addEventListener('resize',this.updateDensity);
 }
 show(notice=''){
  this.content.className='spark-showcase';this.content.scrollTop=0;this.content.closest('dialog').scrollTop=0;
  this.content.innerHTML=`${web}${masthead()}<div class="spark-heading"><div><p class="spark-kicker">NO WIRES. JUST A LITTLE MAGIC.</p><h1>A little wireless <em>witchcraft.</em></h1></div><p class="spark-invitation">Four ways to conjure something extraordinary.<br>Touch a product to discover its story.</p></div>${notice?`<p class="spark-notice" role="status">${notice}</p>`:''}<div class="spark-products">${products.map((p,i)=>`<button class="spark-card spark-card-${p.id}" data-product="${p.id}" aria-label="Explore ${p.name}"><div class="spark-card-image">${productImage(p)}<span class="spark-number">0${i+1}</span><span class="spark-card-symbol" aria-hidden="true">✦</span></div><div class="spark-card-copy"><span class="spark-kind">${p.kind}</span><h2>${p.name}</h2><p>${p.teaser}</p><span class="spark-card-link">Discover the magic <b aria-hidden="true">↗</b></span></div></button>`).join('')}</div>${footer}`;
  this.content.querySelectorAll('[data-product]').forEach(button=>button.onclick=()=>this.detail(button.dataset.product));
 }
 detail(id){
  const product=products.find(p=>p.id===id);if(!product)return;
  this.content.className='spark-showcase spark-showcase-detail';this.content.scrollTop=0;this.content.closest('dialog').scrollTop=0;
  this.content.innerHTML=`${web}${masthead()}<div class="spark-detail"><div class="spark-detail-image spark-detail-${product.id}">${productImage(product,true)}<span class="spark-detail-caption">${product.id==='sr1120'?'SR1120 · SPARK LE-UWB':'SPARK · GAMING APPLICATIONS'}</span></div><div class="spark-detail-copy"><span class="spark-kicker">${product.kind}</span><h1>${product.name}</h1><h2>${product.spell}</h2><p>${product.description}</p><dl class="spark-facts">${product.facts.map(([value,label])=>`<div><dt>${label}</dt><dd>${value}</dd></div>`).join('')}</dl><button class="spark-all-products">‹ All products</button></div></div>${footer}`;
  const back=this.content.querySelector('.spark-all-products');back.onclick=()=>{this.show();this.content.querySelector(`[data-product="${id}"]`).focus({preventScroll:true});};
  this.content.querySelector('h1').tabIndex=-1;this.content.querySelector('h1').focus({preventScroll:true});
 }
}
