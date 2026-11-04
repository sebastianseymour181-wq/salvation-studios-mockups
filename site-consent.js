/* Salvation Studios: sitewide consent, GTM and consented session attribution. */
(() => {
  'use strict';
  if (window.SalvationConsent) return;
  const KEY = 'salvation_cookie_preferences_v1';
  const ATTR = 'salvation_campaign_v1';
  const MAX_AGE = 180 * 24 * 60 * 60 * 1000;
  const GTM = 'GTM-TKKWMVXR';
  const campaignKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
  const adKeys = ['gclid', 'gbraid', 'wbraid'];
  const environment = /(^|\.)salvationstudios\.co\.uk$/.test(location.hostname) ? 'production' : 'test';
  const read = (storage, key) => { try { return JSON.parse(storage.getItem(key)); } catch (_) { return null; } };
  const write = (storage, key, value) => { try { storage.setItem(key, JSON.stringify(value)); } catch (_) {} };
  const remove = (storage, key) => { try { storage.removeItem(key); } catch (_) {} };
  let saved = read(localStorage, KEY);
  if (!saved || saved.version !== 1 || typeof saved.analytics !== 'boolean' || typeof saved.advertising !== 'boolean' || !Number.isFinite(saved.updatedAt) || Date.now() - saved.updatedAt >= MAX_AGE || saved.updatedAt > Date.now()) saved = null;
  let state = saved || { analytics: false, advertising: false };
  let loaded = false;
  let banner, dialog, previousFocus;
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ site_environment: environment });
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  const signals = s => ({ analytics_storage: s.analytics ? 'granted' : 'denied', ad_storage: s.advertising ? 'granted' : 'denied', ad_user_data: s.advertising ? 'granted' : 'denied', ad_personalization: s.advertising ? 'granted' : 'denied', functionality_storage: 'denied', personalization_storage: 'denied', security_storage: 'granted' });
  // Defaults are queued synchronously before any Google script is allowed to load.
  window.gtag('consent', 'default', signals({ analytics: false, advertising: false }));
  window.gtag('set', 'ads_data_redaction', true);

  const clean = (value, clickId = false) => {
    const text = String(value || '').trim().slice(0, clickId ? 200 : 160);
    if (/@|[\r\n<>]/.test(text)) return '';
    return clickId && !/^[A-Za-z0-9._~-]*$/.test(text) ? '' : text;
  };
  const incoming = {};
  const query = new URLSearchParams(location.search);
  [...campaignKeys, ...adKeys].forEach(key => { const value = clean(query.get(key), adKeys.includes(key)); if (value) incoming[key] = value; });
  let campaign = read(sessionStorage, ATTR) || {};
  function updateCampaign() {
    const permitted = [...(state.analytics ? campaignKeys : []), ...(state.advertising ? adKeys : [])];
    const next = {};
    permitted.forEach(key => { const value = clean(incoming[key] || campaign[key], adKeys.includes(key)); if (value) next[key] = value; });
    if (Object.keys(next).length) {
      next.landing_page = campaign.landing_page || location.pathname;
      campaign = next;
      write(sessionStorage, ATTR, next);
    } else { campaign = {}; remove(sessionStorage, ATTR); }
  }
  function loadGtm() {
    if (loaded || (!state.analytics && !state.advertising)) return;
    loaded = true;
    // Consent-gated equivalent of the supplied GTM installation snippet.
    window.dataLayer.push({ 'gtm.start': Date.now(), event: 'gtm.js', site_environment: environment });
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtm.js?id=' + GTM;
    script.id = 'salvation-gtm';
    document.head.appendChild(script);
  }
  function clearMeasurementCookies() {
    const names = document.cookie.split(';').map(part => part.split('=')[0].trim()).filter(name => /^(_ga(?:_|$)|_gid$|_gat(?:_|$)|_gcl_|_gac_)/.test(name));
    const parts = location.hostname.split('.');
    const domains = ['', location.hostname, '.' + location.hostname];
    while (parts.length > 1) { domains.push('.' + parts.join('.')); parts.shift(); }
    const segments = location.pathname.split('/').filter(Boolean);
    const paths = ['/'];
    while (segments.length) { paths.push('/' + segments.join('/'), '/' + segments.join('/') + '/'); segments.pop(); }
    names.forEach(name => domains.forEach(domain => paths.forEach(path => {
      document.cookie = name + '=; Max-Age=0; path=' + path + (domain ? '; domain=' + domain : '') + '; SameSite=Lax';
    })));
  }
  function choose(next) {
    const reduced = (state.analytics && !next.analytics) || (state.advertising && !next.advertising);
    state = { version: 1, analytics: !!next.analytics, advertising: !!next.advertising, updatedAt: Date.now() };
    saved = state;
    write(localStorage, KEY, state);
    window.gtag('consent', 'update', signals(state));
    updateCampaign();
    if (reduced) clearMeasurementCookies();
    window.dataLayer.push({ event: 'salvation_consent_update', analytics_consent: state.analytics, advertising_consent: state.advertising, site_environment: environment });
    if (banner) banner.hidden = true;
    if (dialog && dialog.open) dialog.close();
    // Unload any previously authorised tag listeners after withdrawal.
    if (reduced && loaded) { location.reload(); return; }
    loadGtm();
  }
  function openPreferences() {
    previousFocus = document.activeElement;
    dialog.querySelector('#cookie-analytics').checked = !!state.analytics;
    dialog.querySelector('#cookie-advertising').checked = !!state.advertising;
    dialog.showModal();
  }
  window.SalvationConsent = {
    getState: () => ({ analytics: !!state.analytics, advertising: !!state.advertising }),
    getAttribution: () => ({ ...campaign }),
    openPreferences: () => { if (dialog) openPreferences(); },
    track: (event, fields = {}) => {
      if (!state.analytics && !state.advertising) return;
      // Only controlled, non-personal fields may cross into GTM.
      const allowed = ['source_page', 'form_id', 'session_type', 'event_id', 'target'];
      const detail = {};
      allowed.forEach(key => { if (typeof fields[key] === 'string') detail[key] = fields[key].slice(0, 300); });
      window.dataLayer.push({ event, ...detail, site_environment: environment });
    },
  };
  updateCampaign();
  if (saved) { window.gtag('consent', 'update', signals(state)); loadGtm(); }
  else { remove(localStorage, KEY); clearMeasurementCookies(); }
  window.addEventListener('storage', event => { if (event.key === KEY) location.reload(); });

  function createUi() {
    banner = document.createElement('aside');
    banner.className = 'ss-cookie-banner'; banner.hidden = !!saved;
    banner.setAttribute('aria-label', 'Cookie choices'); banner.setAttribute('data-nosnippet', '');
    banner.innerHTML = '<div><h2>Your cookie choices</h2><p>We use essential storage to remember your cookie preferences. With your permission, we also use optional analytics and advertising cookies managed through Google Tag Manager. You can change your choices at any time through Cookie settings in the footer. <a href="/privacy/#privacy-cookies">Privacy Notice</a></p></div><div class="ss-cookie-actions"><button type="button" data-cookie-choice="accept">Accept all</button><button type="button" data-cookie-choice="reject">Reject optional</button><button type="button" data-cookie-choice="manage">Manage cookies</button></div>';
    document.body.appendChild(banner);
    dialog = document.createElement('dialog');
    dialog.className = 'ss-cookie-dialog'; dialog.setAttribute('aria-labelledby', 'ss-cookie-title');
    dialog.innerHTML = '<h2 id="ss-cookie-title">Cookie preferences</h2><p>Choose which optional cookies you allow. You can change these choices at any time.</p><div class="ss-cookie-option"><strong>Essential storage</strong><span>Always active — remembers your cookie choices.</span></div><label class="ss-cookie-option" for="cookie-analytics"><span><strong>Analytics</strong><span>Optional — helps us understand how visitors use the website.</span></span><input type="checkbox" id="cookie-analytics"></label><label class="ss-cookie-option" for="cookie-advertising"><span><strong>Advertising</strong><span>Optional — helps measure advertising and personalise ads.</span></span><input type="checkbox" id="cookie-advertising"></label><div class="ss-cookie-actions"><button type="button" data-cookie-choice="save">Save preferences</button><button type="button" data-cookie-choice="reject">Reject optional</button><button type="button" data-cookie-choice="close">Close</button></div><p><a href="/privacy/#privacy-cookies">Privacy Notice</a></p>';
    document.body.appendChild(dialog);
    dialog.addEventListener('close', () => { if (previousFocus && previousFocus.isConnected) previousFocus.focus({ preventScroll: true }); });
    [banner, dialog].forEach(element => element.addEventListener('click', event => {
      const button = event.target.closest('[data-cookie-choice]'); if (!button) return;
      const choice = button.dataset.cookieChoice;
      if (choice === 'accept') choose({ analytics: true, advertising: true });
      if (choice === 'reject') choose({ analytics: false, advertising: false });
      if (choice === 'manage') openPreferences();
      if (choice === 'save') choose({ analytics: dialog.querySelector('#cookie-analytics').checked, advertising: dialog.querySelector('#cookie-advertising').checked });
      if (choice === 'close') dialog.close();
    }));
    const footer = document.querySelector('footer') || document.body;
    const settings = document.createElement('button'); settings.type = 'button'; settings.className = 'ss-cookie-settings'; settings.textContent = 'Cookie settings';
    settings.addEventListener('click', openPreferences); footer.appendChild(settings);
    document.addEventListener('click', event => {
      const link = event.target.closest('a[href]'); if (!link) return;
      const href = link.getAttribute('href');
      if (/^(tel:|mailto:)/.test(href)) window.SalvationConsent.track('salvation_contact_click', { source_page: location.pathname, target: href.startsWith('tel:') ? 'phone' : 'email' });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', createUi, { once: true }); else createUi();
})();
