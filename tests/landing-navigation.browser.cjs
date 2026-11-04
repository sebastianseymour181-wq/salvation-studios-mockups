/* Cross-browser regression for EasyList cosmetic false positives.
 * Source: https://github.com/easylist/easylist/blob/master/easylist/easylist_general_hide.txt
 * The real rules ##.ads-header and ##.ads-section previously hid our site content.
 * Injecting their CSS tests the same hiding behaviour without changing a user's extensions.
 */
const { firefox, chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.SALVATION_QA_BASE_URL || 'http://127.0.0.1:8774';
const target = process.env.SALVATION_QA_PATH || '/google-ads.html';
const out = '.qa/firefox-scroll-2026-11-04';fs.mkdirSync(out,{recursive:true});
(async()=>{
 const results=[];
 for(const engine of ['firefox','chromium']){
  const browser=await (engine==='firefox'?firefox.launch({headless:true}):chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']}));
  try{
   for(const width of [1440,390])for(const filtered of [false,true]){
    const context=await browser.newContext({viewport:{width,height:1000}});
    if(base.startsWith('http://127.0.0.1')) await context.route('**/privacy/',r=>r.fulfill({status:200,contentType:'text/html',body:fs.readFileSync('privacy.html','utf8')}));
    const page=await context.newPage();await page.goto(base+target);
    await page.getByRole('button',{name:'Reject optional',exact:true}).first().click();await page.evaluate(()=>document.fonts.ready);
    if(filtered)await page.addStyleTag({content:'.ads-header, .ads-section {display:none!important;}'});
    assert.equal(await page.locator('.ss-landing-section:visible').count(),6);
    assert.equal(await page.locator('#enquiry').isVisible(),true);
    assert.equal(await page.locator('.ss-landing-header .nav-cta').isVisible(),true);
    const initial=await page.evaluate(()=>({height:innerHeight,scrollHeight:document.documentElement.scrollHeight}));
    assert.ok(initial.scrollHeight>initial.height*3);
    await page.mouse.move(width/2,500);await page.mouse.wheel(0,650);
    await page.waitForFunction(()=>scrollY>100);
    const wheel=await page.evaluate(()=>scrollY);
    const links=[['.ss-landing-hero .btn-primary','enquiry'],['.ss-landing-hero .ss-landing-text-link','studio'],['.ss-landing-header .nav-cta','enquiry'],['.ss-landing-closing .btn-primary','enquiry']];
    if(width===1440)links.push(['.ss-landing-header a[href="#services"]','services'],['.ss-landing-header a[href="#studio"]','studio']);
    for(const [selector,id] of links){
     await page.locator(selector).click();
     await page.waitForFunction(id=>{const r=document.getElementById(id).getBoundingClientRect();return location.hash==='#'+id&&r.height>0&&Math.abs(r.top-parseFloat(getComputedStyle(document.getElementById(id)).scrollMarginTop))<3&&r.bottom>80},id);
     assert.ok(await page.evaluate(()=>scrollY)>100);
    }
    await page.locator('.ss-landing-header .nav-cta').click();
    await page.waitForFunction(()=>location.hash==='#enquiry'&&Math.abs(document.getElementById('enquiry').getBoundingClientRect().top-parseFloat(getComputedStyle(document.getElementById('enquiry')).scrollMarginTop))<3);
    if(engine==='firefox'&&filtered){
     await page.screenshot({path:out+'/after-firefox-'+width+'-enquiry.png'});
     await page.locator('.ss-landing-header a[href="#services"]').isVisible().then(async visible=>{if(visible)await page.locator('.ss-landing-header a[href="#services"]').click();else await page.evaluate(()=>document.getElementById('services').scrollIntoView())});
     await page.waitForFunction(()=>Math.abs(document.getElementById('services').getBoundingClientRect().top-parseFloat(getComputedStyle(document.getElementById('services')).scrollMarginTop))<3);
     await page.locator('#services img').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>null))));
     await page.screenshot({path:out+'/after-firefox-'+width+'-services.png'});
    }
    await page.locator('.ss-landing-footer a[href="/privacy/"]').click();
    await page.waitForURL(/\/privacy(?:\/|\.html)?$/);
    assert.ok(await page.getByRole('heading',{name:'Your cookie choices',exact:true}).isVisible()||await page.locator('#privacy-cookies').count());
    results.push({engine,width,easylistRulesApplied:filtered,visibleSections:6,wheelScroll:wheel,anchorLinksChecked:links.length,privacyLink:true});
    await context.close();
   }
  }finally{await browser.close()}
 }
 fs.writeFileSync(out+'/navigation-results.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
