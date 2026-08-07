(() => {
  function track(eventName, detail) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(Object.assign({ event: eventName }, detail || {}));
  }

  document.querySelectorAll('[data-analytics]').forEach(element => {
    if (element.dataset.analyticsBound) return;
    element.dataset.analyticsBound = 'true';
    element.addEventListener('click', () => {
      track('salvation_click', {
        target: element.getAttribute('data-analytics'),
        href: element.getAttribute('href') || '',
      });
    });
  });

  function enquiryMailto(data) {
    const lines = [
      'Name: ' + (data.get('name') || ''),
      'Artist / company: ' + (data.get('artist_company') || ''),
      'Email: ' + (data.get('email') || ''),
      'Phone: ' + (data.get('phone') || ''),
      'Session type: ' + (data.get('session_type') || ''),
      'Preferred dates: ' + (data.get('dates') || ''),
      '',
      'Additional session details:',
      data.get('message') || '',
    ];
    return 'mailto:info@salvationstudios.co.uk?subject='
      + encodeURIComponent('Studio session enquiry - Salvation Studios')
      + '&body='
      + encodeURIComponent(lines.join('\n'));
  }

  document.querySelectorAll('.enquiry-form').forEach(form => {
    if (form.dataset.enquiryBound) return;
    form.dataset.enquiryBound = 'true';

    const status = form.querySelector('.form-status');
    const submit = form.querySelector('button[type="submit"]');
    const startedAt = form.querySelector('input[name="form_started_at"]');
    const sourcePage = window.location.pathname || '/';
    const markFormStarted = () => {
      if (startedAt) startedAt.value = String(Date.now());
    };

    markFormStarted();
    form.addEventListener('focusin', () => {
      track('salvation_enquiry_start', { source_page: sourcePage });
    }, { once: true });

    form.addEventListener('submit', async event => {
      event.preventDefault();
      const data = new FormData(form);
      const payload = Object.fromEntries(data.entries());
      payload.source_page = sourcePage;
      if (status) {
        status.hidden = false;
        status.textContent = 'Sending your enquiry...';
      }
      if (submit) submit.disabled = true;

      try {
        const response = await fetch('/api/enquiry', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok || !result.ok) {
          throw new Error(result.error || 'The enquiry could not be sent.');
        }
        track('salvation_enquiry_submit', {
          source_page: sourcePage,
          session_type: data.get('session_type') || '',
        });
        form.reset();
        markFormStarted();
        if (status) status.textContent = form.dataset.successMessage || 'Thanks. Your enquiry has been sent to Salvation Studios.';
      } catch (error) {
        track('salvation_enquiry_error', { source_page: sourcePage });
        if (error.message === 'Email delivery is not configured yet.') {
          if (status) status.textContent = 'Direct delivery is being configured. Opening a fallback email draft.';
          window.location.href = enquiryMailto(data);
        } else if (status) {
          status.textContent = error.message || 'The enquiry could not be sent. Please email info@salvationstudios.co.uk.';
        }
      } finally {
        if (submit) submit.disabled = false;
      }
    });
  });
})();
