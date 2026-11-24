// Start the staged site first: python3 -m http.server 18929 --bind 127.0.0.1 --directory build/website
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {mkdir} from 'node:fs/promises';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/home/mathis/openclaw-workspace/option-pricing-workbench/web/node_modules/playwright-core');
const output=new URL('../website-src/downloads/VoltoShare-Praesentation.pdf',import.meta.url);
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--renderer-process-limit=2']});
try{
 const page=await browser.newPage({viewport:{width:1280,height:900}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const res=await page.goto((process.env.BASE_URL||'http://127.0.0.1:18929')+'/praesentation/?print=1&baseline=1&export=1');
 if(!res.ok())throw new Error('Staged presentation did not load');
 await page.waitForFunction(()=>window.voltoPresentationReady);
 await page.evaluate(()=>document.fonts.ready);
 if(errors.length)throw new Error(errors.join('\n'));
 const count=await page.locator('.deck-stage').count();if(count!==18)throw new Error('Expected18slides');
 await mkdir(new URL('../website-src/downloads/',import.meta.url),{recursive:true});
 await page.pdf({path:fileURLToPath(output),preferCSSPageSize:true,printBackground:true,tagged:true});
 console.log('Created18-slide baseline PDF: '+fileURLToPath(output));
}finally{await browser.close();}
