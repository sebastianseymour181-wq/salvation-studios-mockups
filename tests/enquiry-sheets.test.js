const test = require('node:test');
const assert = require('node:assert/strict');

const { buildSheetPayload, postToSheet } = require('../api/enquiry-sheets');

test('buildSheetPayload adds a stable submission id and preserves enquiry fields', () => {
  const payload = buildSheetPayload({
    name: 'A band',
    email: 'band@example.com',
    session_type: 'Live video',
    message: 'We need a day in the live room.',
    source_page: '/live-video-sessions/',
  });

  assert.match(payload.submission_id, /^[0-9a-f-]{36}$/);
  assert.equal(payload.name, 'A band');
  assert.equal(payload.source_page, '/live-video-sessions/');
  assert.match(payload.submitted_at, /^\d{4}-\d{2}-\d{2}T/);
});

test('postToSheet skips cleanly when the integration is not configured', async () => {
  const previousUrl = process.env.ENQUIRY_SHEETS_WEBHOOK_URL;
  const previousSecret = process.env.ENQUIRY_SHEETS_SECRET;
  delete process.env.ENQUIRY_SHEETS_WEBHOOK_URL;
  delete process.env.ENQUIRY_SHEETS_SECRET;

  try {
    assert.deepEqual(await postToSheet({ name: 'A band' }), { skipped: true });
  } finally {
    if (previousUrl === undefined) delete process.env.ENQUIRY_SHEETS_WEBHOOK_URL;
    else process.env.ENQUIRY_SHEETS_WEBHOOK_URL = previousUrl;
    if (previousSecret === undefined) delete process.env.ENQUIRY_SHEETS_SECRET;
    else process.env.ENQUIRY_SHEETS_SECRET = previousSecret;
  }
});

test('postToSheet sends the shared secret and enquiry payload to the webhook', async () => {
  const previousUrl = process.env.ENQUIRY_SHEETS_WEBHOOK_URL;
  const previousSecret = process.env.ENQUIRY_SHEETS_SECRET;
  process.env.ENQUIRY_SHEETS_WEBHOOK_URL = 'https://script.google.com/macros/s/test/exec';
  process.env.ENQUIRY_SHEETS_SECRET = 'test-secret';
  let request;

  try {
    const result = await postToSheet(
      { name: 'A band', email: 'band@example.com' },
      async (_url, options) => {
        request = options;
        return { ok: true, json: async () => ({ ok: true }) };
      },
    );

    assert.deepEqual(result, { ok: true });
    assert.equal(request.method, 'POST');
    assert.equal(request.headers['Content-Type'], 'application/json');
    assert.deepEqual(JSON.parse(request.body), {
      secret: 'test-secret',
      enquiry: { name: 'A band', email: 'band@example.com' },
    });
  } finally {
    if (previousUrl === undefined) delete process.env.ENQUIRY_SHEETS_WEBHOOK_URL;
    else process.env.ENQUIRY_SHEETS_WEBHOOK_URL = previousUrl;
    if (previousSecret === undefined) delete process.env.ENQUIRY_SHEETS_SECRET;
    else process.env.ENQUIRY_SHEETS_SECRET = previousSecret;
  }
});
