const { buildSheetPayload, postToSheet } = require('./enquiry-sheets');

const MAX_BODY_BYTES = 12000;
const MIN_FORM_AGE_MS = 3000;
const MAX_FORM_AGE_MS = 24 * 60 * 60 * 1000;
const DEFAULT_TO_EMAIL = 'info@salvationstudios.co.uk';

function readBody(req) {
  return new Promise((resolve, reject) => {
    let total = 0;
    let body = '';

    req.on('data', chunk => {
      total += chunk.length;
      if (total > MAX_BODY_BYTES) {
        reject(Object.assign(new Error('Request body too large'), { statusCode: 413 }));
        req.destroy();
        return;
      }
      body += chunk.toString('utf8');
    });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

function clean(value, maxLength = 1200) {
  return String(value || '').replace(/\r/g, '').trim().slice(0, maxLength);
}

function isEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function isAllowedOrigin(origin) {
  if (!origin) return false;

  try {
    const { hostname, protocol } = new URL(origin);
    if (protocol !== 'https:') return false;
    return hostname === 'www.salvationstudios.co.uk'
      || hostname === 'salvationstudios.co.uk'
      || hostname.endsWith('.vercel.app');
  } catch (_error) {
    return false;
  }
}

function hasHumanFormTiming(value) {
  const startedAt = Number(value);
  if (!Number.isFinite(startedAt) || startedAt <= 0) return false;

  const age = Date.now() - startedAt;
  if (age >= 0 && age < MIN_FORM_AGE_MS) return false;
  if (age > MAX_FORM_AGE_MS) return false;
  if (age < -5 * 60 * 1000) return false;
  return true;
}

function escapeHtml(value) {
  return clean(value, 4000)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/\n/g, '<br>');
}

function textBlock(enquiry) {
  return [
    'New Salvation Studios enquiry',
    '',
    `Name: ${enquiry.name}`,
    `Artist / company: ${enquiry.artist_company || '-'}`,
    `Instagram: ${enquiry.instagram || '-'}`,
    `Email: ${enquiry.email}`,
    `Phone: ${enquiry.phone || '-'}`,
    `Session type: ${enquiry.session_type}`,
    `Preferred dates: ${enquiry.dates || '-'}`,
    `Source page: ${enquiry.source_page || '-'}`,
    '',
    'Additional session details:',
    enquiry.message,
  ].join('\n');
}

function htmlBlock(enquiry) {
  const rows = [
    ['Name', enquiry.name],
    ['Artist / company', enquiry.artist_company || '-'],
    ['Instagram', enquiry.instagram || '-'],
    ['Email', enquiry.email],
    ['Phone', enquiry.phone || '-'],
    ['Session type', enquiry.session_type],
    ['Preferred dates', enquiry.dates || '-'],
    ['Source page', enquiry.source_page || '-'],
  ];

  return `<!doctype html>
  <html>
    <body style="font-family:Arial,sans-serif;color:#1f1729;line-height:1.5">
      <h1 style="font-size:22px;margin:0 0 18px">New Salvation Studios enquiry</h1>
      <table cellpadding="8" cellspacing="0" style="border-collapse:collapse;margin-bottom:20px">
        ${rows.map(([label, value]) => `<tr><td style="font-weight:700;border-bottom:1px solid #eee">${escapeHtml(label)}</td><td style="border-bottom:1px solid #eee">${escapeHtml(value)}</td></tr>`).join('')}
      </table>
      <h2 style="font-size:17px;margin:0 0 10px">Additional session details</h2>
      <p style="margin:0">${escapeHtml(enquiry.message)}</p>
    </body>
  </html>`;
}

async function sendWithResend(enquiry) {
  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    const error = new Error('Email delivery is not configured');
    error.statusCode = 503;
    throw error;
  }

  const to = (process.env.ENQUIRY_TO_EMAIL || DEFAULT_TO_EMAIL)
    .split(',')
    .map(email => email.trim())
    .filter(Boolean);
  const from = process.env.ENQUIRY_FROM_EMAIL;
  if (!from) {
    const error = new Error('Sender email is not configured');
    error.statusCode = 503;
    throw error;
  }

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from,
      to,
      reply_to: enquiry.email,
      subject: `Studio enquiry: ${enquiry.session_type} - ${enquiry.name}`,
      text: textBlock(enquiry),
      html: htmlBlock(enquiry),
    }),
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    const error = new Error(`Email provider rejected the enquiry (${response.status})`);
    error.statusCode = 502;
    error.providerDetail = detail.slice(0, 300);
    throw error;
  }
}

module.exports = async function handler(req, res) {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    res.statusCode = 405;
    res.end(JSON.stringify({ ok: false, error: 'Method not allowed' }));
    return;
  }

  try {
    if (!isAllowedOrigin(req.headers.origin)) {
      res.statusCode = 403;
      res.end(JSON.stringify({ ok: false, error: 'Origin not allowed' }));
      return;
    }

    const rawBody = await readBody(req);
    let payload;
    try {
      payload = JSON.parse(rawBody || '{}');
    } catch (_error) {
      res.statusCode = 400;
      res.end(JSON.stringify({ ok: false, error: 'Invalid JSON payload.' }));
      return;
    }

    if (clean(payload.website, 200)) {
      res.statusCode = 200;
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    if (!hasHumanFormTiming(payload.form_started_at)) {
      res.statusCode = 400;
      res.end(JSON.stringify({ ok: false, error: 'Please wait a moment and try again.' }));
      return;
    }

    const enquiry = {
      name: clean(payload.name, 120),
      artist_company: clean(payload.artist_company, 160),
      instagram: clean(payload.instagram, 120),
      email: clean(payload.email, 180),
      phone: clean(payload.phone, 80),
      session_type: clean(payload.session_type, 120),
      dates: clean(payload.dates, 180),
      message: clean(payload.message, 4000),
      source_page: clean(payload.source_page, 300),
    };

    const isCompetition = enquiry.session_type === 'Full Package Competition';
    const missingRequiredField = !enquiry.name || !enquiry.email || !enquiry.session_type
      || (isCompetition ? !enquiry.phone || !enquiry.artist_company : !enquiry.message);
    if (missingRequiredField) {
      res.statusCode = 400;
      res.end(JSON.stringify({
        ok: false,
        error: isCompetition
          ? 'Please fill in name, email, phone number and artist or band name.'
          : 'Please fill in name, email, session type and additional session details.',
      }));
      return;
    }

    if (!isEmail(enquiry.email)) {
      res.statusCode = 400;
      res.end(JSON.stringify({ ok: false, error: 'Please enter a valid email address.' }));
      return;
    }

    await sendWithResend(enquiry);
    try {
      await postToSheet(buildSheetPayload({
        ...enquiry,
        artist_company: [enquiry.artist_company, enquiry.instagram && `Instagram: ${enquiry.instagram}`].filter(Boolean).join('\n'),
        phone: enquiry.phone && `'${enquiry.phone}`,
      }));
    } catch (error) {
      // Email remains the delivery fallback if the optional sheet sync is unavailable.
      console.error('Google Sheets enquiry sync failed:', error.message);
    }
    res.statusCode = 200;
    res.end(JSON.stringify({ ok: true }));
  } catch (error) {
    const statusCode = error.statusCode || 500;
    res.statusCode = statusCode;
    res.end(JSON.stringify({
      ok: false,
      error: statusCode === 503
        ? 'Email delivery is not configured yet.'
        : 'The enquiry could not be sent. Please try again or email info@salvationstudios.co.uk.',
    }));
  }
};
