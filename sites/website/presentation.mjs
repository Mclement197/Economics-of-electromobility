import {mountFinance} from './finance-ui.mjs';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const params=new URLSearchParams(location.search);
const printMode=params.has('print');
function transcript(s){return s.text.map(t=>`<p>${esc(t)}</p>`).join('')+(s.charts||[]).map(c=>`<div class="deck-chart-table"><table><caption>${esc(c.title||'Diagrammdaten der Originalfolie')}</caption><thead><tr><th></th>${c.categories.map(x=>`<th>${esc(x)}</th>`).join('')}</tr></thead><tbody>${c.series.map(x=>`<tr><th>${esc(x.name)}</th>${x.values.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`).join('');}
function slideHTML(s,i){return `<article class="deck-slide" data-slide="${i}" aria-label="Folie ${s.number}: ${esc(s.title)}"><img class="deck-artwork" src="${esc(s.image)}" width="1600" height="900" alt="${esc(s.title)} – vollständiger Folieninhalt im Lesemodus" ${i?'loading="lazy"':''}></article>`;}
function mountDeck(root,data){
 const slides=data.slides;
 let index=0,expanded=false,previousFocus=null,finance=null,live=false,chromeTimer=null;
 root.classList.add('deck');root.setAttribute('aria-label','VoltoShare-Präsentation');
 if(printMode){root.innerHTML=slides.map((s,i)=>`<div class="deck-stage">${slideHTML(s,i)}</div>`).join('');root.querySelectorAll('img').forEach(x=>x.loading='eager');document.body.classList.add('deck-print');return;}
 function overviewButton(s){return `<button type="button" data-slide-jump="${s.number-1}"><span>${String(s.number).padStart(2,'0')}</span>${esc(s.title)}${s.hidden?'<small>Original: ausgeblendet</small>':''}</button>`;}
 root.innerHTML=`<div class="deck-toolbar"><div class="deck-label">TEAM VOLTOSHARE <span class="deck-count" aria-live="polite"></span></div><div class="deck-tools"><button type="button" data-action="finance" aria-expanded="false"><span class="deck-live-dot" aria-hidden="true"></span>Live-Szenario</button><button type="button" data-action="overview" aria-expanded="false">Folienübersicht</button><button type="button" data-action="fullscreen">Vollbild ↗</button></div></div>
 <div class="deck-overview" hidden><p>17 Originalfolien · mit einem zusätzlichen Live-Szenario nach Folie 14</p><button type="button" class="deck-live-jump" data-action="finance-jump">LIVE · Annahmen verändern & Wirkung zeigen →</button><h3>VoltoShare · 01–17</h3><div class="deck-overview-group">${slides.map(overviewButton).join('')}</div></div>
 <div class="deck-stage" tabindex="0" aria-label="Präsentation. Mit Pfeiltasten blättern."></div>
 <section class="deck-lab" aria-label="Live-Szenario: Annahmen und Wirkung" hidden><div class="deck-lab-heading"><div><p>LIVE-SZENARIO · ERGÄNZUNG ZUR ORIGINALFOLIE</p><h2>Wirtschaftlichkeit pro Gebäude</h2></div><button type="button" data-action="finance-close">Zur Originalfolie</button></div><div class="deck-live-finance"></div></section>
 <div class="deck-controls"><button type="button" data-action="prev" aria-label="Vorherige Folie">←</button><div class="deck-current-title"></div><button type="button" data-action="next" aria-label="Nächste Folie">→</button></div>
 <div class="deck-finance-cue" hidden><div><strong>Jetzt die Annahmen hinterfragen.</strong><span>Zum Beispiel: Wie wirkt ein anderes Abo auf den Cashflow?</span></div><button type="button" data-action="finance-open">Live ausprobieren →</button></div>
 <div class="deck-utility"><button type="button" data-action="read" aria-expanded="false">Lesemodus</button><span>← → blättern · F: Live-Szenario · Esc: zurück · Vollbild: Maus zum Rand für Steuerung</span></div><div class="deck-reading" hidden></div><details class="deck-notes"><summary>Originalnotizen</summary><div></div></details><div class="deck-downloads"><a href="/downloads/VoltoShare-Praesentation.pdf?v=${esc(data.revision)}" download>PDF herunterladen ↓</a><a href="/downloads/VoltoShare-Praesentation.pptx?v=${esc(data.revision)}" download>Editierbares PowerPoint ↓</a><p>17 Originalfolien mit unveränderten Inhalten. Das zusätzliche Live-Szenario funktioniert im Browser, auch im Vollbild. PDF und PowerPoint bleiben unveränderte Momentaufnahmen.</p></div>`;
 const stage=root.querySelector('.deck-stage'),overview=root.querySelector('.deck-overview'),lab=root.querySelector('.deck-lab'),reading=root.querySelector('.deck-reading');
 function hideOverview(){overview.hidden=true;root.querySelector('[data-action="overview"]').setAttribute('aria-expanded','false');}
 function updateChrome(){
  root.classList.toggle('deck-live-active',live);stage.hidden=live;lab.hidden=!live;
  root.querySelector('.deck-count').textContent=live?`LIVE · nach ${String(index+1).padStart(2,'0')}`:`${String(index+1).padStart(2,'0')} / ${slides.length}`;
  root.querySelector('.deck-current-title').textContent=live?'Live-Szenario · Annahmen & Wirkung':slides[index].title;
  root.querySelector('[data-action="prev"]').disabled=!live&&index===0;
  root.querySelector('[data-action="next"]').disabled=index===slides.length-1;
  root.querySelector('[data-action="next"]').setAttribute('aria-label',!live&&index===13?'Weiter zum Live-Szenario':'Nächste Folie');
  root.querySelectorAll('[data-action="finance"]').forEach(b=>b.setAttribute('aria-expanded',String(live)));
  root.querySelector('.deck-finance-cue').hidden=live||index<11||index>14;
 }
 function render(){
  const s=slides[index];stage.innerHTML=slideHTML(s,index);updateChrome();
  root.querySelectorAll('[data-slide-jump]').forEach(b=>b.setAttribute('aria-current',String(+b.dataset.slideJump===index&&!live)));
  reading.innerHTML=`<h3>${esc(s.title)}</h3>${transcript(s)}`;
  root.querySelector('.deck-notes>div').innerHTML=s.notes?`<p>${esc(s.notes)}</p>`:'<p>Keine Originalnotizen zu dieser Folie.</p>';
  if(slides[index+1]){const next=new Image();next.src=slides[index+1].image;}
 }
 function openLive(){
  hideOverview();reading.hidden=true;root.querySelector('[data-action="read"]').setAttribute('aria-expanded','false');
  live=true;updateChrome();
  if(!finance)finance=mountFinance(root.querySelector('.deck-live-finance'),{compact:true,preset:params.get('live')==='1'&&params.get('preset')==='cham'?'cham':'zurich'});
  root.querySelector('[data-action="finance-close"]').focus({preventScroll:true});
  if(!expanded)root.scrollIntoView({block:'start',behavior:'instant'});
 }
 function closeLive(focus=true){live=false;updateChrome();if(focus)stage.focus({preventScroll:true});}
 function go(n){closeLive(false);index=Math.max(0,Math.min(slides.length-1,n));render();}
 function next(){if(!live&&index===13)openLive();else go(index+1);}
 function prev(){if(live)closeLive();else if(index===14){go(13);openLive();}else go(index-1);}
 // Controls float over the canvas; they never reserve slide space.
 function revealChrome(){
  if(!expanded)return;
  root.classList.add('deck-chrome-visible');clearTimeout(chromeTimer);
  chromeTimer=setTimeout(hideChrome,2200);
 }
 function hideChrome(){
  if(root.querySelector('.deck-toolbar:focus-within,.deck-controls:focus-within,.deck-toolbar:hover,.deck-controls:hover'))return;
  root.classList.remove('deck-chrome-visible');
 }
 root.addEventListener('pointermove',e=>{
  if(!expanded)return;
  const rect=root.getBoundingClientRect();
  if((!live&&e.clientY-rect.top<72)||rect.bottom-e.clientY<(live?16:72))revealChrome();
  else if(root.classList.contains('deck-chrome-visible')){clearTimeout(chromeTimer);chromeTimer=setTimeout(hideChrome,2200);}
 });
 root.addEventListener('pointerdown',e=>{if(expanded&&e.pointerType==='touch'&&e.target.closest('.deck-stage'))revealChrome();});
 root.addEventListener('focusin',e=>{if(e.target.closest('.deck-toolbar,.deck-controls'))revealChrome();});
 root.addEventListener('focusout',()=>{if(expanded){clearTimeout(chromeTimer);chromeTimer=setTimeout(hideChrome,2200);}});
 function exit(){clearTimeout(chromeTimer);root.classList.remove('deck-expanded','deck-chrome-visible');document.body.classList.remove('deck-is-presenting');expanded=false;root.querySelector('[data-action="fullscreen"]').textContent='Vollbild ↗';previousFocus?.focus();}
 async function fullscreen(){
  if(expanded){if(document.fullscreenElement===root)await document.exitFullscreen();exit();return;}
  previousFocus=document.activeElement;expanded=true;root.classList.add('deck-expanded');document.body.classList.add('deck-is-presenting');root.querySelector('[data-action="fullscreen"]').textContent='Vollbild beenden';
  try{await root.requestFullscreen?.();}catch{}
  (live?root.querySelector('[data-action="finance-close"]'):stage).focus({preventScroll:true});
  revealChrome();
 }
 root.addEventListener('click',e=>{
  const jump=e.target.closest('[data-slide-jump]');if(jump){go(+jump.dataset.slideJump);hideOverview();stage.focus();return;}
  const action=e.target.closest('[data-action]')?.dataset.action;
  if(action==='next'||action==='prev'){action==='next'?next():prev();if(!live)stage.focus({preventScroll:true});revealChrome();}
  if(action==='fullscreen')fullscreen();
  if(action==='overview'){overview.hidden=!overview.hidden;root.querySelector('[data-action="overview"]').setAttribute('aria-expanded',String(!overview.hidden));}
  if(action==='read'){reading.hidden=!reading.hidden;root.querySelector('[data-action="read"]').setAttribute('aria-expanded',String(!reading.hidden));}
  if(action==='finance')live?closeLive():openLive();
  if(action==='finance-open')openLive();
  if(action==='finance-jump'){go(13);openLive();}
  if(action==='finance-close')closeLive();
 });
 root.addEventListener('keydown',e=>{
  if(e.defaultPrevented)return;
  if(e.key==='Tab'&&expanded)revealChrome();
  if(e.key==='Escape'){
   if(!overview.hidden){hideOverview();root.querySelector('[data-action="overview"]').focus();return;}
   if(live){e.preventDefault();closeLive();return;}
   if(expanded){if(document.fullscreenElement===root)document.exitFullscreen();exit();}return;
  }
  const editing=e.target.closest('input,select,textarea,summary,[contenteditable="true"]');
  if(!editing&&overview.hidden){
   if(e.key==='ArrowRight'||e.key==='PageDown'){e.preventDefault();next();}
   if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();prev();}
   if(e.key==='Home'){e.preventDefault();go(0);}
   if(e.key==='End'){e.preventDefault();go(slides.length-1);}
   if(e.key.toLowerCase()==='f'&&!e.ctrlKey&&!e.metaKey&&!e.altKey){e.preventDefault();live?closeLive():openLive();}
  }
  if(e.key==='Tab'&&expanded){
   const all=[...root.querySelectorAll('a,button:not(:disabled),input,select,summary,[tabindex="0"]')].filter(x=>!x.matches(':disabled')&&x.getClientRects().length&&![...root.querySelectorAll('details:not([open])')].some(d=>d.contains(x)&&x!==d.querySelector(':scope > summary')));
   if(e.shiftKey&&document.activeElement===all[0]){e.preventDefault();all.at(-1)?.focus();}
   else if(!e.shiftKey&&document.activeElement===all.at(-1)){e.preventDefault();all[0]?.focus();}
  }
 });
 document.addEventListener('fullscreenchange',()=>{if(!document.fullscreenElement&&expanded)exit();});render();
 if(params.get('live')==='1'){go(13);openLive();}
}
try{const res=await fetch('/presentation-data.json');if(!res.ok)throw Error('Präsentation nicht verfügbar');const data=await res.json();document.querySelectorAll('[data-presentation]').forEach(root=>mountDeck(root,data));await document.fonts.ready;window.voltoPresentationReady=true;}catch(e){document.querySelectorAll('[data-presentation]').forEach(root=>root.innerHTML='<p>Bitte laden Sie die Seite erneut oder nutzen Sie die PDF- und PowerPoint-Downloads.</p>');console.error(e);}
