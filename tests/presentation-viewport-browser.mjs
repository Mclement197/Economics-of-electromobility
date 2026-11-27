import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/home/mathis/openclaw-workspace/option-pricing-workbench/web/node_modules/playwright-core');
const base=process.env.BASE_URL||'http://127.0.0.1:18929';
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--renderer-process-limit=2']});
let checks=0;
const ok=(value,message)=>{assert.ok(value,message);checks++;};
const inViewport=async locator=>locator.evaluate(el=>{const r=el.getBoundingClientRect();return r.width>0&&r.height>0&&r.left>=-1&&r.top>=-1&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1;});
const closeTo=(a,b)=>Math.abs(a-b)<2;
const sizes=[{width:1280,height:720},{width:1440,height:900},{width:1920,height:1080},{width:768,height:1024},{width:360,height:800}].filter(size=>!process.env.VIEWPORT_WIDTHS||process.env.VIEWPORT_WIDTHS.split(',').includes(String(size.width)));
try{
 for(const fallback of [false,true].filter(mode=>!process.env.FULLSCREEN_MODE||process.env.FULLSCREEN_MODE===(mode?'fallback':'native'))){
  const context=await browser.newContext();
  if(fallback)await context.addInitScript(()=>{Element.prototype.requestFullscreen=undefined;});
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const size of sizes){
   const name=`${fallback?'viewport fallback':'native fullscreen'} ${size.width}×${size.height}`;
   await page.setViewportSize(size);await page.goto(base+'/praesentation/',{waitUntil:'domcontentloaded',timeout:60000});
   await page.waitForFunction(()=>window.voltoPresentationReady);
   await page.locator('.deck-artwork').evaluate(img=>img.decode());
   await page.locator('[data-action="fullscreen"]').click();
   await page.waitForFunction(()=>document.querySelector('.deck').classList.contains('deck-expanded'));
   if(!fallback)ok(await page.evaluate(()=>document.fullscreenElement===document.querySelector('.deck')),name+' enters browser fullscreen');
   await page.locator('.deck-stage').focus();await page.mouse.move(size.width/2,size.height/2);
   await page.waitForTimeout(2600);
   const bounds=await page.locator('.deck-stage').boundingBox();
   const expectedWidth=Math.min(size.width,size.height*16/9),expectedHeight=expectedWidth*9/16;
   ok(closeTo(bounds.width,expectedWidth)&&closeTo(bounds.height,expectedHeight),name+' slide uses largest uncropped 16:9 rectangle');
   ok(closeTo(bounds.x,(size.width-expectedWidth)/2)&&closeTo(bounds.y,(size.height-expectedHeight)/2),name+' slide centered');
   ok(await page.locator('.deck').evaluate(el=>el.scrollHeight<=el.clientHeight+1&&el.scrollWidth<=el.clientWidth+1),name+' has no deck scrollbar');
   ok(!(await page.locator('.deck-controls').isVisible()),name+' has no persistent navigation footer');
   ok(!(await page.locator('.deck-toolbar').isVisible()),name+' has no persistent toolbar');
   if(process.env.SCREENSHOTS)await page.screenshot({path:`/tmp/volto-viewport-fullscreen-${fallback?'fallback':'native'}-${size.width}.png`});
   await page.keyboard.press('ArrowRight');ok(await page.locator('.deck-slide').getAttribute('data-slide')==='1',name+' keyboard navigation works with hidden chrome');
   if(size.width===1280){
    await page.mouse.move(size.width/2,size.height-10);await page.locator('[data-action="next"]').click();
    ok(await page.locator('.deck-slide').getAttribute('data-slide')==='2',name+' pointer navigation works');
    await page.mouse.move(size.width/2,size.height/2);await page.waitForTimeout(2600);
    ok(!(await page.locator('.deck-controls').isVisible()),name+' pointer navigation controls hide again');
    await page.keyboard.press('Tab');ok(await page.locator('.deck-toolbar').isVisible(),name+' Tab reveals controls for keyboard access');
    await page.locator('.deck-stage').focus();await page.mouse.move(size.width/2,size.height/2);await page.waitForTimeout(2600);
   }
   if(!process.env.SHELL_ONLY){
   await page.keyboard.press('f');await page.waitForSelector('.deck-lab:not([hidden])');
   ok(await page.locator('.deck-lab iframe').count()===0,name+' live finance is native interactive content');
   ok(await inViewport(page.locator('.deck-lab')),name+' live finance remains within screen');
   const labBefore=await page.locator('.deck-lab').boundingBox();
   await page.locator('[data-finance-reset]').click();
   const beforeChart=await page.locator('.finance-chart').innerHTML();
   await page.locator('[data-finance-key="subscription"]').fill('35');
   ok((await page.locator('.finance-kpis').textContent()).includes('23’100'),name+' subscription changes annual cashflow');
   ok(beforeChart!==await page.locator('.finance-chart').innerHTML(),name+' chart responds immediately');
   const labAfter=await page.locator('.deck-lab').boundingBox();
   ok(closeTo(labBefore.height,labAfter.height)&&closeTo(labBefore.width,labAfter.width),name+' recalculation does not enlarge the slide');
   if(size.width>=1280){
    ok(await inViewport(page.locator('.finance-chart')),name+' full chart is visible');
    ok(await inViewport(page.locator('.finance-kpis')),name+' all financial headline metrics visible');
    const metrics=await page.locator('.finance-kpis').boundingBox(),plot=await page.locator('.finance-chart').boundingBox(),assumptions=await page.locator('.finance-assumptions').boundingBox();
    ok(metrics.y+metrics.height<=plot.y+1,name+' financial headline metrics lead above chart');
    ok(plot.y+plot.height<=assumptions.y+1,name+' controls support chart from below, not a dashboard sidebar');
    const levers=await page.locator('.finance-quick .finance-lever').evaluateAll(els=>els.map(e=>({x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y})));
    ok(levers.length===4&&levers.every((r,i)=>Math.abs(r.y-levers[0].y)<2&&(!i||r.x>levers[i-1].x)),name+' four levers share one horizontal rail');
    for(const key of ['subscription','margin','chargerCost','maintenance'])ok(await inViewport(page.locator(`[data-finance-key="${key}"]`)),name+' quick control '+key+' visible');
   }
   await page.locator('[data-finance-reset]').click();ok(await page.locator('[data-finance-key="subscription"]').inputValue()==='25',name+' baseline reset works');
   await page.locator('[data-finance-preset]').selectOption('cham');
   ok((await page.locator('.finance-kpis').textContent()).includes('17’400'),name+' Cham preset calculates');
   await page.locator('[data-finance-key="evShare"]').fill('0');
   ok((await page.locator('.finance-kpis').textContent()).includes('Nicht erreicht'),name+' zero demand handled');
   ok(!/NaN|Infinity/.test(await page.locator('.finance').textContent()),name+' no invalid values');
   await page.locator('[data-finance-reset]').click();
   if(process.env.SCREENSHOTS)await page.screenshot({path:`/tmp/volto-viewport-live-cham-${fallback?'fallback':'native'}-${size.width}.png`});
   await page.locator('[data-finance-preset]').selectOption('zurich');
   await page.locator('[data-finance-panel="advanced"]').click();
   ok(await page.locator('.finance-advanced').isVisible(),name+' advanced assumptions pane opens');
   const advancedInput=page.locator('.finance-advanced [data-finance-key]').first();
   const initial=await advancedInput.inputValue();await advancedInput.fill(String(Number(initial)+1));
   ok(await advancedInput.inputValue()!==initial,name+' advanced assumptions editable');
   ok(await inViewport(page.locator('.deck-lab')),name+' advanced assumptions do not enlarge slide');
   await page.locator('[data-finance-panel="details"]').click();
   ok(await page.locator('.finance-more').isVisible(),name+' calculation details pane opens');
   ok(await page.locator('.finance-more table').count()>=2,name+' exact financial tables remain available');
   ok(await inViewport(page.locator('.deck-lab')),name+' details do not enlarge slide');
   await page.locator('[data-finance-panel="scenario"]').click();
   await page.locator('[data-finance-reset]').click();
   if(process.env.SCREENSHOTS)await page.screenshot({path:`/tmp/volto-viewport-live-zurich-${fallback?'fallback':'native'}-${size.width}.png`});
   await page.locator('[data-action="finance-close"]').click();await page.locator('.deck-stage').focus();
   }
   await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('.deck').classList.contains('deck-expanded'));
   ok(!await page.evaluate(()=>document.body.classList.contains('deck-is-presenting')),name+' exit restores ordinary page scrolling');
   console.log(`Checked ${name}`);
  }
  ok(errors.length===0,`No script errors (${fallback?'fallback':'native'}): ${errors.join('; ')}`);
  await context.close();
 }
 if(!process.env.SHELL_ONLY){
  const page=await browser.newPage({viewport:{width:1280,height:720}});
  await page.goto(base+'/finanzen/');await page.waitForSelector('[data-finance-key="subscription"]');
  ok(await page.locator('[data-finance-panel]').count()===0,'standalone finance page retains original disclosure layout');
  await page.locator('[data-finance-key="subscription"]').fill('35');
  ok((await page.locator('.finance-kpis').textContent()).includes('23’100'),'standalone finance calculations unaffected');
  await page.locator('.finance-advanced>summary').click();ok(await page.locator('.finance-advanced').evaluate(el=>el.open),'standalone advanced disclosure works');
  await page.locator('.finance-details>summary').click();ok(await page.locator('.finance-details').evaluate(el=>el.open),'standalone details disclosure works');
  await page.close();
 }
 console.log(`PASS ${checks} presentation viewport/interaction checks on ${base}`);
}finally{await browser.close();}
