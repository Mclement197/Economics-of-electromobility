/** Shared, deterministic scenario engine. Inputs are team assumptions, not offers. */
const field = (key, label, unit, value, min=0, max=1000000, step=1) => ({key,label,unit,value,min,max,step});
const select = (key,label,value,options) => ({key,label,value,options});
export const FINANCE_FIELDS = {
  zurich: [
    {title:'Gebäude & Nutzung', fields:[field('flats','Wohnungen','Wohnungen',60,0,10000),field('chargers','Ladepunkte','Ladepunkte',15,0,10000),field('evs','E-Autos','Fahrzeuge',24,0,10000),field('kwhPerEv','Strombedarf je E-Auto','kWh/Jahr',2500,0,100000,100)]},
    {title:'Preise & Leerstand', fields:[field('subscription','Abo pro Wohnung','CHF/Monat',25,0,1000,1),field('margin','Stromaufschlag','Rp./kWh',6,0,100,0.5),field('rent','Mietaufschlag pro Wohnung','CHF/Monat',40,0,1000),field('vacancy','Leerstand','%',0.1,0,100,0.1),select('vacancyPolicy','Abo bei Leerstand','continue',[['continue','Weiterlaufen lassen'],['pause','Für Leerstand pausieren']])]},
    {title:'Investition & Betrieb',fields:[field('chargerCost','Kosten je Ladepunkt','CHF',3000,0,100000,100),field('gridCost','Netzanschluss & Lastmanagement','CHF',15000,0,1000000,500),field('platform','Plattform & Software','CHF/Jahr',1800,0,1000000,100),field('maintenance','Wartung & Support','% der Investition/Jahr',4,0,100,0.5),field('other','Messung, Zahlung, Versicherung','CHF/Jahr',1500,0,1000000,100)]},
  ],
  cham: [
    {title:'Liegenschaft',fields:[field('flats','Wohnungen','Wohnungen',270,0,10000,10),field('parkingShare','Wohnungen mit Parkplatz','%',70,0,100),field('evShare','Anteil Elektroautos','%',11.9,0,100,0.1),field('usersPerBox','Mietparteien pro Wallbox','Parteien',4,1,8),field('boxPower','Ladeleistung pro Wallbox','kW',11,1,350,0.1)]},
    {title:'Nutzung',fields:[field('kmPerYear','Fahrleistung pro E-Auto','km/Jahr',13000,0,100000,500),field('consumption','Verbrauch ab Steckdose','kWh/100 km',20,0,100,0.5),field('homeShare','Anteil zu Hause geladen','%',75,0,100),field('battery','Nutzbare Batterie','kWh',60,1,300,5)]},
    {title:'Preise',fields:[field('feePerBox','Entschädigung pro Wallbox','CHF/Monat',55,0,1000),field('buyPrice','Stromeinkauf (WWZ-Annahme)','Rp./kWh',21.15,0,200,0.05),field('markup','Stromaufschlag','Rp./kWh',7,0,100,0.5),field('gridLoss','Leitungsverluste bis Zähler','%',2,0,30,0.5)]},
    {title:'Kosten pro Wallbox',fields:[field('hwCost','Hardware inkl. MID-Zähler','CHF',950,0,100000,50),field('installCost','Installation & Infrastrukturanteil','CHF',1950,0,100000,50),field('subsidy','Förderbeitrag pro Wallbox','CHF',0,0,100000,50),field('lifetime','Nutzungsdauer','Jahre',10,1,25),field('paymentFee','Zahlungsgebühren','% Stromumsatz',2.5,0,100,0.1),field('backendPerBox','App, Backend, Datenverbindung','CHF/Monat',4,0,10000,0.5),field('servicePerBox','Wartung, Reparatur, Versicherung','CHF/Jahr',80,0,100000,5),field('overheadPerBox','Overhead-Anteil Anbieter','CHF/Jahr',150,0,100000,10)]},
    {title:'Akquise & Vergleich',fields:[select('acqOn','Akquisekosten berücksichtigen','no',[['no','Nein'],['yes','Ja']]),field('acqCost','Akquise für die Liegenschaft','CHF',2500,0,1000000,250),field('contractYears','Vertragsdauer','Jahre',10,1,30),field('publicPrice','Öffentliches AC-Laden','Rp./kWh',50,0,300)]},
    {title:'Ladeslots',fields:[field('daySlots','Tagslots pro Wallbox','pro Woche',7,0,7),field('nightSlots','Nachtslots pro Wallbox','pro Woche',7,0,7),field('dayHours','Dauer Tagslot','Stunden',10,0.5,24,0.5),field('nightHours','Dauer Nachtslot','Stunden',12,0.5,24,0.5),field('dayPerUser','Tagslots pro Mietpartei','pro Woche',1,0,7),field('nightPerUser','Nachtslots pro Mietpartei','pro Woche',1,0,7)]}
  ]
};
export const PRESETS = Object.freeze(Object.fromEntries(Object.entries(FINANCE_FIELDS).map(([name,groups])=>[name,Object.freeze(Object.fromEntries(groups.flatMap(g=>g.fields).map(f=>[f.key,f.value])))])));
export const PRESET_LABELS = {zurich:'Zürich · Abo pro Wohnung',cham:'Cham · Entschädigung pro Wallbox'};
export function normalizeState(input={}) {
  const preset=input.preset==='cham'?'cham':'zurich';
  const values={};
  for(const f of FINANCE_FIELDS[preset].flatMap(g=>g.fields)) {
    const raw=input.values?.[f.key];
    if(f.options) values[f.key]=f.options.some(o=>o[0]===raw)?raw:f.value;
    else {const n=typeof raw==='number'?raw:NaN;values[f.key]=Number.isFinite(n)?Math.min(f.max,Math.max(f.min,n)):f.value;}
  }
  for(const key of preset==='zurich'?['flats','chargers','evs']:['flats','usersPerBox','lifetime','daySlots','nightSlots','dayPerUser','nightPerUser']) values[key]=Math.round(values[key]);
  return {preset,values};
}
function cashSeries(investment,annualCash,horizon) {
  return Array.from({length:horizon+1},(_,year)=>({year,value:-investment+annualCash*year}));
}
export function calculateFinance(input={}) {
  const state=normalizeState(input),p=state.values;
  if(state.preset==='zurich') {
    const occupied=p.flats*(1-p.vacancy/100),billable=p.vacancyPolicy==='pause'?occupied:p.flats;
    const investment=p.chargers*p.chargerCost+p.gridCost;
    const energy=p.evs*p.kwhPerEv,subscription=billable*p.subscription*12,energyMargin=energy*p.margin/100;
    const maintenance=investment*p.maintenance/100,costs=p.platform+maintenance+p.other;
    const annualCash=subscription+energyMargin-costs;
    const rent=occupied*p.rent*12;
    return {preset:'zurich',state,investment,annualCash,ebitda:annualCash,ebit:null,revenue:null,netRevenue:subscription+energyMargin,subscription,energyMargin,costs,maintenance,energy,evs:p.evs,chargers:p.chargers,occupied,billable,rent,landlordNet:rent-subscription,payback:annualCash>0?investment/annualCash:null,horizon:10,cashflow:cashSeries(investment,annualCash,10),warnings:[...(p.evs>0&&p.chargers===0?['Energiebedarf ohne Ladepunkte: technisch nicht umsetzbar.']:[]),...(p.evs>p.flats?['Mehr E-Autos als Wohnungen: Mehrfahrzeug-Haushalte werden vorausgesetzt.']:[])]};
  }
  const parking=p.flats*p.parkingShare/100,evs=Math.max(0,Math.round(parking*p.evShare/100)),chargers=Math.ceil(evs/p.usersPerBox),avgUsers=chargers?evs/chargers:0;
  const energyPerUser=p.kmPerYear*p.consumption/100*p.homeShare/100,energy=evs*energyPerUser;
  const buy=p.buyPrice/100,sell=(p.buyPrice+p.markup)/100,capexBox=Math.max(0,p.hwCost+p.installCost-p.subsidy),capex=capexBox*chargers;
  const subscription=p.feePerBox*12*chargers,energyRevenue=energy*sell,revenue=subscription+energyRevenue;
  const energyCost=energy/(1-p.gridLoss/100)*buy,payment=energyRevenue*p.paymentFee/100,backend=p.backendPerBox*12*chargers,service=p.servicePerBox*chargers,overhead=p.overheadPerBox*chargers;
  const acquisition=p.acqOn==='yes'?p.acqCost:0,acquisitionAnnual=acquisition/p.contractYears;
  const annualCash=revenue-energyCost-payment-backend-service-overhead;
  // Acquisition is paid once at t=0; its allocated expense is not a second cash payment.
  const ebitda=annualCash-acquisitionAnnual,depreciation=capex/p.lifetime,ebit=ebitda-depreciation,investment=capex+acquisition;
  const slotsPerUser=p.dayPerUser+p.nightPerUser,fullUsers=evs?Math.min(evs,p.usersPerBox):0;
  const bookedDay=fullUsers*p.dayPerUser,bookedNight=fullUsers*p.nightPerUser;
  const overbooked=Math.max(0,bookedDay-p.daySlots)+Math.max(0,bookedNight-p.nightSlots);
  const kwhPerSlot=slotsPerUser?energyPerUser/52/slotsPerUser:null,hoursNeeded=kwhPerSlot===null?null:kwhPerSlot/p.boxPower;
  const shortest=Math.min(p.dayPerUser?p.dayHours:Infinity,p.nightPerUser?p.nightHours:Infinity);
  const timeOk=hoursNeeded!==null&&hoursNeeded<=shortest,batteryOk=kwhPerSlot!==null&&kwhPerSlot<=p.battery;
  const dailyHoursOk=p.dayHours+p.nightHours<=24;
  const monthlyKwh=energyPerUser/12,vat=1.081;
  const tenant=evs?{volto:p.feePerBox/avgUsers+monthlyKwh*sell,wwz:35/vat+monthlyKwh*buy+Math.min(monthlyKwh*0.095/vat,16/vat),public:monthlyKwh*p.publicPrice/100,monthlyKwh}:null;
  const warnings=[];
  if(evs&&overbooked)warnings.push(`${overbooked} Slots pro Woche überbucht an einer voll belegten Wallbox.`);
  if(evs&&!slotsPerUser)warnings.push('Keine Ladeslots gebucht; der berechnete Energiebedarf kann so nicht gedeckt werden.');
  if(evs&&slotsPerUser&&!timeOk)warnings.push('Der Energiebedarf überschreitet die angenommene Ladezeit pro Slot.');
  if(evs&&slotsPerUser&&!batteryOk)warnings.push('Die Lademenge pro Slot übersteigt die nutzbare Batterie.');
  if(!dailyHoursOk)warnings.push('Tag- und Nachtslots summieren sich auf mehr als 24 Stunden.');
  if(p.subsidy>p.hwCost+p.installCost)warnings.push('Förderbeitrag übersteigt die Kosten; Investition wird bei null begrenzt.');
  return {preset:'cham',state,investment,annualCash,ebitda,ebit,revenue,netRevenue:revenue-energyCost,subscription,energyRevenue,energyMargin:energyRevenue-energyCost,energyCost,payment,backend,service,overhead,acquisition,acquisitionAnnual,depreciation,capexBox,capex,costs:energyCost+payment+backend+service+overhead+acquisitionAnnual,energy,energyPerUser,evs,chargers,parking,avgUsers,tenant,payback:annualCash>0?investment/annualCash:null,horizon:p.lifetime,cashflow:cashSeries(investment,annualCash,p.lifetime),slots:{fullUsers,bookedDay,bookedNight,overbooked,kwhPerSlot,hoursNeeded,timeOk,batteryOk,dailyHoursOk,available:p.daySlots+p.nightSlots,booked:bookedDay+bookedNight},warnings};
}
export function sensitivity(input={}) {
  const s=normalizeState(input),key=s.preset==='zurich'?'subscription':'feePerBox',base=s.values[key],step=s.preset==='zurich'?10:20;
  const candidates=[base-step,base,base+step].map(value=>normalizeState({...s,values:{...s.values,[key]:value}}).values[key]);
  return [...new Set(candidates)].map(value=>({value,...calculateFinance({...s,values:{...s.values,[key]:value}})}));
}
