/** Mutating browser tests. Run only against an isolated local demo database. */
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/home/mathis/openclaw-workspace/option-pricing-workbench/web/node_modules/playwright-core');
const base=process.env.BASE_URL||'http://127.0.0.1:18931';
assert.ok(['127.0.0.1','localhost'].includes(new URL(base).hostname),'Refusing mutating parking tests on a public host');
let checks=0;const ok=(v,m)=>{assert.ok(v,m);checks++;};
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
const images=[];const created=[];
let alex;
try{
 const context=await browser.newContext({viewport:{width:1440,height:1100},reducedMotion:'reduce'}),page=await context.newPage(),errors=[];alex=context;
 page.on('pageerror',e=>errors.push(e.message));
 const state=async c=>(await (await c.request.get(base+'/api/state/')).json());
 const post=async(c,url,data)=>{const csrf=(await c.cookies()).find(x=>x.name==='csrftoken')?.value;return c.request.post(base+url,{data,headers:{'X-CSRFToken':csrf,Referer:base+'/'}});};
 const login=async(p,name)=>{await p.goto(base+'/login/');await p.getByRole('button',{name:new RegExp('Explore as '+name)}).click();await p.waitForURL(base+'/');await p.waitForSelector('#app-view h1');};
 const route=async(name)=>{await page.goto(base+'/#'+name);await page.waitForSelector('#app-view h1');if(name==='parking')await page.waitForSelector('.garage-plan');};
 await login(page,'Alex');let data=await state(context);ok(data.demo===true,'isolated demo mode');
 const floors=[...new Set(data.bays.map(b=>b.floor))];ok(floors.includes('UG1')&&floors.includes('UG2'),'two staged floors');
 const ug1=data.bays.filter(b=>b.floor==='UG1'),ug2=data.bays.filter(b=>b.floor==='UG2');ok(ug1.length===20&&ug2.length===8,'original and test-only floor inventories');
 const ordinary=ug2.find(b=>!b.charger_id&&b.bookable),otherOrdinary=ug2.find(b=>!b.charger_id&&b.bookable&&b.id!==ordinary.id),charger=data.chargers.find(c=>c.status==='available'),chargedBay=data.bays.find(b=>b.id===charger.bay_id),vehicle=data.vehicles.find(v=>!v.archived&&v.connector===charger.connector);
 const local=d=>{const parts=Object.fromEntries(new Intl.DateTimeFormat('en-CA',{timeZone:data.property.timezone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(d).map(x=>[x.type,x.value]));return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}`;};
 const overlaps=(a,b,c,d)=>a<d&&c<b;
 let start=new Date(Math.ceil((Date.now()+3*86400000)/1800000)*1800000),end=new Date(+start+3600000);
 while(data.reservations.some(r=>r.status!=='cancelled'&&r.vehicle_id===vehicle.id&&overlaps(+start,+end,+new Date(r.start),+new Date(r.end)))){start=new Date(+start+7200000);end=new Date(+start+3600000);}
 const times=async(s=start,e=end)=>{await page.locator('#booking-start').fill(local(s));await page.locator('#booking-end').fill(local(e));await page.locator('#booking-vehicle').selectOption(String(vehicle.id));};
 await route('parking');await times();
 ok(await page.locator('.garage-plan [data-action="select-bay"]').count()===20,'every UG1 ordinary and charging bay visible');
 ok(await page.locator('.garage-plan').innerText().then(t=>t.includes('Illustrative'))||await page.locator('#parking-live').innerText().then(t=>t.includes('Illustrative')),'map is truthfully schematic');
 await page.locator('[data-action="parking-floor"][data-id="UG2"]').click();
 ok(await page.locator('.garage-plan [data-action="select-bay"]').count()===8,'floor switch replaces full bay inventory');
 await page.locator(`[data-action="select-bay"][data-id="${ordinary.id}"]`).click();
 ok((await page.locator('#charger-details').innerText()).includes('Parking only'),'ordinary-space detail');
 ok(await page.locator('[data-action="review-booking"]').isEnabled(),'ordinary bay can be reserved');
 const beforeAccounts=JSON.stringify({sessions:data.sessions,invoices:data.invoices});
 await page.locator('[data-action="review-booking"]').click();
 ok((await page.locator('#dialog-content').innerText()).includes('Parking only'),'ordinary review not charging tariff');
 const createResponse=page.waitForResponse(r=>r.url()===base+'/api/reservations/'&&r.request().method()==='POST');
 await page.locator('#dialog-form button[type="submit"]').click();const createdBody=await(await createResponse).json();
 ok(createdBody.ok,'ordinary reservation saved');const reservationID=createdBody.reservation_id;created.push(reservationID);
 await page.waitForFunction(()=>!document.querySelector('dialog').open);
 data=await state(context);let reservation=data.reservations.find(r=>r.id===reservationID);
 ok(reservation?.bay_id===ordinary.id&&reservation.charger_id===null&&reservation.floor==='UG2','ordinary reservation has bay/floor but no charger');
 ok(JSON.stringify({sessions:data.sessions,invoices:data.invoices})===beforeAccounts,'parking booking creates no session or invoice');
 await page.reload();await page.waitForSelector('.garage-plan');
 ok((await state(context)).reservations.some(r=>r.id===reservationID),'reservation survives reload');
 const jordan=await browser.newContext(),jp=await jordan.newPage();await login(jp,'Jordan');const foreign=await state(jordan);
 const occupied=foreign.occupancy.find(o=>o.bay_id===ordinary.id&&o.kind==='reservation'&&o.start===reservation.start);
 ok(occupied&&!occupied.own,'other household sees ordinary bay occupancy');
 assert.deepEqual(Object.keys(occupied).sort(),['bay_id','charger_id','start','end','kind','own'].sort());checks++;
 ok(!foreign.reservations.some(r=>r.id===reservationID),'private reservation not disclosed');
 const blocked=await post(jordan,'/api/reservations/',{bay_id:ordinary.id,vehicle_id:foreign.vehicles.find(v=>!v.archived).id,start:local(start),end:local(end),request_id:'browser-conflict-'+Date.now()});
 ok(blocked.status()>=400&&!(await blocked.json()).ok,'second household cannot double book');
 const card=page.locator('.reservation-card').filter({has:page.locator(`[data-action="reservation-detail"][data-id="${reservationID}"]`)});
 await card.locator('[data-action="reservation-detail"]').click();await page.locator(`[data-action="reservation-edit"][data-id="${reservationID}"]`).click();
 await page.locator(`[data-action="select-bay"][data-id="${otherOrdinary.id}"]`).click();
 await page.locator('[data-action="review-booking"]').click();
 const changeResponse=page.waitForResponse(r=>r.url()===base+`/api/reservations/${reservationID}/change/`&&r.request().method()==='POST');
 await page.locator('#dialog-form button[type="submit"]').click();ok((await(await changeResponse).json()).ok,'ordinary booking edit succeeds');
 await page.waitForFunction(()=>!document.querySelector('dialog').open);
 reservation=(await state(context)).reservations.find(r=>r.id===reservationID);ok(reservation.bay_id===otherOrdinary.id,'edit moves bay and preserves booking');
 await page.locator(`[data-action="reservation-detail"][data-id="${reservationID}"]`).click();await page.locator(`[data-action="reservation-cancel"][data-id="${reservationID}"]`).click();
 const cancelResponse=page.waitForResponse(r=>r.url()===base+`/api/reservations/${reservationID}/cancel/`&&r.request().method()==='POST');
 await page.locator('#dialog-form button[type="submit"]').click();ok((await(await cancelResponse).json()).ok,'ordinary reservation cancellation succeeds');await page.waitForFunction(()=>!document.querySelector('dialog').open);
 ok((await state(context)).reservations.find(r=>r.id===reservationID).status==='cancelled','cancelled record retained');
 await page.locator('#parking-search').fill(chargedBay.label);await page.locator('#parking-search').dispatchEvent('change');
 ok(await page.locator('[data-action="parking-floor"][data-id="UG1"]').getAttribute('aria-pressed')==='true','search changes floor');
 ok((await page.locator('#charger-details').innerText()).includes(charger.name),'search selects requested charger');
 await times();await page.locator('[data-action="review-booking"]').click();ok((await page.locator('#dialog-content').innerText()).includes('/ kWh'),'charger review retains energy tariff');
 const chargeResponse=page.waitForResponse(r=>r.url()===base+'/api/reservations/'&&r.request().method()==='POST');await page.locator('#dialog-form button[type="submit"]').click();const chargeBody=await(await chargeResponse).json();ok(chargeBody.ok,'charger reservation succeeds');created.push(chargeBody.reservation_id);await page.waitForFunction(()=>!document.querySelector('dialog').open);
 const chargeReservation=(await state(context)).reservations.find(r=>r.id===chargeBody.reservation_id);ok(chargeReservation.charger_id===charger.id&&chargeReservation.bay_id===chargedBay.id,'charging reservation keeps correct bay+charger');
 await post(context,`/api/reservations/${chargeBody.reservation_id}/cancel/`,{});await page.reload();await page.waitForSelector('.garage-plan');await times();
 await page.locator('[data-action="parking-view"][data-view="list"]').click();ok(await page.locator('.garage-space-list [data-action="select-bay"]').count()===20,'list contains ordinary as well as charging spaces');
 await page.locator('[data-action="parking-view"][data-view="map"]').click();const widthBefore=await page.locator('.garage-plan').evaluate(e=>e.getBoundingClientRect().width);await page.locator('[data-action="map-zoom-in"]').click();ok(await page.locator('.garage-plan').evaluate(e=>e.getBoundingClientRect().width)>widthBefore,'zoom enlarges architectural plan');await page.locator('[data-action="map-zoom-reset"]').click();
 const firstBay=page.locator('.garage-plan [data-row="0"][data-column="0"]');const nextBay=page.locator('.garage-plan [data-row="0"][data-column="1"]');await firstBay.focus();await page.keyboard.press('ArrowRight');ok(await nextBay.evaluate(e=>document.activeElement===e),'arrow keys navigate adjacent physical bays');
 const originalStart=await page.locator('#booking-start').inputValue();await page.locator('#booking-start').fill('');ok(await page.locator('.garage-plan').count()===1,'empty time retains usable garage');ok(await page.locator('[data-action="review-booking"]').isDisabled(),'empty time prevents booking');await page.locator('#booking-start').fill(originalStart);
 for(const width of [360,768,1440]){await page.setViewportSize({width,height:1100});await page.evaluate(()=>document.fonts.ready);ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'parking fits viewport '+width);ok(await page.locator('.garage-plan [data-action="select-bay"]').evaluateAll(nodes=>nodes.every(n=>{const r=n.getBoundingClientRect();return r.width>=44&&r.height>=44;})),'all bay targets at least44 '+width);if(width<=768)ok(await page.locator('.garage-scroll').evaluate(e=>e.scrollWidth>e.clientWidth),'garage pans within its viewport '+width);ok(await page.locator('.garage-selection').evaluate(e=>{const n=e.querySelector('.garage-selected-number').getBoundingClientRect(),h=e.querySelector('h2').getBoundingClientRect();return h.top>=n.bottom-1;}),'selected-space heading does not overlap bay number '+width);if(process.env.SCREENSHOTS){const file=`/tmp/volto-parking-${width}.png`;await page.screenshot({path:file,fullPage:true});images.push(file);}}
 for(const name of ['dashboard','history','household','billing']){await route(name);for(const width of [360,1440]){await page.setViewportSize({width,height:1000});ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),name+' remains responsive '+width);}ok(await page.locator('#app-view h1').count()===1,name+' loads');}
 ok(errors.length===0,'no browser errors: '+errors.join(';'));
 console.log(`PASS ${checks} parking/reservation browser checks on ${base}`);if(images.length)console.log('Review images: '+images.join(', '));
}finally{
 if(alex){const csrf=(await alex.cookies()).find(x=>x.name==='csrftoken')?.value;for(const id of created){try{await alex.request.post(base+`/api/reservations/${id}/cancel/`,{data:{},headers:{'X-CSRFToken':csrf,Referer:base+'/'}});}catch{}}}
 await browser.close();
}
