import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/home/mathis/openclaw-workspace/option-pricing-workbench/web/node_modules/playwright-core');
const base=process.env.BASE_URL||'http://127.0.0.1:18929';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--renderer-process-limit=2']});
let checks=0;const ok=(v,m)=>{assert.ok(v,m);checks++;};
try{
const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto(base+'/finanzen/');await page.waitForSelector('[data-finance-key="subscription"]');
ok((await page.locator('.finance-kpis').innerText()).includes('15’900'),'Zurich baseline matches deck');
const chart=await page.locator('.finance-chart').innerHTML();
await page.locator('[data-finance-key="subscription"]').fill('35');
ok((await page.locator('.finance-kpis').innerText()).includes('23’100'),'subscription updates profit');
ok(chart!==await page.locator('.finance-chart').innerHTML(),'chart changes live');
await page.locator('[data-finance-key="subscription"]').fill('-1');ok(await page.locator('[data-finance-key="subscription"]').getAttribute('aria-invalid')==='true','invalid rejected');
await page.locator('[data-finance-key="subscription"]').fill('35');await page.reload();await page.waitForSelector('[data-finance-key="subscription"]');ok(await page.locator('[data-finance-key="subscription"]').inputValue()==='35','scenario persists');
await page.goto(base+'/praesentation/');await page.waitForFunction(()=>window.voltoPresentationReady);
ok(await page.locator('.deck-overview button').count()===18,'18 slides');
for(let i=0;i<18;i++){
 await page.locator('[data-action="overview"]').click();await page.locator(`[data-slide-jump="${i}"]`).click();
 ok(await page.locator('.deck-slide').getAttribute('data-slide')===String(i),'select slide '+i);
 const over=await page.locator('.deck-slide').evaluate(e=>({scroll:e.scrollHeight,height:e.clientHeight,contentBottom:Math.max(...[...e.querySelectorAll('.deck-slide-main > *')].map(n=>n.getBoundingClientRect().bottom)),footerTop:e.querySelector('.deck-slide-bottom').getBoundingClientRect().top}));
 ok(over.scroll<=over.height+2,'slide outer clips '+i+' '+JSON.stringify(over));
 if(![13,17].includes(i))ok(over.contentBottom<=over.footerTop+3,'slide content overlaps footer '+i+' '+JSON.stringify(over));
 if(process.env.SCREENSHOTS){await page.locator('.deck-stage').screenshot({path:`/tmp/volto-slide-${String(i+1).padStart(2,'0')}.png`});}
}
await page.locator('[data-action="overview"]').click();await page.locator('[data-slide-jump="13"]').click();
ok(await page.locator('[data-finance-key="subscription"]').inputValue()==='35','financial page shares with deck');
await page.locator('[data-finance-key="subscription"]').focus();await page.keyboard.press('ArrowRight');ok(await page.locator('.deck-slide').getAttribute('data-slide')==='13','input arrows do not change slides');
await page.locator('[data-action="fullscreen"]').click();ok(await page.locator('.deck').evaluate(e=>e.classList.contains('deck-expanded')),'fullscreen presentation enters');
await page.locator('.deck-stage').focus();await page.keyboard.press('ArrowLeft');ok(await page.locator('.deck-slide').getAttribute('data-slide')==='12','presenter keyboard works');await page.keyboard.press('Escape');await page.waitForTimeout(100);ok(!(await page.locator('.deck').evaluate(e=>e.classList.contains('deck-expanded'))),'escape exits');
await page.locator('[data-action="overview"]').click();await page.locator('[data-slide-jump="13"]').click();await page.locator('[data-finance-reset]').click();
ok(await page.locator('[data-finance-key="subscription"]').inputValue()==='25','reset basis');
for(const width of [360,768,1440]){
 await page.setViewportSize({width,height:1000});
 for(const route of ['/finanzen/','/praesentation/','/']){
  await page.goto(base+route);await page.waitForTimeout(150);
  ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),route+' width '+width);
 }
}
await page.goto(base+'/finanzen/');await page.waitForSelector('[data-finance-preset]');await page.locator('[data-finance-preset]').selectOption('cham');
ok((await page.locator('.finance-kpis').innerText()).includes('17’400'),'Cham baseline investment');
await page.locator('[data-finance-key="evShare"]').fill('0');ok((await page.locator('.finance-kpis').innerText()).includes('Nicht erreicht'),'zeroEV handled');ok(!(await page.locator('.finance').innerText()).match(/NaN|Infinity/),'no invalidnumbers');await page.locator('[data-finance-reset]').click();
if(process.env.SCREENSHOTS){for(const width of [360,1440]){await page.setViewportSize({width,height:1000});await page.goto(base+'/finanzen/');await page.waitForSelector('.finance-chart');await page.screenshot({path:`/tmp/volto-finance-${width}.png`,fullPage:true});}}
await page.setViewportSize({width:1280,height:900});await page.goto(base+'/praesentation/?print=1&baseline=1&export=1');await page.waitForFunction(()=>window.voltoPresentationReady);ok(await page.locator('.deck-stage').count()===18,'print all18slides');
for(const ext of ['pdf','pptx']){const res=await page.request.get(base+`/downloads/VoltoShare-Praesentation.${ext}`);ok(res.ok(),ext+' download exists');const body=await res.body();ok(body.length>20000,ext+' nonempty');ok(body.subarray(0,ext==='pdf'?4:2).toString() ===(ext==='pdf'?'%PDF':'PK'),ext+' actualformat');}
ok(errors.length===0,'no JavaScript errors: '+errors.join(';'));
console.log(`PASS ${checks} finance/presentation browser checks on ${base}`);
}finally{await browser.close();}
