'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const read = file => fs.readFileSync(path.join(__dirname, '..', file), 'utf8');
const html = read('google-ads.html');
const css = read('google-ads.css');
const script = read('google-ads.js');
const text = html.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ');

test('landing revision keeps hero, enquiry, compact services, one studio and testimonials in order', () => {
  const sections = [...html.matchAll(/<section class="ss-landing-(?:section )?([^\"]+)"/g)].map(m => m[1]);
  assert.deepEqual(sections, ['hero', 'ss-landing-enquiry', 'ss-landing-services', 'ss-landing-intro', 'ss-landing-testimonials', 'ss-landing-closing']);
  assert.doesNotMatch(html, /id="planning-title"|id="spaces-title"|ss-landing-pillars/);
  assert.match(html, /<h2 id="services-title">Studio <em>services\.<\/em><\/h2>/);
  assert.equal((html.match(/<article class="ss-landing-service">/g) || []).length, 4);
  assert.match(html, /href="#services">Learn more about the studio \+ services/);
});

test('approved copy and all original tracking targets remain', () => {
  for (const copy of [
    'A world-class recording studio in Brighton.',
    "Exceptional acoustics, world-class analogue equipment and inspiring creative spaces. Whether you're an established artist or an emerging musician, Salvation offers the space, facilities and support to bring your ideas to life. From full-band recording to production, mixing and writing, we're here to help you make something special.",
    'The studio of choice for Wet Leg, David Gilmour, Fontaines D.C., Skindred, shame and many independent and unsigned artists.',
    "Set within a beautifully restored historic building, Salvation Studios offers a unique setting to make music. With its characterful spaces, vaulted ceilings and relaxed atmosphere, it's somewhere to step away from everyday distractions, work creatively and really get into your music.",
    "Whether you're recording your first single or your next album, you'll find a welcoming environment where artists can feel at home and focus on what matters most – making music.",
    'Come and spend some time by the beach in sunny Brighton.',
  ]) assert.ok(text.includes(copy), copy);
  for (const target of ['header', 'hero', 'services', 'studio', 'closing']) assert.equal((html.match(new RegExp(`data-analytics="ads-${target}-enquiry"`, 'g')) || []).length, 1);
  for (const target of ['email', 'phone']) assert.match(html, new RegExp(`data-analytics="ads-${target}"`));
  assert.match(html, /name="robots" content="noindex, nofollow"/);
  assert.match(html, /data-gtm-container="GTM-TKKWMVXR"/);
  assert.match(html, /id="google-ads-enquiry-form" class="enquiry-form" action="\/api\/enquiry" method="post"/);
  assert.match(html, /<label for="ss-landing-service">What can we help you create\?<\/label>/);
  assert.match(html, /name="form_started_at"/);
  assert.match(html, /name="website" tabindex="-1" autocomplete="off"/);
});

test('artist list is unique, duplicated only for animation and has static fallbacks', () => {
  const lists = [...html.matchAll(/<ul class="ss-landing-artist-list[^\"]*"[^>]*>(.*?)<\/ul>/gs)];
  assert.equal(lists.length, 2);
  assert.equal(lists[0][1], lists[1][1]);
  const artists = [...lists[0][1].matchAll(/<li>(.*?)<\/li>/g)].map(m => m[1]);
  assert.equal(artists.length, 35);
  assert.equal(new Set(artists).size, artists.length);
  assert.match(lists[1][0], /aria-hidden="true"/);
  assert.match(html, /aria-controls="artist-credits-track" hidden>Pause artist credits/);
  assert.match(css, /\.ss-landing-artist-list-copy \{ display: none; \}/);
  assert.match(css, /@media \(prefers-reduced-motion: reduce\)/);
  assert.doesNotMatch(lists[0][1], /Led Zeppelin|David Bowie|Bob Marley|Pink Floyd/);
});

function harness(reduced = false, options = {}) {
  const classes = new Set();
  const button = { hidden: true, textContent: '', addEventListener(type, fn) { this[type] = fn; } };
  const credits = { classList: { toggle(name, value) { value ? classes.add(name) : classes.delete(name); } }, querySelector() { return button; } };
  const motion = { matches: reduced, addEventListener(type, fn) { this.change = fn; } };
  const context = { document: { querySelector() { return options.noCredits ? null : credits; } }, window: { matchMedia: options.noMatchMedia ? undefined : () => motion } };
  vm.runInNewContext(script, context);
  return { classes, button, motion };
}

test('credits enhance with a working pause/resume control and respect motion preference changes', () => {
  const { classes, button, motion } = harness();
  assert.equal(button.hidden, false);
  assert.ok(classes.has('is-animated'));
  button.click(); assert.ok(classes.has('is-paused')); assert.equal(button.textContent, 'Resume artist credits');
  button.click(); assert.equal(classes.has('is-paused'), false); assert.equal(button.textContent, 'Pause artist credits');
  motion.matches = true; motion.change(); assert.equal(classes.has('is-animated'), false); assert.equal(button.hidden, true);
  motion.matches = false; motion.change(); assert.ok(classes.has('is-animated')); assert.equal(button.hidden, false);
});

test('reduced motion and unsupported/no-credits pages stay safely static', () => {
  const { classes, button } = harness(true);
  assert.equal(classes.has('is-animated'), false); assert.equal(button.hidden, true);
  assert.equal(harness(false, { noMatchMedia: true }).classes.size, 0);
  assert.doesNotThrow(() => harness(false, { noCredits: true }));
});
