const MAX_BODY_BYTES = 12000;
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
  const from = process.env.ENQUIRY_FROM_EMAIL || 'Salvation Studios <onboarding@resend.dev>';

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

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    res.statusCode = 405;
    res.end(JSON.stringify({ ok: false, error: 'Method not allowed' }));
    return;
  }

  try {
    const rawBody = await readBody(req);
    const payload = JSON.parse(rawBody || '{}');

    if (clean(payload.website, 200)) {
      res.statusCode = 200;
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    const enquiry = {
      name: clean(payload.name, 120),
      artist_company: clean(payload.artist_company, 160),
      email: clean(payload.email, 180),
      phone: clean(payload.phone, 80),
      session_type: clean(payload.session_type, 120),
      dates: clean(payload.dates, 180),
      message: clean(payload.message, 4000),
      source_page: clean(payload.source_page, 300),
    };

    if (!enquiry.name || !enquiry.email || !enquiry.session_type || !enquiry.message) {
      res.statusCode = 400;
      res.end(JSON.stringify({ ok: false, error: 'Please fill in name, email, session type and additional session details.' }));
      return;
    }

    if (!isEmail(enquiry.email)) {
      res.statusCode = 400;
      res.end(JSON.stringify({ ok: false, error: 'Please enter a valid email address.' }));
      return;
    }

    await sendWithResend(enquiry);
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
