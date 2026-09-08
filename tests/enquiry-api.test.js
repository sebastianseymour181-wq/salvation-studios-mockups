const test = require('node:test');
const assert = require('node:assert/strict');
const { Readable } = require('node:stream');

const handler = require('../api/enquiry');

async function submit(payload) {
  const req = Readable.from([JSON.stringify({
    form_started_at: Date.now() - 4000,
    session_type: 'Full Package Competition',
    ...payload,
  })]);
  req.method = 'POST';
  req.headers = { origin: 'https://salvation-studios-mockups-three.vercel.app' };

  return new Promise(resolve => {
    const res = {
      headers: {},
      setHeader(name, value) { this.headers[name] = value; },
      end(body) { resolve({ statusCode: this.statusCode, body: JSON.parse(body) }); },
    };
    handler(req, res);
  });
}

test('competition entries require phone and artist name but allow no demo link', async () => {
  const originalFetch = global.fetch;
  const originalKey = process.env.RESEND_API_KEY;
  const originalFrom = process.env.ENQUIRY_FROM_EMAIL;
  const originalSheetUrl = process.env.ENQUIRY_SHEETS_WEBHOOK_URL;
  const originalSheetSecret = process.env.ENQUIRY_SHEETS_SECRET;
  let sentEmail;

  process.env.RESEND_API_KEY = 'test-key';
  process.env.ENQUIRY_FROM_EMAIL = 'website@example.com';
  delete process.env.ENQUIRY_SHEETS_WEBHOOK_URL;
  delete process.env.ENQUIRY_SHEETS_SECRET;
  global.fetch = async (_url, options) => {
    sentEmail = JSON.parse(options.body);
    return { ok: true };
  };

  try {
    const missingPhone = await submit({
      name: 'Test Artist',
      artist_company: 'The Tests',
      email: 'artist@example.com',
    });
    assert.equal(missingPhone.statusCode, 400);

    const missingArtist = await submit({
      name: 'Test Artist',
      email: 'artist@example.com',
      phone: '07123 456789',
    });
    assert.equal(missingArtist.statusCode, 400);

    const valid = await submit({
      name: 'Test Artist',
      artist_company: 'The Tests',
      instagram: '@thetests',
      email: 'artist@example.com',
      phone: '07123 456789',
    });
    assert.equal(valid.statusCode, 200);
    assert.deepEqual(valid.body, { ok: true });
    assert.match(sentEmail.text, /Instagram: @thetests/);
  } finally {
    global.fetch = originalFetch;
    if (originalKey === undefined) delete process.env.RESEND_API_KEY;
    else process.env.RESEND_API_KEY = originalKey;
    if (originalFrom === undefined) delete process.env.ENQUIRY_FROM_EMAIL;
    else process.env.ENQUIRY_FROM_EMAIL = originalFrom;
    if (originalSheetUrl === undefined) delete process.env.ENQUIRY_SHEETS_WEBHOOK_URL;
    else process.env.ENQUIRY_SHEETS_WEBHOOK_URL = originalSheetUrl;
    if (originalSheetSecret === undefined) delete process.env.ENQUIRY_SHEETS_SECRET;
    else process.env.ENQUIRY_SHEETS_SECRET = originalSheetSecret;
  }
});
