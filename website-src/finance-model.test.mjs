import test from 'node:test';
import assert from 'node:assert/strict';
import {PRESETS,normalizeState,calculateFinance,sensitivity} from './finance-model.mjs';
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-7,`${a} != ${b}`);
const scenario=(preset,values={})=>calculateFinance({preset,values});
test('Zurich source deck baseline reconciles cash result and break-even',()=>{
 const r=scenario('zurich');assert.equal(r.investment,60000);assert.equal(r.energy,60000);assert.equal(r.subscription,18000);assert.equal(r.energyMargin,3600);assert.equal(r.costs,5700);assert.equal(r.annualCash,15900);close(r.payback,60000/15900);assert.equal(r.cashflow[0].value,-60000);assert.equal(r.cashflow[10].value,99000);assert.equal(r.ebit,null);assert.equal(r.revenue,null);
});
test('Deck sensitivity reproduces CHF 15 / 25 / 35 annual outcomes',()=>{
 assert.deepEqual(sensitivity({preset:'zurich'}).map(r=>r.annualCash),[8700,15900,23100]);
});
test('Vacancy policy changes apartment subscription only; rent uses occupied apartments',()=>{
 const full=scenario('zurich',{vacancy:10});const pause=scenario('zurich',{vacancy:10,vacancyPolicy:'pause'});
 assert.equal(full.billable,60);assert.equal(pause.billable,54);assert.equal(full.subscription-pause.subscription,1800);assert.equal(full.energy,pause.energy);assert.equal(full.rent,25920);assert.equal(full.landlordNet,7920);
});
test('Zero-margin loss has no fabricated payback',()=>{
 const r=scenario('zurich',{subscription:0,margin:0});assert.equal(r.annualCash,-5700);assert.equal(r.payback,null);assert.ok(r.cashflow.at(-1).value<r.cashflow[0].value);
});
test('Cham reproduces supplied calculator baseline',()=>{
 const r=scenario('cham');assert.equal(r.evs,22);assert.equal(r.chargers,6);assert.equal(r.energy,42900);assert.equal(r.investment,17400);assert.equal(r.subscription,3960);close(r.revenue,16036.35);close(r.energyCost,42900/0.98*0.2115);close(r.ebitda,4807.920841836733);close(r.ebit,3067.920841836733);close(r.payback,17400/r.annualCash);
});
test('Cham uses charger compensation, never apartment subscription',()=>{
 const r=scenario('cham',{feePerBox:100});assert.equal(r.subscription,6*100*12);assert.notEqual(r.subscription,270*100*12);
});
test('Zero EV demand creates no phantom vehicle, box, sales or tenant comparison',()=>{
 const r=scenario('cham',{evShare:0});assert.equal(r.evs,0);assert.equal(r.chargers,0);assert.equal(r.investment,0);assert.equal(r.revenue,0);assert.equal(r.annualCash,0);assert.equal(r.tenant,null);assert.equal(r.slots.fullUsers,0);assert.equal(r.payback,null);assert.ok(r.cashflow.every(x=>Number.isFinite(x.value)));
});
test('Acquisition cash occurs exactly once, while annual allocated expense is displayed',()=>{
 const plain=scenario('cham'),withAcq=scenario('cham',{acqOn:'yes',acqCost:2500,contractYears:10});
 assert.equal(withAcq.investment-plain.investment,2500);close(withAcq.annualCash,plain.annualCash);close(withAcq.ebitda,plain.ebitda-250);close(withAcq.cashflow.at(-1).value,plain.cashflow.at(-1).value-2500);close(withAcq.payback,19900/plain.annualCash);
});
test('Grid loss reduces energy margin, fees scale with gross energy sales',()=>{
 const clean=scenario('cham',{gridLoss:0}),lossy=scenario('cham',{gridLoss:10});assert.ok(lossy.energyMargin<clean.energyMargin);assert.equal(lossy.payment,clean.payment);close(clean.payment,clean.energyRevenue*.025);
});
test('Subsidy cannot produce negative capex or a refund',()=>{
 const r=scenario('cham',{subsidy:10000});assert.equal(r.capex,0);assert.equal(r.investment,0);assert.ok(r.warnings.some(x=>x.includes('Förderbeitrag')));
});
test('Slot overbooking and insufficient time remain explicit; no false revenue throttling',()=>{
 const r=scenario('cham',{usersPerBox:8,daySlots:3,dayPerUser:3,nightPerUser:0,dayHours:0.5,boxPower:1});assert.ok(r.slots.overbooked>0);assert.equal(r.slots.timeOk,false);assert.equal(r.energy,42900);assert.ok(r.warnings.length>=2);
});
test('Zero booked slots and overlapping daily duration expose feasibility errors',()=>{
 const r=scenario('cham',{dayPerUser:0,nightPerUser:0,dayHours:15,nightHours:15});assert.equal(r.slots.kwhPerSlot,null);assert.equal(r.slots.dailyHoursOk,false);assert.ok(r.warnings.some(x=>x.includes('Keine Ladeslots')));
});
test('Zero user energy remains finite, and zero lifetime/divisors are normalized',()=>{
 const r=scenario('cham',{kmPerYear:0,lifetime:0,usersPerBox:0,contractYears:0});for(const k of ['annualCash','ebit','investment','energy'])assert.ok(Number.isFinite(r[k]));assert.equal(r.state.values.lifetime,1);assert.equal(r.state.values.usersPerBox,1);
});
test('Malformed, nonfinite, negative, unknown and out-of-range inputs are bounded',()=>{
 const s=normalizeState({preset:'unexpected',values:{flats:-20,subscription:Infinity,margin:NaN,maintenance:200,vacancy:300,unexpected:'x'}});assert.equal(s.preset,'zurich');assert.equal(s.values.flats,0);assert.equal(s.values.subscription,25);assert.equal(s.values.margin,6);assert.equal(s.values.maintenance,100);assert.equal(s.values.vacancy,100);assert.equal(s.values.unexpected,undefined);
});
test('Defaults are immutable and edits do not contaminate next scenario',()=>{
 const s=normalizeState({preset:'zurich'});s.values.subscription=100;assert.equal(PRESETS.zurich.subscription,25);assert.equal(scenario('zurich').subscription,18000);
});
test('All schema boundary cases produce finite money and cash series',()=>{
 for(const preset of ['zurich','cham'])for(const values of [{},{flats:10000,evShare:100,evs:10000,kwhPerEv:100000},{flats:0,evShare:0,evs:0,chargers:0},{subscription:0,feePerBox:0,margin:0,markup:0}]){
 const r=scenario(preset,values);for(const key of ['investment','annualCash','energy','subscription','energyMargin','costs'])assert.ok(Number.isFinite(r[key]),`${preset}.${key}`);assert.ok(r.cashflow.every(x=>Number.isFinite(x.value)));assert.ok(r.payback===null||Number.isFinite(r.payback));
 }
});

test('Sensitivity labels and calculations stay aligned at upper and lower bounds',()=>{
 for(const [preset,key] of [['zurich','subscription'],['cham','feePerBox']]){
 for(const value of [0,1000]) {const rows=sensitivity({preset,values:{[key]:value}});assert.equal(new Set(rows.map(r=>r.value)).size,rows.length);for(const r of rows){assert.equal(r.value,r.state.values[key]);assert.ok(r.value>=0&&r.value<=1000);}}
 }
});
