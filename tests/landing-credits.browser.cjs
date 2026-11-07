/* Read-only browser regression. Blocks all non-read network requests. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.SALVATION_QA_BASE_URL || 'http://127.0.0.1:8774';
const target = process.env.SALVATION_QA_PATH || '/google-ads.html';
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', headless: true, args: ['--no-sandbox'] });
  const results = [];
  try {
    for (const width of [1440, 1024, 768, 390, 320]) {
      const context = await browser.newContext({ viewport: { width, height: 1000 } });
      await context.route('**/*', route => ['GET', 'HEAD'].includes(route.request().method()) ? route.continue() : route.abort());
      const page = await context.newPage();
      await page.goto(base + target);
      await page.getByRole('button', { name: 'Reject optional', exact: true }).first().click();
      await page.evaluate(() => document.fonts.ready);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `${width}: no page overflow`);
      assert.equal(await page.locator('main > section').nth(1).getAttribute('id'), 'enquiry');
      await page.locator('.ss-landing-explore-link').click();
      await page.waitForFunction(() => location.hash === '#services' && Math.abs(document.getElementById('services').getBoundingClientRect().top - parseFloat(getComputedStyle(document.getElementById('services')).scrollMarginTop)) < 3);
      await page.getByRole('button', { name: 'Pause artist credits', exact: true }).click();
      assert.equal(await page.locator('[data-artist-credits]').evaluate(e => e.classList.contains('is-paused')), true);
      await page.getByRole('button', { name: 'Resume artist credits', exact: true }).click();
      assert.equal(await page.locator('[data-artist-credits]').evaluate(e => e.classList.contains('is-paused')), false);
      await page.emulateMedia({ reducedMotion: 'reduce' });
      assert.equal(await page.locator('.ss-landing-credits-toggle').isVisible(), false);
      assert.equal(await page.locator('.ss-landing-artist-list-copy').isVisible(), false);
      assert.equal(await page.locator('.ss-landing-credits-track').evaluate(e => getComputedStyle(e).animationName), 'none');
      assert.equal(await page.locator('.ss-landing-artist-list:not(.ss-landing-artist-list-copy) li:visible').count(), 35);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `${width}: reduced motion no page overflow`);
      fs.mkdirSync('.qa/eliza-revision', { recursive: true });
      await page.screenshot({ path: `.qa/eliza-revision/${width}-reduced-motion.png`, fullPage: true });
      results.push({ width, sectionOrder: true, sidebarLink: true, pauseResume: true, reducedMotion: true, horizontalOverflow: false });
      await context.close();
    }
    const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 320, height: 1000 } });
    await context.route('**/*', route => ['GET', 'HEAD'].includes(route.request().method()) ? route.continue() : route.abort());
    const page = await context.newPage(); await page.goto(base + target);
    assert.equal(await page.locator('.ss-landing-credits-toggle').isVisible(), false);
    assert.equal(await page.locator('.ss-landing-artist-list-copy').isVisible(), false);
    assert.equal(await page.locator('.ss-landing-artist-list:not(.ss-landing-artist-list-copy) li:visible').count(), 35);
    assert.equal(await page.locator('.ss-landing-noscript').isVisible(), true);
    assert.equal(await page.locator('#google-ads-enquiry-form button[type=submit]').isVisible(), false);
    await context.close();
    console.log(JSON.stringify({ results, noJavaScript: true }, null, 2));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
