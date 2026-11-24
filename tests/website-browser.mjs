import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || '/home/mathis/openclaw-workspace/option-pricing-workbench/web/node_modules/playwright-core');
const base=process.env.BASE_URL || 'http://127.0.0.1:18929';
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']});
let checks=0;function ok(test,label){assert.ok(test,label);checks++;}
try{
 const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const routes=['/','/geschaeftsmodell/','/finanzen/','/praesentation/','/kontakt/','/impressum/','/datenschutz/'];
 for(const route of routes){
  ok((await page.goto(base+route)).ok(),route+' HTTP');await page.evaluate(()=>document.fonts.ready);
  ok(await page.locator('h1').count()===1,route+' one h1');
  for(const width of [320,360,768,1440]){await page.setViewportSize({width,height:1000});ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),route+' no overflow '+width);}
  ok(await page.evaluate(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0)),route+' images loaded');
  if(process.env.SCREENSHOTS){await page.setViewportSize({width:1440,height:1100});await page.screenshot({path:'/tmp/volto-'+(route.split('/')[1]||'home')+'-desktop.png',fullPage:true});await page.setViewportSize({width:360,height:900});await page.screenshot({path:'/tmp/volto-'+(route.split('/')[1]||'home')+'-mobile.png',fullPage:true});}
 }
 await page.goto(base+'/');await page.setViewportSize({width:360,height:900});
 await page.getByRole('button',{name:/Menü/}).click();ok(await page.getByRole('navigation',{name:'Hauptnavigation'}).isVisible(),'menu opens');await page.keyboard.press('Escape');ok(await page.getByRole('button',{name:/Menü/}).getAttribute('aria-expanded')==='false','escape closes');
 ok(await page.locator('#faq').count()===0,'FAQ removed');ok(await page.locator('.closing').count()===0,'closing enquiry removed');ok(await page.locator('#praesentation [data-presentation]').count()===1,'homepage presentation mount');
 await page.goto(base+'/geschaeftsmodell/');ok(await page.locator('#calc-financials').isHidden(),'initial money blank');
 await page.locator('#calc-S').fill('20');ok(await page.locator('#calc-financials').isHidden(),'one blank stays neutral');await page.locator('#calc-R').fill('30');
 for(const [o,a,b]of[['20','200.00','200.00'],['16','80.00','160.00'],['0','-400.00','0.00']]){await page.locator('#calc-O').fill(o);ok((await page.locator('#calc-continue-contribution').textContent()).includes(a),'continue '+o);ok((await page.locator('#calc-pause-contribution').textContent()).includes(b),'pause '+o);}
 const before=await page.locator('#calc-financials').innerText();await page.locator('#calc-P').fill('4');ok(before===await page.locator('#calc-financials').innerText(),'P-independent UI');
 await page.locator('#calc-O').fill('16');await page.locator('#calc-N').fill('10');ok(await page.locator('#calc-O').inputValue()==='16','O retained');ok(await page.locator('#calc-financials').isHidden(),'invalid relation hides money');ok((await page.locator('#calc-O-error').innerText()).includes('selbst'),'adjustment explained');
 await page.locator('#calc-N').fill('20');await page.locator('#calc-S').fill('-1');ok(await page.locator('#calc-financials').isHidden(),'negative rejected');await page.locator('#calc-S').fill('0');await page.locator('#calc-R').fill('0');ok(await page.locator('#calc-financials').isVisible(),'zero accepted');await page.locator('#calc-N').fill('1.5');ok(await page.locator('#calc-N').getAttribute('aria-invalid')==='true','fraction count invalid');
 await page.locator('#calc-N').fill('999999999');await page.locator('#calc-O').fill('999999999');await page.locator('#calc-P').fill('999999999');await page.locator('#calc-S').fill('12345');await page.locator('#calc-R').fill('54321');await page.setViewportSize({width:320,height:900});ok(await page.locator('#calc-rental-income').evaluate(e=>e.scrollWidth<=e.clientWidth+1),'large accepted money wraps');
 await page.goto(base+'/kontakt/');ok(await page.locator('.site-nav .button').evaluate(e=>getComputedStyle(e).color==='rgb(255, 255, 255)'),'active Kontakt contrast');await page.waitForFunction(()=>!document.querySelector('#contact-submit').disabled);await page.locator('#contact-submit').click();ok(await page.locator('#contact-name').getAttribute('aria-invalid')==='true','required inline error');
 await page.locator('#contact-name').fill('Demo Person');await page.locator('#contact-email').fill('demo@example.test');await page.locator('#contact-role').selectOption('landlord');await page.locator('#contact-message').fill('Fiktives Gebäude mit 20 Wohnungen.');
 const storageBefore=await page.evaluate(()=>JSON.stringify({local:{...localStorage},session:{...sessionStorage}}));
 const requests=[];page.on('request',r=>requests.push(r.url()));await page.locator('#contact-submit').click();ok(await page.locator('#contact-result').isVisible(),'honest demo result');ok((await page.locator('#contact-result').innerText()).includes('nicht versendet'),'explicit no send');ok(requests.length===0,'no enquiry network request');ok(await page.evaluate(()=>JSON.stringify({local:{...localStorage},session:{...sessionStorage}}))===storageBefore,'enquiry does not store personal data');ok(await page.locator('#contact-name').inputValue()==='Demo Person','entries preserved');
 // Verify every local link and asset including section targets across pages.
 const urls=new Set();for(const route of routes){await page.goto(base+route);for(const href of await page.locator('[href],[src]').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('href')||n.getAttribute('src')))){if(href?.startsWith('/'))urls.add(href);}}
 for(const href of urls){const url=new URL(href,base);const res=await page.request.get(url.href);ok(res.ok(),'resource '+href);if(url.hash){const body=await res.text();ok(body.includes('id="'+url.hash.slice(1)+'"'),'anchor '+href);}}
 for(const route of ['/geschaeftsmodell','/finanzen','/praesentation','/kontakt','/impressum','/datenschutz'])ok((await page.request.get(base+route)).ok(),'direct route '+route);
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:360,height:900}});const np=await nojs.newPage();await np.goto(base+'/kontakt/');ok(await np.locator('#contact-submit').isDisabled(),'no-JS cannot submit');ok(await np.locator('#contact-form [name]').count()===0,'no native PII field names');await nojs.close();
 // Text enlargement: check responsive content at 200% CSS font zoom.
 await page.goto(base+'/');await page.setViewportSize({width:768,height:1000});await page.addStyleTag({content:'body{zoom:2}'});ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'200% zoom no overflow');
 ok(errors.length===0,'no JS errors: '+errors.join(';'));
 console.log(`PASS ${checks} browser checks on ${base}`);
}finally{await browser.close();}
