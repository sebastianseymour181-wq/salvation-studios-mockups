'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../site-consent.js'), 'utf8');
const ATTR = 'salvation_campaign_v1';
function storage(seed = {}) {
  const values = new Map(Object.entries(seed));
  return { getItem: key => values.get(key) ?? null, setItem: (key, value) => values.set(key, value), removeItem: key => values.delete(key) };
}
function visit(url, session = storage(), allowed = { analytics: true, advertising: true }) {
  const window = { addEventListener() {} };
  const scripts = [];
  vm.runInNewContext(source, {
    window, location: new URL(url), URLSearchParams, Date,
    localStorage: storage({ salvation_cookie_preferences_v1: JSON.stringify({ version: 1, ...allowed, updatedAt: Date.now() }) }),
    sessionStorage: session,
    document: { readyState: 'loading', cookie: '', addEventListener() {}, createElement: () => ({}), head: { appendChild: script => scripts.push(script) } },
  });
  return { api: window.SalvationConsent, dataLayer: window.dataLayer, scripts, session };
}
const plain = value => JSON.parse(JSON.stringify(value));

test('last tagged arrival replaces the whole record, while untagged navigation preserves its landing page', () => {
  const session = storage();
  visit('https://example.test/first/?utm_source=google&utm_campaign=A&gclid=OLD_CLICK', session);
  const next = visit('https://example.test/second/?utm_source=facebook&utm_campaign=B', session);
  assert.deepEqual(plain(next.api.getAttribution()), { utm_source: 'facebook', utm_campaign: 'B', landing_page: '/second/' });
  const untagged = visit('https://example.test/contact/', session);
  assert.deepEqual(plain(untagged.api.getAttribution()), plain(next.api.getAttribution()));
  const clickOnly = visit('https://example.test/third/?gclid=NEW_CLICK', session);
  assert.deepEqual(plain(clickOnly.api.getAttribution()), { gclid: 'NEW_CLICK', landing_page: '/third/' });
});

test('attribution includes only consented categories and never pairs a new forbidden tag with old context', () => {
  const url = 'https://example.test/landing/?utm_source=google&utm_campaign=A&gclid=CLICK&gbraid=BRAID&wbraid=WEB';
  assert.deepEqual(plain(visit(url, storage(), { analytics: true, advertising: false }).api.getAttribution()), { utm_source: 'google', utm_campaign: 'A', landing_page: '/landing/' });
  assert.deepEqual(plain(visit(url, storage(), { analytics: false, advertising: true }).api.getAttribution()), { gclid: 'CLICK', gbraid: 'BRAID', wbraid: 'WEB', landing_page: '/landing/' });
  const session = storage();
  visit(url, session);
  const none = visit('https://example.test/contact/', session, { analytics: false, advertising: false });
  assert.deepEqual(plain(none.api.getAttribution()), {});
  assert.equal(session.getItem(ATTR), null);
  assert.equal(none.scripts.length, 0);
  visit(url, session, { analytics: true, advertising: false });
  const forbiddenArrival = visit('https://example.test/new/?gclid=NEW', session, { analytics: true, advertising: false });
  assert.deepEqual(plain(forbiddenArrival.api.getAttribution()), {});
});

test('tracking is consent gated, returns eligibility, and strips personal fields', () => {
  const denied = visit('https://example.test/', storage(), { analytics: false, advertising: false });
  const before = denied.dataLayer.length;
  assert.equal(denied.api.track('salvation_enquiry_start', { form_id: 'enquiry' }), false);
  assert.equal(denied.dataLayer.length, before);
  const accepted = visit('https://example.test/');
  assert.equal(accepted.api.track('salvation_enquiry_submit', {
    form_id: 'enquiry', source_page: '/contact/', session_type: 'Recording', event_id: 'safe-id',
    name: 'Private Person', email: 'private@example.test', phone: '0123456789', message: 'private project', attribution: { gclid: 'CLICK' },
  }), true);
  assert.deepEqual(plain(accepted.dataLayer.at(-1)), { event: 'salvation_enquiry_submit', form_id: 'enquiry', source_page: '/contact/', session_type: 'Recording', event_id: 'safe-id', site_environment: 'test' });
});

test('invalid campaign values are filtered and returned attribution cannot mutate storage', () => {
  const page = visit('https://example.test/?utm_source=person%40example.test&utm_campaign=clean&gclid=bad%20click');
  assert.deepEqual(plain(page.api.getAttribution()), { utm_campaign: 'clean', landing_page: '/' });
  page.api.getAttribution().utm_campaign = 'changed';
  assert.equal(page.api.getAttribution().utm_campaign, 'clean');
});
