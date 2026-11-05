const crypto = require('node:crypto');

const GOOGLE_SCRIPT_HOSTS = new Set([
  'script.google.com',
  'script.googleusercontent.com',
]);

function buildSheetPayload(enquiry) {
  return {
    ...enquiry,
    submitted_at: new Date().toISOString(),
    submission_id: crypto.randomUUID(),
  };
}

function webhookUrl() {
  const rawUrl = process.env.ENQUIRY_SHEETS_WEBHOOK_URL;
  if (!rawUrl) return null;

  let url;
  try {
    url = new URL(rawUrl);
  } catch (_error) {
    throw new Error('Google Sheets webhook URL is invalid');
  }

  if (url.protocol !== 'https:' || !GOOGLE_SCRIPT_HOSTS.has(url.hostname)) {
    throw new Error('Google Sheets webhook URL is not allowed');
  }
  return url.toString();
}

async function postToSheet(enquiry, fetchImpl = global.fetch) {
  const url = webhookUrl();
  const secret = process.env.ENQUIRY_SHEETS_SECRET;
  if (!url || !secret) return { skipped: true };
  if (typeof fetchImpl !== 'function') throw new Error('Fetch is not available');

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);
  let response;
  try {
    response = await fetchImpl(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ secret, enquiry }),
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeout);
  }

  let result = {};
  try {
    result = await response.json();
  } catch (_error) {
    // The webhook must return JSON, but keep the public error generic if it does not.
  }
  if (!response.ok || !result.ok) {
    const error = new Error('Google Sheets webhook rejected the enquiry');
    error.statusCode = 502;
    throw error;
  }
  return result;
}

module.exports = { buildSheetPayload, postToSheet };
