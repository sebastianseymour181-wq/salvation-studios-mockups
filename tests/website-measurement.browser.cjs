/* Run with NODE_PATH pointing to an installed Playwright package; no build dependency. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = process.env.SALVATION_QA_BASE_URL || 'http://127.0.0.1:8774';
const out = path.resolve('.qa/ads-upgrade-2026-11-04'); fs.mkdirSync(out, { recursive: true });
const tracking = /(?:googletagmanager\.com|google-analytics\.com|googleadservices\.com|doubleclick\.net|googlesyndication\.com)/;
const consentSignals = page => page.evaluate(() => (window.dataLayer || []).filter(x => x[0] === 'consent').map(x => ({ action:x[1],state:x[2] })));
const events = page => page.evaluate(() => window.dataLayer.filter(x => x.event));
const results = [];
(async () => {
 const browser = await chromium.launch({ executablePath:'/usr/bin/chromium', headless:true, args:['--no-sandbox'] });
 async function context(options = {}) {
  const c = await browser.newContext({viewport:{width:1440,height:1000},...options});
  const requests = [];
  await c.route('**/*', async route => {
   if (tracking.test(route.request().url())) { requests.push(route.request().url()); return route.fulfill({status:200,contentType:'application/javascript',body:'/* QA: Google tracking intercepted. */'}); }
   return route.continue();
  });
  return {c, requests, p:await c.newPage()};
 }
 try {
  // Fresh, reject and granular choices: no Google tracking before consent.
  let {c,p,requests}=await context();
  await p.goto(base+'/google-ads.html?utm_source=google&utm_campaign=QA_november&gclid=QA_123');
  await p.locator('.ss-cookie-banner').waitFor(); await p.waitForTimeout(200);
  assert.equal(requests.length,0); assert.equal(await p.evaluate(()=>sessionStorage.getItem('salvation_campaign_v1')),null);
  assert.equal((await consentSignals(p))[0].state.ad_storage,'denied');
  await p.screenshot({path:out+'/01-desktop-cookie-banner.png'});
  await p.getByRole('button',{name:'Reject optional',exact:true}).first().click();
  assert.equal(requests.length,0); await p.getByRole('button',{name:'Cookie settings',exact:true}).click();
  assert.equal(await p.locator('#cookie-analytics').isChecked(),false); assert.equal(await p.locator('#cookie-advertising').isChecked(),false);
  await p.locator('#cookie-analytics').check(); await p.getByRole('button',{name:'Save preferences',exact:true}).click();
  await p.waitForTimeout(150); assert.equal(requests.filter(x=>x.includes('/gtm.js?id=GTM-TKKWMVXR')).length,1);
  let last=(await consentSignals(p)).at(-1).state; assert.equal(last.analytics_storage,'granted');assert.equal(last.ad_storage,'denied');
  let attr=await p.evaluate(()=>SalvationConsent.getAttribution());assert.equal(attr.utm_source,'google');assert.equal(attr.gclid,undefined);
  await p.goto(base+'/about.html');assert.equal(await p.locator('.ss-cookie-banner').isVisible(),false);assert.equal((await p.evaluate(()=>SalvationConsent.getAttribution())).utm_campaign,'QA_november');
  await c.close(); results.push('Fresh/reject/granular/persistence: PASS');

  // Full acceptance, backward-compatible lead metadata, canonical success event, no PII.
  ({c,p,requests}=await context());
  await p.goto(base+'/google-ads.html?utm_source=google&utm_campaign=QA_november&gclid=QA_123');
  await p.getByRole('button',{name:'Accept all',exact:true}).click();
  let payload;
  await p.route('**/api/enquiry',async route=>{payload=route.request().postDataJSON();await route.fulfill({status:503,contentType:'application/json',body:'{"ok":false,"error":"QA delivery failure"}'});});
  await p.locator('.ss-landing-hero .btn-primary').click();
  await p.locator('#ss-landing-name').fill('QA Person Not Sent');await p.locator('#ss-landing-email').fill('qa-person@example.invalid');await p.locator('#ss-landing-message').fill('QA project text must never enter dataLayer.');
  await p.locator('.ss-landing-extra summary').click();await p.locator('#ss-landing-room').selectOption('Main studio');await p.locator('#ss-landing-support').selectOption('Dry hire');await p.locator('#ss-landing-duration').fill('Two days');
  await p.locator('button[type=submit]').click();await p.locator('.form-status').filter({hasText:'QA delivery failure'}).waitFor();
  assert.equal((await events(p)).filter(x=>x.event==='salvation_enquiry_submit').length,0);assert.equal(await p.locator('#ss-landing-name').inputValue(),'QA Person Not Sent');
  await p.unroute('**/api/enquiry');await p.route('**/api/enquiry',route=>route.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'}));
  await p.locator('button[type=submit]').click();await p.locator('.form-status').filter({hasText:'Thanks.'}).waitFor();
  let lead=(await events(p)).filter(x=>x.event==='salvation_enquiry_submit');assert.equal(lead.length,1);assert.equal(lead[0].site_environment,'test');assert.equal(lead[0].form_id,'google-ads-enquiry-form');assert.ok(lead[0].event_id);
  assert.match(payload.message,/Preferred room: Main studio/);assert.match(payload.message,/Approximate duration: Two days/);assert.match(payload.message,/utm_campaign: QA_november/);assert.match(payload.message,/gclid: QA_123/);
  const layer=await p.evaluate(()=>JSON.stringify(dataLayer));for(const value of ['QA Person Not Sent','qa-person@example.invalid','QA project text'])assert.equal(layer.includes(value),false);
  await p.screenshot({path:out+'/02-enquiry-success-mocked.png'});
  // Withdrawal is persisted before a reload, clears accessible first-party cookies and stops new GTM loads.
  await c.addCookies([{name:'_ga',value:'QA-cookie',url:base},{name:'_gcl_au',value:'QA-cookie',url:base}]);
  const oldCount=requests.length;
  await p.getByRole('button',{name:'Cookie settings',exact:true}).click();await p.getByRole('button',{name:'Reject optional',exact:true}).last().click();
  await p.waitForLoadState('load');await p.waitForTimeout(250);
  assert.equal((await c.cookies()).some(x=>/^_ga|^_gcl_/.test(x.name)),false);assert.equal(requests.length,oldCount);assert.equal(await p.evaluate(()=>sessionStorage.getItem('salvation_campaign_v1')),null);
  assert.deepEqual(await p.evaluate(()=>SalvationConsent.getState()),{analytics:false,advertising:false});
  await c.close();results.push('Accepted enquiry, attribution, recovery, no PII, withdrawal: PASS (intercepted responses; no real leads sent)');

  // A real successful response without optional consent never queues a measurement event.
  ({c,p}=await context());await p.goto(base+'/google-ads.html');await p.getByRole('button',{name:'Reject optional',exact:true}).first().click();await p.route('**/api/enquiry',route=>route.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'}));
  await p.locator('#ss-landing-name').fill('No tracking QA');await p.locator('#ss-landing-email').fill('qa@example.invalid');await p.locator('#ss-landing-message').fill('No tracking');await p.locator('button[type=submit]').click();await p.locator('.form-status').filter({hasText:'Thanks.'}).waitFor();assert.equal((await events(p)).some(e=>e.event==='salvation_enquiry_submit'),false);await c.close();results.push('Enquiry without tracking consent: PASS');

  // Verify installation/usable preferences on every shipped HTML page, including campaigns.
  function htmlFiles(dir='.') { return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=> e.isDirectory() ? (['.git','.qa','.vercel','node_modules'].includes(e.name)?[]:htmlFiles(path.join(dir,e.name))) : e.name.endsWith('.html')?[path.join(dir,e.name)]:[]); }
  ({c,p,requests}=await context());
  for(const file of htmlFiles()){await p.goto(base+'/'+file.replaceAll(path.sep,'/'),{waitUntil:'domcontentloaded'});await p.locator('.ss-cookie-settings').waitFor();assert.equal(await p.locator('script[data-gtm-container]').count(),1);assert.equal(await p.locator('.ss-cookie-banner').isVisible(),true);}
  assert.equal(requests.length,0);await c.close();results.push('All 36 HTML pages: consent UI/installation and no pre-consent tracking requests PASS');

  // Mobile and tablet reflow plus actual touch-input scrolling.
  for(const width of [320,375,390,768,1024,1440]){
   ({c,p}=await context({viewport:{width,height:844},isMobile:width<760,hasTouch:width<760}));await p.goto(base+'/google-ads.html');await p.evaluate(()=>document.fonts.ready);
   if(width===390)await p.screenshot({path:out+'/03-mobile-cookie-banner.png'});
   await p.getByRole('button',{name:'Reject optional',exact:true}).first().click();
   assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth),width);assert.equal(await p.locator('.ss-landing-header .nav-cta').isVisible(),true);
   if(width===390){const cd=await c.newCDPSession(p);await cd.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:190,y:700}]});for(let y=680;y>=220;y-=20){await cd.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:190,y}]});await p.waitForTimeout(16)}await cd.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await p.waitForTimeout(300);assert.ok(await p.evaluate(()=>scrollY)>0);}
   await p.locator('.ss-landing-header .nav-cta').click();await p.waitForTimeout(500);assert.equal(await p.evaluate(()=>location.hash),'#enquiry');
   if(width===390){await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(500);await p.locator('.ss-landing-hero-image img').evaluate(e=>e.decode());await p.screenshot({path:out+'/04-mobile-hero.png'});await p.getByRole('button',{name:'Cookie settings',exact:true}).click();await p.screenshot({path:out+'/05-mobile-preferences.png'});}
   results.push({width,formY:await p.locator('form').evaluate(e=>e.getBoundingClientRect().top+scrollY),height:await p.evaluate(()=>document.documentElement.scrollHeight)});await c.close();
  }
  fs.writeFileSync(path.join(out,'browser-results.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));
 } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1});
