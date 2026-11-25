import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/home/mathis/openclaw-workspace/option-pricing-workbench/web/node_modules/playwright-core');
const base=process.env.BASE_URL||'http://127.0.0.1:18929';
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--renderer-process-limit=2']});
let checks=0;const ok=(v,m)=>{assert.ok(v,m);checks++;};
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const assetResponse=await page.request.get(base+'/presentation-data.json');ok(assetResponse.ok(),'slide manifest available');const data=await assetResponse.json();
 ok(data.slides.length===51,'all 51 original slides are in the manifest');
 assert.deepEqual(data.slides.filter(s=>s.hidden).map(s=>s.number),[8,13,23]);checks++;
 const waitArtwork=()=>page.locator('.deck-artwork').evaluate(async img=>{await img.decode();return img.naturalWidth>0&&img.naturalHeight>0;});
 const jump=async i=>{await page.locator('[data-action="overview"]').click();await page.locator(`[data-slide-jump="${i}"]`).click();await waitArtwork();};
 await page.goto(base+'/finanzen/');await page.waitForSelector('[data-finance-key="subscription"]');
 ok((await page.locator('.finance-kpis').innerText()).includes('15’900'),'Zurich baseline matches original case');
 const chart=await page.locator('.finance-chart').innerHTML();
 await page.locator('[data-finance-key="subscription"]').fill('35');
 ok((await page.locator('.finance-kpis').innerText()).includes('23’100'),'subscription updates financial result');
 ok(chart!==await page.locator('.finance-chart').innerHTML(),'financial chart changes live');
 await page.locator('[data-finance-key="subscription"]').fill('-1');ok(await page.locator('[data-finance-key="subscription"]').getAttribute('aria-invalid')==='true','negative subscription rejected');
 await page.locator('[data-finance-key="subscription"]').fill('35');await page.reload();await page.waitForSelector('[data-finance-key="subscription"]');ok(await page.locator('[data-finance-key="subscription"]').inputValue()==='35','scenario persists');
 await page.goto(base+'/praesentation/');await page.waitForFunction(()=>window.voltoPresentationReady);
 ok(await page.locator('.deck-overview [data-slide-jump]').count()===51,'all 51 slides selectable');
 assert.deepEqual(await page.locator('.deck-overview-group').evaluateAll(groups=>groups.map(g=>g.querySelectorAll('button').length)),[17,34]);checks++;
 ok(await page.locator('.deck-overview small').count()===3,'original hidden slides are labelled');
 for(let i=0;i<data.slides.length;i++){
  await jump(i);const s=data.slides[i];
  ok(await page.locator('.deck-slide').getAttribute('data-slide')===String(i),'select slide '+(i+1));
  ok(await page.locator('.deck-artwork').getAttribute('src')===s.image,'correct rendered artwork '+(i+1));
  ok(await waitArtwork(),'artwork decodes '+(i+1));
  const bounds=await page.locator('.deck-stage').evaluate(e=>{const a=e.querySelector('img').getBoundingClientRect(),b=e.getBoundingClientRect();return {inside:a.left>=b.left-1&&a.right<=b.right+1&&a.top>=b.top-1&&a.bottom<=b.bottom+1,ratio:a.width/a.height};});
  ok(bounds.inside&&Math.abs(bounds.ratio-16/9)<.01,'uncropped 16:9 artwork '+(i+1));
  assert.deepEqual(await page.locator('.deck-reading>p').allTextContents(),s.text,'accessible original text '+(i+1));checks++;
  ok(await page.locator('.deck-reading table').count()===(s.charts||[]).length,'chart tables available '+(i+1));
  for(let c=0;c<(s.charts||[]).length;c++){
   const rows=await page.locator('.deck-reading table').nth(c).locator('tbody tr').allTextContents();
   ok(rows.length===s.charts[c].series.length,'every chart series retained '+(i+1));
  }
  if(process.env.SCREENSHOTS&&[0,2,4,7,8,12,13,14,16,43,50].includes(i))await page.locator('.deck-stage').screenshot({path:`/tmp/volto-redesign-slide-${String(i+1).padStart(2,'0')}.png`});
 }
 ok(data.slides[12].charts[0].series.length===3,'charging chart retains all three source series');
 await jump(12);await page.locator('[data-action="read"]').click();
 ok(await page.locator('.deck-reading').isVisible(),'read mode opens');
 ok(await page.locator('.deck-reading table tbody tr').count()===3,'readable charging chart includes limit series');
 await page.locator('[data-action="read"]').click();ok(!(await page.locator('.deck-reading').isVisible()),'read mode closes');
 await jump(13);const originalArtwork=await page.locator('.deck-artwork').getAttribute('src');
 await page.locator('[data-action="finance"]').click();
 ok(await page.locator('.deck-lab').isVisible(),'in-presentation live scenario opens');
 ok(await page.locator('[data-finance-key="subscription"]').inputValue()==='35','financial page shares saved assumptions with lab');
 ok((await page.locator('.deck-lab-heading').innerText()).includes('ERGÄNZUNG ZUR ORIGINALFOLIE'),'lab distinguishes experiments from original slides');
 await page.locator('[data-finance-key="subscription"]').focus();await page.keyboard.press('ArrowRight');ok(await page.locator('.deck-slide').getAttribute('data-slide')==='13','input arrows do not navigate slides');
 const labChart=await page.locator('.deck-lab .finance-chart').innerHTML();
 await page.locator('[data-finance-key="subscription"]').fill('15');
 ok((await page.locator('.deck-lab .finance-kpis').innerText()).includes('8’700'),'lab recalculates financial output');
 ok(labChart!==await page.locator('.deck-lab .finance-chart').innerHTML(),'lab chart updates live');
 ok(await page.locator('.deck-artwork').getAttribute('src')===originalArtwork,'experiments leave source slide unchanged');
 ok(await page.locator('[data-action="finance-close"]').isVisible(),'live scenario has return control');
 await page.locator('[data-finance-reset]').click();ok(await page.locator('[data-finance-key="subscription"]').inputValue()==='25','reset restores original assumptions');
 await page.keyboard.press('Escape');ok(!(await page.locator('.deck-lab').isVisible()),'escape closes lab');
 ok(await page.locator('.deck-stage').evaluate(e=>e===document.activeElement),'lab close returns focus to original slide');
 await page.locator('[data-action="fullscreen"]').click();ok(await page.locator('.deck').evaluate(e=>e.classList.contains('deck-expanded')),'fullscreen enters');
 await page.locator('.deck-stage').focus();await page.keyboard.press('ArrowLeft');ok(await page.locator('.deck-slide').getAttribute('data-slide')==='12','fullscreen keyboard navigates');
 await page.keyboard.press('Home');ok(await page.locator('.deck-slide').getAttribute('data-slide')==='0','Home selects first slide');
 await page.keyboard.press('End');ok(await page.locator('.deck-slide').getAttribute('data-slide')==='50','End reaches final original slide');
 await page.locator('[data-action="finance"]').click();ok(await page.locator('.deck-lab').isVisible(),'finance lab also works fullscreen');
 await page.keyboard.press('Escape');ok(await page.locator('.deck').evaluate(e=>e.classList.contains('deck-expanded')),'first Escape closes lab without leaving fullscreen');
 await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('.deck').classList.contains('deck-expanded'));ok(!(await page.locator('.deck').evaluate(e=>e.classList.contains('deck-expanded'))),'second Escape exits fullscreen');
 for(const width of [360,768,1440]){
  await page.setViewportSize({width,height:1000});
  for(const route of ['/finanzen/','/praesentation/','/']){
   await page.goto(base+route);await page.waitForSelector(route==='/finanzen/'?'.finance-chart':'.deck-artwork');
   ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),route+' fits width '+width);
   if(route!=='/finanzen/'){
    ok(await waitArtwork(),'embedded artwork loads '+route+' '+width);
    await page.locator('[data-action="read"]').click();
    ok(await page.locator('.deck-reading').isVisible(),'read mode available '+route+' '+width);
    ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'read mode no horizontal overflow '+route+' '+width);
    await page.locator('[data-action="read"]').click();
    await page.locator('[data-action="finance"]').click();
    ok(await page.locator('[data-finance-key="subscription"]').isVisible(),'lab controls visible '+route+' '+width);
    ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'lab no horizontal overflow '+route+' '+width);
    await page.locator('[data-action="finance-close"]').click();
   }
  }
 }
 await page.goto(base+'/finanzen/');await page.waitForSelector('[data-finance-preset]');await page.locator('[data-finance-preset]').selectOption('cham');
 ok((await page.locator('.finance-kpis').innerText()).includes('17’400'),'Cham baseline investment');
 await page.locator('[data-finance-key="evShare"]').fill('0');ok((await page.locator('.finance-kpis').innerText()).includes('Nicht erreicht'),'zero EV handled');ok(!(await page.locator('.finance').innerText()).match(/NaN|Infinity/),'no invalid numbers');await page.locator('[data-finance-reset]').click();
 await page.setViewportSize({width:1280,height:900});await page.goto(base+'/praesentation/?print=1');await page.waitForFunction(()=>window.voltoPresentationReady);
 ok(await page.locator('.deck-stage').count()===51,'print route retains all 51 slides');
 ok(await page.locator('.deck-artwork').evaluateAll(async images=>(await Promise.all(images.map(async img=>{try{await img.decode();return img.naturalWidth>0;}catch{return false;}}))).every(Boolean)),'all print slide assets decode');
 await page.goto(base+'/praesentation/');await page.waitForFunction(()=>window.voltoPresentationReady);
 for(const ext of ['pdf','pptx']){
  const link=page.locator(`.deck-downloads a[href*=".${ext}"]`);const [download]=await Promise.all([page.waitForEvent('download'),link.click()]);const downloadPath=await download.path();const body=await fs.readFile(downloadPath);
  ok(body.length>20000,ext+' real download nonempty');
  ok(body.subarray(0,ext==='pdf'?4:2).toString()===(ext==='pdf'?'%PDF':'PK'),ext+' actual format');
  ok(download.suggestedFilename()===`VoltoShare-Praesentation.${ext}`,ext+' download filename');
 }
 ok(errors.length===0,'no JavaScript errors: '+errors.join(';'));
 console.log(`PASS ${checks} source-exact presentation/finance browser checks on ${base}`);
}finally{await browser.close();}
