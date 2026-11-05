(() => {
  const REQUEST_TIMEOUT_MS = 20000;
  // Vercel filesystem functions take precedence over rewrites. Use a distinct
  // same-origin proxy path on the approved test alias; all other hosts retain
  // their own API. Production credentials never enter this deployment.
  const enquiryEndpoint = window.location.hostname === 'salvation-studios-mockups-three.vercel.app'
    ? '/test-enquiry-delivery'
    : '/api/enquiry';
  const FIELD_LIMITS = { name: 120, artist_company: 160, instagram: 120, email: 180, phone: 80, session_type: 120, dates: 180, message: 4000, preferred_room: 160, engineering_support: 160, duration: 160 };
  const bookingFields = [['preferred_room', 'Preferred room'], ['engineering_support', 'Engineer or support required'], ['duration', 'Approximate duration']];
  function track(eventName, detail) {
    return !!(window.SalvationConsent && window.SalvationConsent.track(eventName, detail));
  }

  document.querySelectorAll('[data-analytics]').forEach(element => {
    if (element.dataset.analyticsBound) return;
    element.dataset.analyticsBound = 'true';
    element.addEventListener('click', () => {
      track('salvation_click', { target: element.getAttribute('data-analytics') });
    });
  });

  function enquiryContext(payload) {
    const blocks = [];
    bookingFields.forEach(([key, label]) => { if (payload[key]) blocks.push(label + ': ' + payload[key]); });
    const campaign = Object.entries(payload.attribution || {}).map(([key, value]) => key + ': ' + value);
    if (campaign.length) blocks.push('Campaign attribution (consented):\n' + campaign.join('\n'));
    return blocks;
  }

  function enquiryText(payload) {
    const lines = [
      'Name: ' + (payload.name || ''),
      'Artist / company: ' + (payload.artist_company || ''),
      'Instagram: ' + (payload.instagram || ''),
      'Email: ' + (payload.email || ''),
      'Phone: ' + (payload.phone || ''),
      'Session type: ' + (payload.session_type || ''),
      'Preferred dates: ' + (payload.dates || ''),
      'Source page: ' + (payload.source_page || ''),
      '', 'Additional session details:', payload.message || '',
    ];
    enquiryContext(payload).forEach(block => lines.push('', block));
    return lines.join('\n');
  }

  document.querySelectorAll('.enquiry-form').forEach(form => {
    if (form.dataset.enquiryBound) return;
    form.dataset.enquiryBound = 'true';
    const status = form.querySelector('.form-status');
    const submit = form.querySelector('button[type="submit"]');
    const startedAt = form.querySelector('input[name="form_started_at"]');
    const sourcePage = window.location.pathname || '/';
    const detail = { source_page: sourcePage, form_id: form.id || 'studio-enquiry-form' };
    let started = false;
    let pending = false;
    let fallback;
    const markFormStarted = () => { if (startedAt) startedAt.value = String(Date.now()); };
    const eligibleStart = () => {
      // A blocked pre-consent interaction must not consume the start event.
      // Only a new, eligible interaction is recorded; nothing is replayed.
      if (!started) started = track('salvation_enquiry_start', detail);
    };
    markFormStarted();
    ['focusin', 'input', 'change'].forEach(event => form.addEventListener(event, eligibleStart));

    function showFallback(payload) {
      if (!status) return;
      fallback = document.createElement('div');
      fallback.className = 'enquiry-fallback';
      const link = document.createElement('a');
      link.textContent = 'Open an email draft';
      link.href = 'mailto:info@salvationstudios.co.uk?subject=' + encodeURIComponent('Studio session enquiry - Salvation Studios') + '&body=' + encodeURIComponent(enquiryText(payload));
      const note = document.createElement('p');
      note.textContent = 'Your details are still here. If your email app shortens the draft, copy the complete details below. Please check with the studio before resending if delivery is uncertain.';
      const disclosure = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = 'View complete enquiry details to copy';
      const text = document.createElement('textarea');
      text.readOnly = true;
      text.rows = 8;
      text.style.width = '100%';
      text.setAttribute('aria-label', 'Complete enquiry details to copy');
      text.value = enquiryText(payload);
      disclosure.append(summary, text);
      fallback.append(link, note, disclosure);
      status.insertAdjacentElement('afterend', fallback);
    }

    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (pending) return;
      if (fallback) { fallback.remove(); fallback = null; }
      const data = new FormData(form);
      const payload = Object.fromEntries(data.entries());
      payload.source_page = sourcePage;
      const oversized = Object.entries(FIELD_LIMITS).find(([key, max]) => String(payload[key] || '').replace(/\r/g, '').trim().length > max);
      if (oversized) {
        if (status) { status.hidden = false; status.textContent = 'Please shorten ' + oversized[0].replace(/_/g, ' ') + ' to ' + oversized[1] + ' characters or fewer.'; }
        const field = form.elements.namedItem(oversized[0]);
        if (field && field.focus) field.focus();
        return;
      }
      // The deployed API and Sheet accept 4,000 characters in total. Preserve
      // every detail or reject before sending; never silently omit context.
      payload.attribution = window.SalvationConsent ? window.SalvationConsent.getAttribution() : {};
      payload.attribution_consent = window.SalvationConsent ? window.SalvationConsent.getState() : { analytics: false, advertising: false };
      const fallbackPayload = { ...payload };
      const combinedMessage = [String(payload.message || '').replace(/\r/g, '').trim(), ...enquiryContext(payload)].filter(Boolean).join('\n\n');
      if (combinedMessage.length > 4000) {
        if (status) { status.hidden = false; status.textContent = 'To include all your session and campaign details, please shorten your project or optional session details by ' + (combinedMessage.length - 4000) + ' characters. Nothing has been sent and your details have been kept.'; }
        showFallback(fallbackPayload);
        const messageField = form.elements.namedItem('message');
        if (messageField && messageField.focus) messageField.focus();
        return;
      }
      payload.message = combinedMessage;
      // Send only fields understood by the established endpoint. This avoids
      // duplicating private details/context and respects its 12,000-byte cap.
      const wirePayload = {};
      ['name', 'artist_company', 'instagram', 'email', 'phone', 'session_type', 'dates', 'message', 'source_page', 'form_started_at', 'website'].forEach(key => { if (payload[key] !== undefined) wirePayload[key] = payload[key]; });
      const body = JSON.stringify(wirePayload);
      if (new TextEncoder().encode(body).length > 12000) {
        if (status) { status.hidden = false; status.textContent = 'This enquiry exceeds the delivery size limit. Please shorten your project or optional session details. Nothing has been sent and your details have been kept.'; }
        showFallback(fallbackPayload);
        return;
      }
      if (status) { status.hidden = false; status.textContent = 'Sending your enquiry...'; }
      pending = true;
      if (submit) submit.disabled = true;
      const controller = new AbortController();
      let timedOut = false;
      const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, REQUEST_TIMEOUT_MS);
      try {
        const response = await fetch(enquiryEndpoint, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body, signal: controller.signal,
        });
        const result = await response.json().catch(error => { if (timedOut) throw error; return {}; });
        if (!response.ok || !result.ok) throw new Error(result.error || 'We could not confirm delivery. Please check with the studio before resending.');
        if (!payload.website && result.received !== false) {
          track('salvation_enquiry_submit', {
            ...detail, session_type: data.get('session_type') || '',
            event_id: result.submission_id || (window.crypto && crypto.randomUUID ? crypto.randomUUID() : String(Date.now())),
          });
        }
        form.reset();
        started = false;
        markFormStarted();
        if (status) status.textContent = form.dataset.successMessage || 'Thanks. Your enquiry has been sent to Salvation Studios.';
      } catch (error) {
        track('salvation_enquiry_error', detail);
        if (status) {
          status.textContent = timedOut
            ? 'This is taking longer than expected. We could not confirm delivery, but your enquiry may have arrived. Your details have been kept. Please check with the studio before resending.'
            : error instanceof TypeError
              ? 'The connection was interrupted. We could not confirm delivery. Your details have been kept. Please check with the studio before resending.'
              : error.message === 'Email delivery is not configured yet.'
                ? 'Direct delivery is unavailable. Your details have been kept. You can open an email draft below.'
                : error.message || 'We could not confirm delivery. Please check with the studio before resending.';
        }
        showFallback(fallbackPayload);
      } finally {
        clearTimeout(timeout);
        pending = false;
        if (submit) submit.disabled = false;
      }
    });
  });
})();
