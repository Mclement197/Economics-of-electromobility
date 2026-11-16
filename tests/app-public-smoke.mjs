import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/home/mathis/openclaw-workspace/option-pricing-workbench/web/node_modules/playwright-core');
const base=process.env.BASE_URL||'https://app-electromobility.mclement.ch';
let checks=0;function ok(v,label){assert.ok(v,label);checks++;}
const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
try{
 const c=await b.newContext(),p=await c.newPage(),errors=[];
 p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('status of 404'))errors.push(m.text());});
 ok((await p.goto(base+'/login/')).ok(),'public login');
 await p.getByRole('button',{name:/Explore as Alex/}).click();await p.waitForURL(base+'/');await p.waitForFunction(()=>document.querySelector('#sidebar-property')?.innerText.includes('A-12'));
 let data=await (await c.request.get(base+'/api/state/')).json();ok(data.ok&&data.role==='owner','authenticated Alex');ok(data.demo===true,'explicit demo');
 ok(data.chargers.length===5&&data.bays.length===20,'configured layout');
 for(const route of ['dashboard','parking','history','household','billing']){
  await p.goto(base+'/#'+route);await p.waitForFunction(()=>document.querySelector('#app-view h1')&&!document.querySelector('.loading-state'));await p.evaluate(()=>document.fonts.ready);
  for(const width of [360,768,1440]){await p.setViewportSize({width,height:1000});ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),route+' overflow '+width);}
  ok(await p.locator('#app-view h1').count()===1,route+' heading');
  ok(await p.evaluate(()=>[...document.images].every(i=>i.complete&&i.naturalWidth)),'images '+route);
 }
 const before=await(await c.request.get(base+'/api/state/')).json();
 const fp=d=>JSON.stringify({household:d.household,vehicles:d.vehicles,reservations:d.reservations,sessions:d.sessions,invoices:d.invoices});
 if(process.env.RESTART==='1'){
  const r=spawnSync('systemctl',['--user','restart','electromobility-app.service'],{encoding:'utf8'});ok(r.status===0,'restart');
  let ready=false;for(let n=0;n<15;n++){try{const r=await c.request.get(base+'/health/');if(r.ok()){ready=true;break;}}catch{}await new Promise(r=>setTimeout(r,1000));}
  ok(ready,'healthy after restart');const after=await(await c.request.get(base+'/api/state/')).json();ok(after.ok,'session survives restart');ok(fp(before)===fp(after),'household bookings and accounting survive restart');
 }
 const j=await b.newContext(),jp=await j.newPage();await jp.goto(base+'/login/');await jp.getByRole('button',{name:/Explore as Jordan/}).click();await jp.waitForURL(base+'/');
 const foreign=await(await j.request.get(base+'/api/state/')).json();ok(foreign.household.id!==before.household.id,'separate household');ok(!foreign.vehicles.some(v=>before.vehicles.some(w=>w.id===v.id)),'private vehicles separated');
 const invoice=before.invoices[0];ok((await c.request.get(base+`/invoices/${invoice.id}/print/`)).ok(),'own invoice printable');ok((await j.request.get(base+`/invoices/${invoice.id}/print/`)).status()===404,'foreign invoice denied');
 const anon=await b.newContext();ok((await anon.request.get(base+'/api/state/')).status()===401,'anonymous state denied');ok((await anon.request.get(base+'/api/history.csv')).status()===401,'anonymous CSV denied');
 const csv=await c.request.get(base+'/api/history.csv');ok(csv.ok()&&(await csv.text()).includes('Cost CHF'),'own CSV');
 for(const path of ['/static/brand/site.webmanifest','/static/brand/symbol.svg','/static/brand/apple-touch-icon.png','/static/brand/icon-192.png','/static/brand/icon-512.png','/static/brand/fonts/LiberationSans-Regular.ttf','/static/brand/fonts/LiberationSans-Bold.ttf'])ok((await c.request.get(base+path)).ok(),'asset '+path);
 for(const path of ['/private/app.sqlite3','/.env','/core/models.py','/.git/config']){const r=await c.request.get(base+path);ok([403,404].includes(r.status()),'source blocked '+path);}
 const cookies=await c.cookies();if(base.startsWith('https:')){ok(cookies.find(x=>x.name==='sessionid')?.secure,'secure session');ok(cookies.find(x=>x.name==='sessionid')?.httpOnly,'HttpOnly session');}
 ok((await c.request.get(base+'/api/state/')).headers()['cache-control'].includes('no-store'),'private no-store');ok(errors.length===0,'browser errors '+errors.join(';'));
 console.log(`PASS ${checks} app public checks on ${base}`);
}finally{await b.close();}
