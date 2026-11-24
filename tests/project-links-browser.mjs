import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const {chromium}=createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE||'/home/mathis/openclaw-workspace/option-pricing-workbench/web/node_modules/playwright-core');
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.APP_URL||'https://app-electromobility.mclement.ch/');
 // Explicit public fictional persona: no bookings, household or invoice mutations.
 await page.getByRole('button',{name:/Explore as Sam/}).click();
 await page.waitForSelector('#project-finance-link');
 assert.equal(await page.locator('#project-finance-link').getAttribute('href'),'https://website-electromobility.mclement.ch/finanzen/');
 assert.equal(await page.locator('#project-presentation-link').getAttribute('href'),'https://website-electromobility.mclement.ch/praesentation/');
 await page.setViewportSize({width:360,height:900});
 await page.getByRole('button',{name:'More',exact:true}).click();
 const dialog=page.locator('#app-dialog');await dialog.waitFor({state:'visible'});
 assert.equal(await dialog.getByRole('link',{name:/Financial scenarios/}).getAttribute('href'),'https://website-electromobility.mclement.ch/finanzen/');
 assert.equal(await dialog.getByRole('link',{name:/Project presentation/}).getAttribute('href'),'https://website-electromobility.mclement.ch/praesentation/');
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 assert.deepEqual(errors,[]);
 console.log('PASS live app project links: desktop, mobile More, destinations, reflow; no business-data mutations');
}finally{await browser.close();}
