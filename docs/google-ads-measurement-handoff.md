# Google Ads / GTM website handoff for Ollie

## Installation

Container: **GTM-TKKWMVXR**. The synchronous `/site-consent.js` entrypoint is the first script on all 36 static HTML pages, including the homepage, service/room pages, Google Ads landing page and Sean/Phill Signature Sessions pages. `tools/install_site_tracking.py` makes installation repeatable; the site hygiene check prevents untagged new pages.

The container is consent-gated rather than unconditionally loading the pasted snippet. A denied default is queued before Google can execute. Basic Consent Mode means **no GTM, GA4 or Ads tracking requests until optional consent is given**. The body includes the supplied GTM no-JavaScript iframe URL as an inert `data-consent-src`, deliberately without `src`: without JavaScript we cannot obtain an optional-cookie choice, so we do not activate that fallback.

Current public container verification on 4 November: HTTP 200; published version 2 includes a Google tag for **G-B7EBGRME05**. This verifies the public container, not unpublished workspace settings or reporting in the account. No additional GA4 installation was hardcoded into the website.

## Consent contract

- First visit: Analytics and Advertising off. The banner has equally styled Accept all and Reject optional actions, plus Manage cookies.
- Analytics toggles `analytics_storage`.
- Advertising toggles `ad_storage`, `ad_user_data` and `ad_personalization` together. Its label explains measurement and personalised advertising.
- Defaults for those four signals are denied; security storage is granted. No URL passthrough is enabled. `ads_data_redaction` is true.
- An explicit choice is remembered in essential local storage under `salvation_cookie_preferences_v1` for 180 days. Consented campaign attribution uses session storage `salvation_campaign_v1`.
- Cookie settings is available in every footer. Withdrawal updates consent, removes category-specific attribution, attempts to clear accessible first-party Google measurement cookies and reloads the page to unload previously authorised tag listeners.
- The site pushes `salvation_consent_update` with boolean `analytics_consent` and `advertising_consent`. Google consent commands are already queued by the site; do not add a competing banner or reset them to granted in GTM.
- Google tags must retain their built-in consent checks. Any future Custom HTML or third-party tags require their own additional consent checks before publication. The CSP supports normal GTM, GA4, Ads endpoints and Tag Manager preview without adding `unsafe-eval`; use templates rather than Custom JavaScript variables requiring eval.

## Enquiry and booking behaviour

Enquiries POST JSON to `/api/enquiry`. The established server validates the request, sends an email through Resend, and attempts an optional Google Sheets sync. Success is displayed inline; there is **no thank-you page**. If delivery fails, entered values remain and the visitor can retry. An email draft fallback is an intent to enquire, not a successful submission.

No online payment/booking platform or confirmed-booking callback is present. The studio team discusses availability and confirms a booking after the enquiry. We therefore measure a **successful enquiry**, not a completed booking. If confirmed-booking reporting is required, connect the studio’s confirmation process to an offline conversion import or provide a verified booking-platform callback separately.

### Canonical conversion event

Custom event trigger: **`salvation_enquiry_submit`**.

It is pushed once by the browser after an HTTP-success JSON response with `ok: true`, excluding a filled honeypot or an explicit `received: false` response. It does not fire on button clicks, validation failures, server errors or email-draft fallback. It is emitted only with optional measurement consent.

Parameters:

| Field | Meaning |
| --- | --- |
| `form_id` | Stable form ID, e.g. `google-ads-enquiry-form`, `enquiry-form`, `sean-enquiry-form`, `phill-enquiry-form` |
| `source_page` | Current pathname, without the query string |
| `session_type` | Selected service, or named Signature Sessions producer/package |
| `event_id` | Per-success random identifier for debugging/deduplication; not a customer identifier |
| `site_environment` | `production` on the two official domains, `test` elsewhere |

In GTM, map this trigger to a GA4 **`generate_lead`** event and/or the intended Google Ads lead conversion tag. Choose one primary Ads conversion source, so a direct Ads tag and an imported GA4 event do not double-count the same enquiry. Do not make GA4 automatic `form_submit`, `salvation_click`, `salvation_contact_click` or `salvation_enquiry_start` primary enquiry conversions: those are intent signals, not delivery confirmation.

Other events: `salvation_enquiry_start`, `salvation_enquiry_error`, `salvation_click` (existing labelled CTA intents), `salvation_contact_click` (phone/email intent). The last two identify the action without sending email addresses or phone numbers to GTM.

The site’s dataLayer allowlist excludes names, email addresses, phone numbers, Instagram handles, music links and project messages. Do not enable automatic user-provided-data collection or enhanced conversions using those form fields without a separately reviewed implementation.

### Attribution

Whitelisted `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content` are retained across pages only with Analytics permission. `gclid`, `gbraid`, `wbraid` are retained only with Advertising permission. They are held for the browsing session, with the landing pathname. No raw query string or referrer is copied to dataLayer.

Consented attribution and optional room/support/duration answers are appended as complete blocks to the existing enquiry message when they fit its established 4,000-character limit. The landing-page project field is limited to 3,000 characters to leave room for this context; unusually long existing-page messages are preserved rather than cut to make room for attribution. This is compatible with the existing email service, Sheets webhook and campaign tabs; no workbook schema change is required. No advertising identifiers are retained in our session storage or added to the enquiry when Advertising is off.

## Ollie’s account-side checks

1. Open the test landing page and give the optional consent needed for the tags under test. A fresh/rejecting browser intentionally shows no GTM network request.
2. In Tag Assistant, verify the denied defaults precede container startup and that Analytics/Advertising changes produce the four expected Google consent signals.
3. Configure the custom-event conversion trigger and GA4/Ads destinations. Check GA4 DebugView and Ads diagnostics for one accepted test enquiry, not just a form click.
4. Filter test traffic using the hostname and `site_environment`. Production hostnames are `www.salvationstudios.co.uk` and `salvationstudios.co.uk`. The existing published base tag can otherwise receive accepted preview page views; review its hostname filters or use a test property during QA.
5. Keep automatic form interaction events separate from the canonical successful-enquiry conversion. Ensure future tags respect category consent.
6. Recheck official-domain attribution, consent, the normal enquiry form and Sean’s package form after the production release.

## Review state

Website-side implementation and automated browser checks are recorded in `docs/google-ads-upgrade-plan.md` and the task QA output. Mocked form tests never send a studio lead. End-to-end receipt of a real enquiry in email/Sheets and GA4/Ads account-side reporting require the final coordinated check. No message has been sent to Ollie by this task.
