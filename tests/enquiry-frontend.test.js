'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const enquirySource = fs.readFileSync(path.join(__dirname, '../enquiry.js'), 'utf8');
const consentSource = fs.readFileSync(path.join(__dirname, '../site-consent.js'), 'utf8');
function node(tag = 'div') {
  return {
    tag, dataset: {}, style: {}, children: [], handlers: {}, value: '', hidden: false,
    addEventListener(type, fn) { this.handlers[type] = fn; },
    setAttribute(key, value) { this[key] = value; },
    append(...children) { this.children.push(...children); },
    appendChild(child) { this.children.push(child); },
    insertAdjacentElement(position, child) { this.adjacent = child; },
    remove() { this.removed = true; }, focus() { this.focused = true; },
    querySelector() { return node('input'); },
  };
}
function storage(seed = {}) {
  const map = new Map(Object.entries(seed));
  return { getItem: key => map.get(key) ?? null, setItem: (key, value) => map.set(key, value), removeItem: key => map.delete(key) };
}
function harness(options = {}) {
  const status = node(), button = node('button'), startedAt = node('input');
  const values = { name: 'Private Person', email: 'private@example.test', phone: '0123456789', artist_company: 'Private Artist', instagram: '@private', session_type: 'Recording', dates: 'Next month', message: 'Private project details', website: '', ...options.values };
  const fields = Object.fromEntries(Object.keys(values).map(key => [key, node('input')]));
  const form = node('form');
  Object.assign(form, { id: 'campaign-enquiry', resetCount: 0, elements: { namedItem: key => fields[key] },
    querySelector: selector => ({ '.form-status': status, 'button[type="submit"]': button, 'input[name="form_started_at"]': startedAt })[selector],
    reset() { this.resetCount++; },
  });
  const body = node('body'), head = node('head');
  const document = { body, head, cookie: '', readyState: 'loading', handlers: {},
    createElement: node, querySelectorAll: selector => selector === '.enquiry-form' ? [form] : [], querySelector: () => null,
    addEventListener(type, fn) { this.handlers[type] = fn; },
  };
  const location = new URL(options.url || 'https://example.test/google-ads/?utm_source=google&utm_campaign=studio&gclid=CLICK');
  let reloads = 0;
  location.reload = () => { reloads++; };
  const window = { location, addEventListener() {}, crypto: { randomUUID: () => 'safe-event-id' } };
  const calls = [], timers = new Map(), controllers = [];
  const context = {
    window, document, location, URLSearchParams, Date, TextEncoder, crypto: window.crypto,
    localStorage: storage(options.consent === false ? {} : { salvation_cookie_preferences_v1: JSON.stringify({ version: 1, analytics: true, advertising: true, updatedAt: Date.now() }) }), sessionStorage: storage(),
    FormData: class { entries() { return Object.entries({ ...values, form_started_at: startedAt.value }); } get(key) { return values[key]; } },
    AbortController: class { constructor() { this.signal = { aborted: false }; controllers.push(this); } abort() { this.signal.aborted = true; this.signal.onabort?.(); } },
    setTimeout(fn, ms) { const id = timers.size + 1; timers.set(id, { fn, ms }); return id; }, clearTimeout(id) { timers.delete(id); },
    fetch(url, init) { calls.push({ url, init, payload: JSON.parse(init.body) }); return options.fetch ? options.fetch(url, init) : Promise.resolve({ ok: options.httpOk ?? true, json: async () => options.result || { ok: true, received: true, submission_id: 'submission-123' } }); },
  };
  vm.createContext(context);
  vm.runInContext(consentSource, context);
  vm.runInContext(enquirySource, context);
  return { form, status, button, values, fields, calls, timers, controllers, window,
    submit: () => form.handlers.submit({ preventDefault() {} }),
    interact: type => form.handlers[type](),
    accept() { document.handlers.DOMContentLoaded(); body.children[0].handlers.click({ target: { closest: () => ({ dataset: { cookieChoice: 'accept' } }) } }); },
    events: name => window.dataLayer.filter(event => event.event === name),
  };
}
function descendants(element) { return [element, ...(element.children || []).flatMap(descendants)]; }

test('preconsent focus does not consume start; postconsent input records exactly one start with form_id and no PII', async () => {
  const h = harness({ consent: false });
  h.interact('focusin');
  assert.equal(h.events('salvation_enquiry_start').length, 0);
  h.accept();
  assert.equal(h.events('salvation_enquiry_start').length, 0, 'consent must not replay prior interaction');
  h.interact('input'); h.interact('change'); h.interact('focusin');
  assert.equal(h.events('salvation_enquiry_start').length, 1);
  assert.equal(h.events('salvation_enquiry_start')[0].form_id, 'campaign-enquiry');
  await h.submit();
  assert.equal(h.events('salvation_enquiry_submit').length, 1);
  assert.equal(h.events('salvation_enquiry_submit')[0].event_id, 'submission-123');
  const layer = JSON.stringify(h.window.dataLayer);
  for (const key of ['name', 'email', 'phone', 'artist_company', 'instagram', 'message']) assert.ok(!layer.includes(h.values[key]), key + ' must not enter dataLayer');
});

for (const [name, options] of [
  ['HTTP error', { httpOk: false, result: { ok: false, error: 'Rejected' } }],
  ['application error', { result: { ok: false, error: 'Rejected' } }],
  ['filled honeypot', { values: { website: 'spam' } }],
  ['received false', { result: { ok: true, received: false } }],
]) test(name + ' emits no success conversion', async () => {
  const h = harness(options); await h.submit();
  assert.equal(h.events('salvation_enquiry_submit').length, 0);
});

test('4000-character message without optional context or attribution is accepted intact', async () => {
  const message = 'x'.repeat(3998) + '\nZ';
  const h = harness({ consent: false, values: { message } });
  await h.submit();
  assert.equal(h.calls.length, 1);
  assert.equal(h.calls[0].payload.message, message);
  assert.equal(h.calls[0].payload.context_version, undefined);
  assert.equal(h.values.message, message);
});

test('legacy message includes full optional context and consented attribution exactly once within limit', async () => {
  const message = 'Project line one\nProject line two';
  const h = harness({ values: { message, preferred_room: 'Studio One', engineering_support: 'Engineer needed', duration: 'Two days' } });
  await h.submit();
  assert.equal(h.calls.length, 1);
  const payload = h.calls[0].payload;
  assert.ok(payload.message.length <= 4000);
  for (const value of [message, 'Preferred room: Studio One', 'Engineer or support required: Engineer needed', 'Approximate duration: Two days', 'utm_source: google', 'utm_campaign: studio', 'gclid: CLICK', 'landing_page: /google-ads/']) assert.equal(payload.message.split(value).length - 1, 1, value);
  assert.deepEqual(Object.keys(payload).sort(), ['name', 'artist_company', 'instagram', 'email', 'phone', 'session_type', 'dates', 'message', 'source_page', 'form_started_at', 'website'].sort());
  assert.equal(payload.context_version, undefined);
  assert.equal(payload.source_page, '/google-ads/');
  assert.equal(h.values.message, message, 'form input must remain untouched');
});

test('combined message overflow requests the exact reduction, preserves every field and sends nothing', async () => {
  const context = { preferred_room: 'Studio One', engineering_support: 'Engineer needed', duration: 'Two days' };
  const short = harness({ values: { ...context, message: 'X' } });
  await short.submit();
  const overhead = short.calls[0].payload.message.length - 1;
  assert.ok(overhead > 0);
  const message = 'x'.repeat(4000);
  const h = harness({ values: { ...context, message } });
  const before = { ...h.values };
  await h.submit();
  assert.equal(h.calls.length, 0);
  assert.deepEqual(h.values, before);
  assert.equal(h.form.resetCount, 0);
  assert.equal(h.timers.size, 0);
  assert.match(h.status.textContent, /shorten/i);
  assert.match(h.status.textContent, new RegExp('\\b' + overhead + '\\b'));
  assert.equal(h.fields.message.focused, true);
  assert.equal(h.events('salvation_enquiry_submit').length, 0);
});

test('failure offers explicit email draft and complete copyable context without navigation or losing values', async () => {
  const h = harness({ httpOk: false, result: { ok: false, error: 'Email delivery is not configured yet.' }, values: { preferred_room: 'Studio One', engineering_support: 'Engineer needed', duration: 'Two days', message: 'x'.repeat(3000) } });
  const before = h.window.location.href;
  await h.submit();
  assert.equal(h.window.location.href, before);
  assert.equal(h.form.resetCount, 0);
  assert.equal(h.button.disabled, false);
  const children = descendants(h.status.adjacent);
  const link = children.find(child => child.tag === 'a');
  const copy = children.find(child => child.tag === 'textarea');
  assert.match(link.href, /^mailto:info@salvationstudios\.co\.uk\?/);
  const emailBody = new URL(link.href).searchParams.get('body');
  assert.equal(emailBody, copy.value);
  for (const value of [h.values.message, 'Studio One', 'Engineer needed', 'Two days', 'CLICK', 'studio', '/google-ads/']) assert.ok(copy.value.includes(value));
  for (const value of [h.values.message, 'Preferred room: Studio One', 'Engineer or support required: Engineer needed', 'Approximate duration: Two days', 'utm_source: google', 'utm_campaign: studio', 'gclid: CLICK', 'landing_page: /google-ads/']) assert.equal(copy.value.split(value).length - 1, 1, value);
  assert.equal(copy.readOnly, true);
  assert.equal(h.events('salvation_enquiry_error').length, 1);
});

test('timeout aborts once, blocks repeated pending submits, retains values and offers uncertainty guidance without retry', async () => {
  const h = harness({ fetch: (url, init) => new Promise((resolve, reject) => { init.signal.onabort = () => reject(new Error('Aborted')); }) });
  const pending = h.submit();
  assert.equal(h.button.disabled, true);
  await h.submit(); await h.submit();
  assert.equal(h.calls.length, 1);
  assert.equal(h.timers.size, 1);
  const timer = [...h.timers.values()][0];
  assert.equal(timer.ms, 20000);
  timer.fn();
  await pending;
  assert.equal(h.controllers[0].signal.aborted, true);
  assert.equal(h.button.disabled, false);
  assert.equal(h.form.resetCount, 0);
  assert.equal(h.values.message, 'Private project details');
  assert.match(h.status.textContent, /could not confirm delivery/i);
  assert.match(h.status.textContent, /may have arrived/i);
  assert.match(h.status.textContent, /check with the studio before resending/i);
  assert.equal(h.calls.length, 1);
  assert.equal(h.timers.size, 0);
  assert.equal(h.events('salvation_enquiry_submit').length, 0);
});

test('oversize message and optional context stop before any request and focus the field', async () => {
  for (const [key, length] of [['message', 4001], ['preferred_room', 161], ['engineering_support', 161], ['duration', 161]]) {
    const h = harness({ values: { [key]: 'x'.repeat(length) } });
    await h.submit();
    assert.equal(h.calls.length, 0, key);
    assert.equal(h.fields[key].focused, true, key);
    assert.match(h.status.textContent, /Please shorten/);
    assert.equal(h.form.resetCount, 0);
    assert.equal(h.timers.size, 0);
  }
});

test('timeout also aborts a stalled response body and preserves uncertain-delivery guidance', async () => {
  let signalBodyStarted;
  const bodyStarted = new Promise(resolve => { signalBodyStarted = resolve; });
  const h = harness({ fetch: async (url, init) => ({
    ok: true,
    json: () => new Promise((resolve, reject) => {
      init.signal.onabort = () => reject(new Error('Body aborted'));
      signalBodyStarted();
    }),
  }) });
  const pending = h.submit();
  await bodyStarted;
  [...h.timers.values()][0].fn();
  await pending;
  assert.equal(h.controllers[0].signal.aborted, true);
  assert.equal(h.button.disabled, false);
  assert.equal(h.form.resetCount, 0);
  assert.match(h.status.textContent, /may have arrived/i);
  assert.equal(h.calls.length, 1);
  assert.equal(h.events('salvation_enquiry_submit').length, 0);
});

test('successful pending request produces only one conversion and clears its timeout', async () => {
  let resolveRequest;
  const h = harness({ fetch: () => new Promise(resolve => { resolveRequest = resolve; }) });
  const pending = h.submit();
  await h.submit();
  assert.equal(h.calls.length, 1);
  resolveRequest({ ok: true, json: async () => ({ ok: true, received: true, submission_id: 'accepted-once' }) });
  await pending;
  assert.equal(h.form.resetCount, 1);
  assert.equal(h.events('salvation_enquiry_submit').length, 1);
  assert.equal(h.events('salvation_enquiry_submit')[0].event_id, 'accepted-once');
  assert.equal(h.button.disabled, false);
  assert.equal(h.timers.size, 0);
});


test('4000 CJK characters exceeding the legacy UTF8 byte cap are retained and never sent', async () => {
  const message = '界'.repeat(4000);
  assert.equal(message.length, 4000);
  const h = harness({ consent: false, values: { message } });
  const before = { ...h.values };
  await h.submit();
  assert.equal(h.calls.length, 0);
  assert.deepEqual(h.values, before);
  assert.equal(h.form.resetCount, 0);
  assert.equal(h.timers.size, 0);
  assert.match(h.status.textContent, /delivery size limit/i);
  assert.match(h.status.textContent, /nothing has been sent/i);
  assert.match(h.status.textContent, /details have been kept/i);
  assert.equal(h.events('salvation_enquiry_submit').length, 0);
});

test('only the approved test alias uses the non-colliding delivery proxy', async () => {
  for (const [host, expected] of [
    ['salvation-studios-mockups-three.vercel.app', '/test-enquiry-delivery'],
    ['www.salvationstudios.co.uk', '/api/enquiry'],
    ['salvationstudios.co.uk', '/api/enquiry'],
    ['unrelated.vercel.app', '/api/enquiry'],
    ['salvation-studios-mockups-three.vercel.app.example.com', '/api/enquiry'],
  ]) {
    const h = harness({url:'https://' + host + '/google-ads/'});
    await h.submit();
    assert.equal(h.calls.length, 1);
    assert.equal(h.calls[0].url, expected, host);
  }
});

test('test proxy rewrite is exact-host-only and cannot collide with a filesystem function', () => {
  const config = JSON.parse(fs.readFileSync(path.join(__dirname, '../vercel.json'), 'utf8'));
  const route = config.rewrites.find(item => item.source === '/test-enquiry-delivery');
  assert.ok(route);
  assert.equal(route.destination, 'https://www.salvationstudios.co.uk/api/enquiry');
  assert.deepEqual(route.has, [{type:'host', value:'salvation-studios-mockups-three.vercel.app'}]);
  assert.equal(fs.existsSync(path.join(__dirname, '../test-enquiry-delivery.js')), false);
  assert.equal(fs.existsSync(path.join(__dirname, '../test-enquiry-delivery.html')), false);
  assert.ok(config.headers.some(item => item.source === '/test-enquiry-delivery' && item.headers.some(header => header.key === 'Cache-Control' && header.value === 'no-store')));
});
