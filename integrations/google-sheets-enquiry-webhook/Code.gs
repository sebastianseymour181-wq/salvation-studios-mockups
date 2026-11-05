const SPREADSHEET_ID = '1-uk-Y-Pb1C0wLwHBoIeCRVE5xBYGVxf_z7TME8fVfC4';
const SHEET_NAME = 'Enquiries';

function doGet() {
  return reply({ ok: true, service: 'salvation-enquiry-sheet' });
}

function doPost(event) {
  try {
    const body = JSON.parse((event && event.postData && event.postData.contents) || '{}');
    const expectedSecret = PropertiesService.getScriptProperties().getProperty('WEBHOOK_SECRET');
    if (!expectedSecret || body.secret !== expectedSecret) return reply({ ok: false });

    const enquiry = body.enquiry || {};
    const required = ['name', 'email', 'session_type', 'message'];
    if (required.some(function (key) { return !cell(enquiry[key], 4000); })) {
      return reply({ ok: false });
    }

    const lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
      if (!sheet) throw new Error('Enquiries sheet tab not found');

      const submissionId = cell(enquiry.submission_id, 120);
      if (submissionId && sheet.getLastRow() > 1) {
        const duplicate = sheet
          .getRange(2, 12, sheet.getLastRow() - 1, 1)
          .createTextFinder(submissionId)
          .matchEntireCell(true)
          .findNext();
        if (duplicate) return reply({ ok: true, duplicate: true });
      }

      sheet.appendRow([
        new Date(),
        cell(enquiry.name, 120),
        cell(enquiry.email, 180),
        cell(enquiry.phone, 80),
        cell(enquiry.artist_company, 160),
        cell(enquiry.session_type, 120),
        cell(enquiry.dates, 180),
        cell(enquiry.message, 4000),
        cell(enquiry.source_page, 300),
        'New',
        '',
        submissionId,
      ]);
    } finally {
      lock.releaseLock();
    }

    return reply({ ok: true });
  } catch (error) {
    console.error(error && error.message ? error.message : error);
    return reply({ ok: false });
  }
}

function cell(value, maxLength) {
  const text = String(value == null ? '' : value)
    .replace(/\r/g, '')
    .trim()
    .slice(0, maxLength);
  return /^[=+\-@]/.test(text) ? "'" + text : text;
}

function reply(body) {
  return ContentService
    .createTextOutput(JSON.stringify(body))
    .setMimeType(ContentService.MimeType.JSON);
}
