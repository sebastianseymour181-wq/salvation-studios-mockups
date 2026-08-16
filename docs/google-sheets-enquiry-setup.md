# Google Sheets enquiry tracker

The site still delivers the enquiry email through Resend. When the two optional
Vercel variables below are present, it also posts the same validated enquiry to
the `Enquiries` tab in the Salvation Studios workbook.

## Owner setup

Charlie should do these steps from the Google account that owns the sheet:

1. Open the [Salvation Studios enquiry sheet](https://docs.google.com/spreadsheets/d/1-uk-Y-Pb1C0wLwHBoIeCRVE5xBYGVxf_z7TME8fVfC4/edit), then choose **Extensions → Apps Script**.
2. Replace the editor contents with `integrations/google-sheets-enquiry-webhook/Code.gs` and save.
3. In **Project Settings → Script properties**, add `WEBHOOK_SECRET` with a long random value (at least 32 characters). Do not commit or email this value.
4. Choose **Deploy → New deployment → Web app**. Set **Execute as** to the owner account and **Who has access** to **Anyone**, then deploy and copy the `/exec` URL.
5. Add these Vercel Production variables, using the same secret value:

   - `ENQUIRY_SHEETS_WEBHOOK_URL` — the Apps Script `/exec` URL
   - `ENQUIRY_SHEETS_SECRET` — the Script property value

6. Redeploy the site and submit one labelled test enquiry. Confirm the email and one new row. Submitting the same request twice is idempotent by `Submission ID`.

The web app must execute as the sheet owner so the script can append rows without
giving the website or visitors direct access to the workbook. Apps Script web apps
use `doPost(e)` for HTTP POST bodies and are deployed from the **Deploy** menu:
[Google's web-app guide](https://developers.google.com/apps-script/guides/web).

The script keeps the secret in [Script Properties](https://developers.google.com/apps-script/reference/properties/properties-service),
serializes writes with [Script Lock](https://developers.google.com/apps-script/reference/lock/lock-service),
appends rows with [`Sheet.appendRow`](https://developers.google.com/apps-script/reference/spreadsheet/sheet#appendRow(Object)),
and uses [TextFinder](https://developers.google.com/apps-script/reference/spreadsheet/text-finder)
to ignore a retry with the same Submission ID.

## Security note

The sheet is currently shared as **Anyone with the link — Editor**. Change
**General access** to **Restricted** before collecting real enquiries. Keep Charlie
as owner and Eliza as an editor.
