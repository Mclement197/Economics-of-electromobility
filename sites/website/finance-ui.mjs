import {PRESETS,PRESET_LABELS,FINANCE_FIELDS,normalizeState,calculateFinance,sensitivity} from './finance-model.mjs';
export const FINANCE_STORAGE_KEY='voltoshare-finance-v1';
const money=new Intl.NumberFormat('de-CH',{maximumFractionDigits:0});
const decimal=new Intl.NumberFormat('de-CH',{maximumFractionDigits:1});
const axisNumber=new Intl.NumberFormat('de-CH',{notation:'compact',maximumFractionDigits:1});
const number=v=>money.format(v);
const chf=v=>`CHF ${number(v)}`;
const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let seq=0;
const mounted=new WeakMap();
export function readFinanceState(preset='zurich') {
  try {const saved=JSON.parse(localStorage.getItem(FINANCE_STORAGE_KEY)||'null');return normalizeState({preset,values:saved?.presets?.[preset]});}catch{return normalizeState({preset});}
}
function saveFinanceState(state) {
  try {let saved;try{saved=JSON.parse(localStorage.getItem(FINANCE_STORAGE_KEY)||'null');}catch{} const presets={...(saved?.presets||{}),[state.preset]:state.values};localStorage.setItem(FINANCE_STORAGE_KEY,JSON.stringify({version:1,presets}));}catch{}
}
function chart(result,id,compact=false,narrow=false) {
  const series=result.cashflow,W=narrow?480:720,H=narrow?270:compact?170:300,left=narrow?83:77,right=24,top=26,bottom=38;
  const baseline=calculateFinance({preset:result.preset});
  const reference=series.map(p=>({year:p.year,value:-baseline.investment+baseline.annualCash*p.year}));
  const raw=[...series,...reference].map(p=>p.value),lo=Math.min(0,...raw),hi=Math.max(0,...raw),span=hi-lo||1;
  // Rounded comparison axes prevent a straight line from looking unchanged when
  // its new endpoints would otherwise be stretched back to the same two corners.
  const rough=span/4,power=10**Math.floor(Math.log10(rough)),scaled=rough/power;
  const step=(scaled<=1?1:scaled<=2?2:scaled<=5?5:10)*power;
  const low=Math.floor(lo/step)*step,high=Math.ceil(hi/step)*step||step;
  const x=n=>left+n/result.horizon*(W-left-right),y=v=>top+(high-v)/(high-low)*(H-top-bottom);
  const points=series.map(p=>`${x(p.year)},${y(p.value)}`).join(' ');
  const baselinePoints=reference.map(p=>`${x(p.year)},${y(p.value)}`).join(' ');
  const ticks=Array.from({length:Math.round((high-low)/step)+1},(_,i)=>low+i*step),end=series.at(-1),baselineEnd=reference.at(-1);
  return `<svg class="finance-chart" viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="${id}-chart-title ${id}-chart-desc"><title id="${id}-chart-title">Kumulierter Cashflow in CHF, aktuell und Basiswerte</title><desc id="${id}-chart-desc">Aktuell: Jahr 0 ${chf(-result.investment)}, Jahr ${result.horizon} ${chf(end.value)}. Gestrichelte Basiswerte: Jahr 0 ${chf(-baseline.investment)}, Jahr ${result.horizon} ${chf(baselineEnd.value)}. Konstante Annahmen über denselben Zeitraum; genaue Jahreswerte in der Datentabelle.</desc>${ticks.map(v=>`<line x1="${left}" y1="${y(v)}" x2="${W-right}" y2="${y(v)}" class="finance-grid-line"/><text x="${left-10}" y="${y(v)+4}" text-anchor="end">${axisNumber.format(v)}</text>`).join('')}<line x1="${left}" y1="${y(0)}" x2="${W-right}" y2="${y(0)}" class="finance-zero"/><polyline fill="none" points="${baselinePoints}" class="finance-baseline"/><polyline fill="none" points="${points}" class="finance-line"/>${series.filter((p,i)=>i===0||i===series.length-1||i%Math.max(1,Math.ceil(result.horizon/5))===0).map(p=>`<circle cx="${x(p.year)}" cy="${y(p.value)}" r="4" class="finance-dot"/><text x="${x(p.year)}" y="${H-12}" text-anchor="middle">${p.year}</text>`).join('')}<text x="${left}" y="13">CHF</text><text x="${W-right}" y="${H-12}" text-anchor="end" class="finance-axis-label">Jahre</text></svg><div class="finance-chart-legend"><span><i class="finance-legend-current" aria-hidden="true"></i>Aktuell</span><span><i class="finance-legend-baseline" aria-hidden="true"></i>Basiswerte (gleicher Zeitraum)</span></div>`;
}
function kpis(m,compact) {
  const base=calculateFinance({preset:m.preset});
  const delta=m.annualCash-base.annualCash;
  const values=[['Investition',chf(m.investment),'Einmalig, Jahr 0'],['Cash-Überschuss / Jahr',chf(m.annualCash),delta===0?'Entspricht den Basiswerten':`${delta>0?'+':'−'} CHF ${number(Math.abs(delta))} gegenüber Basis`],['Amortisation',m.payback===null?'Nicht erreicht':`${decimal.format(m.payback)} Jahre`,m.payback!==null&&m.payback>m.horizon?'Ausserhalb des Zeithorizonts':'Einfach, nicht abgezinst']];
  return `<div class="finance-kpis">${values.map(([label,value,note],i)=>`<div class="finance-kpi ${i===1?'finance-kpi--primary':''}"><span>${label}</span><strong>${value}</strong><small>${note}</small></div>`).join('')}</div>`;
}
function resultRows(m) {
  const p=m.state.values;
  if(m.preset==='zurich')return [['Abo pro Jahr',m.subscription],['Strommarge pro Jahr',m.energyMargin],['Plattform & Software',-p.platform],['Wartung & Support',-m.maintenance],['Messung, Zahlung, Versicherung',-p.other],['Betrieblicher Cash-Überschuss',m.annualCash],['Mehrmiete, nach Leerstand',m.rent],['Vermieter: Mehrmiete abzüglich Abo',m.landlordNet]];
  return [['Entschädigung Vermieterin',m.subscription],['Stromverkauf',m.energyRevenue],['Umsatz',m.revenue],['Stromeinkauf inkl. Verluste',-m.energyCost],['Zahlungsgebühren',-m.payment],['App, Backend & Daten',-m.backend],['Wartung & Versicherung',-m.service],['Overhead',-m.overhead],['Betrieblicher Cash-Überschuss',m.annualCash],['Akquisekosten, jährlicher Rechenanteil',-m.acquisitionAnnual],['EBITDA im gelieferten Rechenmodell',m.ebitda],['Abschreibung',-m.depreciation],['Ergebnis (EBIT)',m.ebit]];
}
function sources(preset) {
  return preset==='zurich'?`Quelle: bereitgestellte VoltoShare-Präsentation, Folien 12–15. Preise, Nutzung und Kosten sind Teamannahmen. 0,1 % Leerstand ist die im Deck genannte Zürcher Statistik; EV-Zahl und Strombedarf werden separat gesetzt.`:`Quelle: bereitgestellter «VoltoShare Profitrechner», Cham/Papieri. Tarif- und Konkurrenzwerte sind übernommene Annahmen, keine aktuelle Offerte: <a href="https://www.wwz.ch/-/media/privatpersonen/energie/strom/tarife/2027/mitteilung-zu-tarifnderung-im-jahr-2027.pdf" target="_blank" rel="noopener">WWZ-Tarif 2027</a> · <a href="https://www.wwz.ch/-/media/privatpersonen/e-mobilitaet/ladeloesung-mehrfamilienhaus/infoblatt-und-preisliste.pdf" target="_blank" rel="noopener">WWZ-Ladelösung</a>. Alle Beträge exkl. MwSt.`;
}
function detailsHtml(m,id) {
  const p=m.state.values,baseline=calculateFinance({preset:m.preset});
  const cashTable=`<div class="finance-table-wrap" tabindex="0" role="region" aria-label="Cashflow-Daten"><table><caption>Kumulierter Cashflow · CHF</caption><thead><tr><th scope="col">Jahr</th><th scope="col">Aktuell</th><th scope="col">Basiswerte</th></tr></thead><tbody>${m.cashflow.map(r=>`<tr><th scope="row">${r.year}</th><td>${chf(r.value)}</td><td>${chf(-baseline.investment+baseline.annualCash*r.year)}</td></tr>`).join('')}</tbody></table></div>`;
  const comparison=m.preset==='cham'&&m.tenant?`<section class="finance-secondary"><h4>Monatskosten je ladender Mietpartei</h4><p>${decimal.format(m.tenant.monthlyKwh)} kWh/Monat · Entschädigung wird hier auf Ladende umgelegt.</p><div class="finance-comparison">${[['VoltoShare, geteilte Box',m.tenant.volto],['WWZ, eigene Mietbox',m.tenant.wwz],['Öffentliches AC-Laden',m.tenant.public]].map(([label,value])=>`<div><span>${label}</span><strong>${chf(value)}</strong></div>`).join('')}</div><p class="finance-note">WWZ inkl. 8,1 % MwSt. auf exkl. umgerechnet; Grundinstallation der Eigentümerschaft ist im WWZ-Monatsvergleich nicht enthalten. Unterschiedliche Leistungen, keine garantierte Ersparnis.</p></section>`:'';
  const slot=m.preset==='cham'?`<section class="finance-secondary"><h4>Kapazität & Ladeslots</h4><p>${number(m.evs)} E-Auto-Haushalte · ${number(m.chargers)} Wallboxen · Ø ${decimal.format(m.avgUsers)} Parteien/Box</p><div class="finance-comparison"><div><span>Slots je volle Box / Woche</span><strong>${m.slots.booked} / ${m.slots.available}</strong></div><div><span>Ladezeit je Slot</span><strong>${m.slots.hoursNeeded===null?'Nicht berechenbar':`${decimal.format(m.slots.hoursNeeded)} h`}</strong></div><div><span>Energie je Slot</span><strong>${m.slots.kwhPerSlot===null?'Nicht berechenbar':`${decimal.format(m.slots.kwhPerSlot)} kWh`}</strong></div></div><p class="finance-note">Auslegung für bis zu ${m.slots.fullUsers} Parteien an einer Box; die letzte Box kann weniger belegt sein. Eine rechnerische Prüfung, kein Lade- oder Belegungsfahrplan. Bei Kapazitätswarnungen bleibt der Bedarf im Finanzmodell ungekürzt.</p></section>`:'';
  const vacancy=m.preset==='zurich'?`<p class="finance-note">Abrechenbar: ${decimal.format(m.billable)} Wohnungen im Jahresmittel. Bei Abo-Pause reduziert Leerstand das Abo, andernfalls trägt die Vermieterschaft dieses Risiko. Mehrmiete wird nur für belegte Wohnungen gerechnet; der Deckwert CHF 10’800 war vor Leerstand. Mietaufschläge sind eine unbestätigte Annahme, keine zugesicherte Einnahme.</p>`:'';
  return `<details class="finance-details"><summary>Rechenweg, Sensitivität & Jahreswerte</summary><div class="finance-detail-grid"><div class="finance-table-wrap" tabindex="0" role="region" aria-label="Jahresrechnung"><table><caption>Jahresrechnung · CHF</caption><thead><tr><th scope="col">Position</th><th scope="col">Pro Jahr</th></tr></thead><tbody>${resultRows(m).map(([label,value])=>`<tr><th scope="row">${label}</th><td>${chf(value)}</td></tr>`).join('')}</tbody></table>${vacancy}</div><div><h4>${m.preset==='zurich'?'Abo':'Entschädigung'} verändern</h4><div class="finance-sensitivity">${sensitivity(m.state).map(s=>`<div><span>${chf(s.value)} / Monat</span><strong>${chf(s.annualCash)} / Jahr</strong><small>${s.payback===null?'Keine Amortisation':`${decimal.format(s.payback)} Jahre Amortisation`}</small></div>`).join('')}</div>${cashTable}</div></div>${comparison}${slot}<p class="finance-note">${sources(m.preset)}</p></details>`;
}
const QUICK_FIELDS={zurich:['subscription','margin','chargerCost','maintenance'],cham:['feePerBox','evShare','markup','installCost']};
const SLIDER_MAX={subscription:100,margin:20,chargerCost:10000,maintenance:15,feePerBox:150,evShare:100,markup:25,installCost:8000};
const QUICK_HELP={subscription:'Monatlich je abrechenbarer Wohnung',margin:'Marge auf jede geladene Kilowattstunde',chargerCost:'Hardware und Installation je Ladepunkt',maintenance:'Jährlicher Anteil der Investition',feePerBox:'Monatlich je installierter Wallbox',evShare:'Anteil an Wohnungen mit Parkplatz',markup:'Aufschlag auf den Stromeinkauf',installCost:'Je Wallbox, zusätzlich zur Hardware'};
const fieldNumber=new Intl.NumberFormat('de-CH',{maximumFractionDigits:2});
const unitText=f=>({'CHF/Monat':'CHF / Monat','Rp./kWh':'Rp. / kWh','% der Investition/Jahr':'% / Jahr'}[f.unit]||f.unit||'');
export function mountFinance(root,{compact=false,preset='zurich',sync=true}={}) {
  if(!root)throw new TypeError('Finance root is required');
  mounted.get(root)?.destroy();
  const id=`finance-${++seq}`;
  let state=sync?readFinanceState(preset):normalizeState({preset}),result=calculateFinance(state),destroyed=false,narrow=root.clientWidth<=520;
  root.classList.add('finance');root.classList.toggle('finance--compact',compact);
  const fields=()=>FINANCE_FIELDS[state.preset].flatMap(g=>g.fields);
  let sliderLimits={},rendering=false;
  function sliderMax(f){return sliderLimits[f.key]=Math.min(f.max,Math.max(sliderLimits[f.key]||0,SLIDER_MAX[f.key]||f.max,Math.ceil(state.values[f.key]/f.step)*f.step));}
  function input(f,quick=false) {
    const key=f.key,controlId=`${id}-${key}`,helpId=`${controlId}-help`;
    const numeric=`<div class="finance-number"><input id="${controlId}" data-finance-key="${key}" type="number" inputmode="decimal" value="${state.values[key]}" min="${f.min}" max="${f.max}" step="${f.step}" required aria-describedby="${helpId} ${id}-validation"><span aria-hidden="true">${escape(unitText(f))}</span></div>`;
    return `<div class="finance-field ${quick?'finance-lever':''}"><div class="finance-field-heading"><label for="${controlId}">${escape(f.label)}${f.unit?`<span class="finance-sr"> (${escape(f.unit)})</span>`:''}</label>${quick?`<small>Basis ${fieldNumber.format(f.value)}</small>`:''}</div>${f.options?`<select id="${controlId}" data-finance-key="${key}" aria-describedby="${helpId}">${f.options.map(([v,label])=>`<option value="${v}">${escape(label)}</option>`).join('')}</select>`:numeric}${quick?`<input type="range" class="finance-slider" data-finance-slider="${key}" min="${f.min}" max="${sliderMax(f)}" step="${f.step}" value="${state.values[key]}" aria-label="${escape(f.label)} – Regler" aria-describedby="${helpId}">`:''}<p class="finance-field-help" id="${helpId}">${quick?escape(QUICK_HELP[key]):escape(f.unit||'Auswahl für dieses Szenario')}</p></div>`;
  }
  function drawShell() {
    // Replacing a focused field may synchronously emit its final change event.
    // Ignore that old control while the model and its DOM are being switched.
    rendering=true;
    try {
    sliderLimits={};
    const groups=FINANCE_FIELDS[state.preset],quick=QUICK_FIELDS[state.preset];
    const quickFields=quick.map(key=>fields().find(f=>f.key===key));
    root.innerHTML=`<div class="finance-toolbar"><label for="${id}-preset"><span>Rechenmodell</span><select id="${id}-preset" data-finance-preset>${Object.entries(PRESET_LABELS).map(([value,label])=>`<option value="${value}">${label}</option>`).join('')}</select></label><div class="finance-toolbar-actions"><span class="finance-scenario-status" data-finance-status></span><button class="finance-reset" type="button" data-finance-reset>Basiswerte zurücksetzen</button></div></div><p class="finance-basis">${state.preset==='zurich'?'Zürich · Abo pro abrechenbarer Wohnung. Strommarge getrennt vom Abo.':'Cham · alternatives Modell: Entschädigung pro Wallbox, nicht pro Wohnung.'}</p><div class="finance-body"><section class="finance-assumptions" aria-labelledby="${id}-assumptions"><div class="finance-section-heading"><span class="finance-eyebrow">Was wäre, wenn …</span><h3 id="${id}-assumptions">Annahmen verändern</h3></div><div class="finance-quick">${quickFields.map(f=>input(f,true)).join('')}</div><p class="finance-validation" id="${id}-validation" role="status"></p><p class="finance-control-hint">Regler bewegen oder Werte direkt eingeben.</p></section><section class="finance-results" aria-label="Berechnetes Szenario"></section></div><details class="finance-advanced"><summary>Weitere Annahmen <span>Gebäude, Nutzung & Kosten</span></summary><div class="finance-advanced-grid">${groups.map(g=>{const remaining=g.fields.filter(f=>!quick.includes(f.key));return remaining.length?`<fieldset class="finance-group"><legend>${g.title}</legend><div class="finance-fields">${remaining.map(f=>input(f)).join('')}</div></fieldset>`:'';}).join('')}</div></details><div class="finance-more"></div><p class="finance-note finance-boundary">Szenario, keine Prognosegarantie. Konstante Jahreswerte; ohne Steuern, Finanzierung, Inflation oder Ersatzinvestitionen.${state.preset==='zurich'?' Der Überschuss ist vor Abschreibung, kein Nettogewinn.':' Akquise wird im Cashflow einmalig zu Beginn bezahlt, nicht nochmals jährlich.'}</p><span class="finance-sr" data-finance-live aria-live="polite" aria-atomic="true"></span>`;
    syncControls();drawResult();
    } finally {rendering=false;}
  }
  function syncControls(changedKey) {
    root.querySelector('[data-finance-preset]').value=state.preset;
    for(const el of root.querySelectorAll('[data-finance-key]')){
      if((!changedKey||el.dataset.financeKey===changedKey)&&el!==document.activeElement){el.value=state.values[el.dataset.financeKey];el.removeAttribute('aria-invalid');}
    }
    for(const el of root.querySelectorAll('[data-finance-slider]')){
      const key=el.dataset.financeSlider,f=fields().find(f=>f.key===key);
      el.max=sliderMax(f);el.value=state.values[key];
      el.setAttribute('aria-valuetext',`${fieldNumber.format(state.values[key])} ${unitText(f)}`);
    }
  }
  function drawResult(announce=false) {
    result=calculateFinance(state);
    const oldDetails=root.querySelector('.finance-details')?.open,baseline=calculateFinance({preset:state.preset});
    const delta=result.cashflow.at(-1).value-(-baseline.investment+baseline.annualCash*result.horizon);
    const changed=Object.keys(state.values).filter(k=>state.values[k]!==PRESETS[state.preset][k]).length;
    root.querySelector('[data-finance-status]').textContent=changed?`${changed} ${changed===1?'Annahme verändert':'Annahmen verändert'}`:'Basis-Szenario';
    root.querySelector('[data-finance-status]').classList.toggle('is-changed',changed>0);
    root.querySelector('.finance-results').innerHTML=`<div class="finance-chart-panel"><div class="finance-chart-heading"><div><span class="finance-eyebrow">Auswirkung im Zeitverlauf</span><h3>Kumulierter Cashflow</h3></div><span class="finance-horizon">${result.horizon} Jahre · CHF</span></div><div class="finance-outcome"><div><span>Nach ${result.horizon} Jahren</span><strong>${chf(result.cashflow.at(-1).value)}</strong></div><p class="finance-delta">${delta===0?'Gleich wie Basiswerte':`${delta>0?'+':'−'} CHF ${number(Math.abs(delta))} zur Basis`}</p></div>${chart(result,id,compact,narrow)}</div>${kpis(result,compact)}${result.warnings.length?`<ul class="finance-warnings">${result.warnings.map(w=>`<li>${escape(w)}</li>`).join('')}</ul>`:''}`;
    root.querySelector('.finance-more').innerHTML=detailsHtml(result,id);
    if(oldDetails)root.querySelector('.finance-details').open=true;
    if(announce)root.querySelector('[data-finance-live]').textContent=`Neu berechnet: ${chf(result.annualCash)} Cash-Überschuss pro Jahr.`;
  }
  function publish() {
    if(sync)saveFinanceState(state);
    window.dispatchEvent(new CustomEvent('voltoshare:finance-change',{detail:{state:structuredClone(state),result,source:id}}));
  }
  function updateValidation(){
    const invalid=root.querySelector('[data-finance-key][aria-invalid="true"]');
    root.querySelector('.finance-validation').textContent=invalid?`Bitte einen gültigen Wert zwischen ${invalid.min} und ${invalid.max} eingeben. Die letzte gültige Rechnung bleibt sichtbar.`:'';
  }
  function onInput(event) {
    const el=event.target,key=el.dataset.financeKey||el.dataset.financeSlider;
    if(rendering||!key||!root.contains(el)||!fields().some(f=>f.key===key))return;
    const valid=el.checkValidity();el.setAttribute('aria-invalid',String(!valid));
    if(!valid){updateValidation();return;}
    state=normalizeState({...state,values:{...state.values,[key]:el.tagName==='SELECT'?el.value:Number(el.value)}});
    if(el.dataset.financeSlider){const peer=root.querySelector(`[data-finance-key="${key}"]`);peer.value=state.values[key];peer.removeAttribute('aria-invalid');}
    syncControls(key);updateValidation();drawResult();publish();
  }
  function onChange(event) {
    if(rendering||!root.contains(event.target))return;
    if(event.target.matches('[data-finance-preset]')) {
      state=sync?readFinanceState(event.target.value):normalizeState({preset:event.target.value});drawShell();publish();
    }else if(event.target.matches('[data-finance-key],[data-finance-slider]')) {
      onInput(event);drawResult(true);
    }
  }
  function onClick(event) {
    if(event.target.closest('[data-finance-reset]')){state=normalizeState({preset:state.preset});drawShell();publish();root.querySelector('[data-finance-reset]').focus();}
  }
  function receive(event) {
    if(!sync||event.detail?.source===id||event.detail?.state?.preset!==state.preset)return;
    state=normalizeState(event.detail.state);syncControls();drawResult();
  }
  function onStorage(event) {if(sync&&event.key===FINANCE_STORAGE_KEY){state=readFinanceState(state.preset);syncControls();drawResult();}}
  root.addEventListener('input',onInput);root.addEventListener('change',onChange);root.addEventListener('click',onClick);
  window.addEventListener('voltoshare:finance-change',receive);window.addEventListener('storage',onStorage);
  drawShell();
  const resizeObserver=typeof ResizeObserver==='undefined'?null:new ResizeObserver(()=>{
    if(destroyed)return;
    const next=root.clientWidth<=520;
    if(next!==narrow){narrow=next;drawResult();}
  });
  resizeObserver?.observe(root);
  const api={getState:()=>structuredClone(state),getResult:()=>calculateFinance(state),setState(patch){const previous=state.preset;state=normalizeState({preset:patch.preset??state.preset,values:{...(patch.preset&&patch.preset!==previous?PRESETS[patch.preset]:state.values),...patch.values}});if(previous!==state.preset)drawShell();else{syncControls();drawResult();}publish();},destroy(){if(destroyed)return;destroyed=true;resizeObserver?.disconnect();root.removeEventListener('input',onInput);root.removeEventListener('change',onChange);root.removeEventListener('click',onClick);window.removeEventListener('voltoshare:finance-change',receive);window.removeEventListener('storage',onStorage);mounted.delete(root);}};
  mounted.set(root,api);return api;
}
