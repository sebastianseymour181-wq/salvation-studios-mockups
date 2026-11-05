/* Read-only layout regression: never sends an enquiry, even if a test regresses. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.SALVATION_QA_BASE_URL || 'http://127.0.0.1:8774';
const target = process.env.SALVATION_QA_PATH || '/google-ads.html';
const out = '.qa/landing-form-alignment';
fs.mkdirSync(out, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const width of [1440, 1024, 390, 320]) {
      const context = await browser.newContext({ viewport: { width, height: 1000 } });
      // Abort non-read requests, including either enquiry endpoint.
      await context.route('**/*', route => ['GET', 'HEAD'].includes(route.request().method())
        ? route.continue() : route.abort());
      try {
        const page = await context.newPage();
        await page.goto(base + target);
        await page.getByRole('button', { name: 'Reject optional', exact: true }).first().click();
        await page.evaluate(() => document.fonts.ready);
        await page.locator('.ss-landing-extra summary').click();
        const controls = await page.locator('#google-ads-enquiry-form .form-field input:not([tabindex="-1"]), #google-ads-enquiry-form .form-field select').evaluateAll(elements =>
          elements.map(element => {
            const box = element.getBoundingClientRect();
            const label = document.querySelector(`label[for="${element.id}"]`).getBoundingClientRect();
            return { id: element.id, top: box.top, left: box.left, right: box.right, height: box.height, labelGap: box.top - label.bottom };
          }));
        for (const control of controls) {
          assert.ok(control.height >= 44, `${width}: ${control.id} tap target`);
          assert.ok(Math.abs(control.height - controls[0].height) < 1, `${width}: ${control.id} height`);
          assert.ok(Math.abs(control.labelGap - 8) < 1, `${width}: ${control.id} label gap`);
          assert.ok(control.left >= 0 && control.right <= width, `${width}: ${control.id} horizontal fit`);
        }
        if (width > 980) {
          const service = controls.find(control => control.id === 'ss-landing-service');
          const dates = controls.find(control => control.id === 'ss-landing-dates');
          assert.ok(Math.abs(service.top - dates.top) < 1, `${width}: service/date top edges`);
        }
        const service = page.locator('#ss-landing-service');
        await service.focus();
        await service.press('End');
        assert.equal(await service.inputValue(), 'Live Video & Other Projects');
        assert.equal(await service.evaluate(element => getComputedStyle(element).outlineStyle), 'solid');
        await page.locator('#google-ads-enquiry-form').screenshot({ path: `${out}/${width}.png` });
        results.push({ width, controls, keyboardSelect: true });
      } finally {
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
  fs.writeFileSync(`${out}/results.json`, JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
})().catch(error => { console.error(error); process.exitCode = 1; });
