# Enquiry improvements prepared 5 November 2026

## Status and release gate

Implemented and tested locally on `feature/google-ads-landing-2026-11-04`, based on `e45069ded89b1505a2900f457f22a8543a0a2ed3`. These changes are not deployed. No real enquiries, emails or Sheet rows were sent.

**Do not publish the new frontend by itself.** The named test alias currently rewrites `/api/enquiry` to the existing production handler. That handler ignores the new structured context and caps message text at 4,000 characters. The deployed Apps Script also caps the combined message at 4,000. Sending the new frontend to that old backend would silently lose context.

A coordinated release must:

1. Have the Sheet owner deploy the updated `integrations/google-sheets-enquiry-webhook/Code.gs`. It retains the same twelve columns and formula protection, but allows 8,000 characters in the message cell. Its same-ID deduplication still only covers webhook retries, not repeat browser submissions.
2. Install the matching API with production credentials through the separately approved release process, or agree an isolated preview API that does not deliver to production. The new API accepts old clients without duplicating their already-embedded context.
3. Release frontend and both versioned shared scripts together. No consent category, advertising permission, tracking ID or marketing subscription behavior changes.
4. Complete visual/browser regression, team review, and one explicitly agreed end-to-end enquiry through inbox, Sheets and conversion reporting. A local mocked API pass does not establish those outcomes.

Production promotion, live test submissions and Apps Script publication remain outside this implementation step.

## Changes

- Attribution follows last tagged arrival: replace the campaign as one record, including landing page, and do not carry old GCLID/UTM values into a different campaign. Untagged navigation preserves the current consented record. Analytics/advertising categories remain separately gated.
- A pre-consent focus does not consume the form-start event. The first new eligible focus/input/change sends one start; starts and errors include the form ID. No pre-consent interactions are replayed.
- Optional room/support/duration and consented attribution have separately validated fields, outside the visitor's message budget. The server renders them into email and the existing Sheet message cell. The project message is never shortened to make room for metadata.
- Manual email fallback contains the same full details and attribution, offers a copyable version for mail apps with URI limits, and no longer opens automatically. Form values remain in the page after failure.
- A 20-second client deadline restores the submit button and says delivery is uncertain, because the enquiry may already have arrived. It never automatically resubmits. Concurrent pending submissions are suppressed. The Sheet timeout now also covers response-body consumption.
- Shared form/browser limits match the API. The API rejects oversized submitted fields instead of silently truncating identities or project text. Landing project text retains its existing 3,000-character limit; other messages may use 4,000.
- Mobile call/email options are visible, input boundaries exceed 3:1 contrast, date/project prompts are flexible, and copy distinguishes enquiries from confirmed bookings. Existing testimonial career credits are labelled and existing studio photography is more prominent on mobile. Original supplied paragraphs, real assets and business facts are retained.
- With JavaScript disabled the landing form shows an email/phone alternative and hides unusable submission controls.
- No email-first capture, marketing opt-in, automatic retry, live conversion configuration, new commercial claim or production deployment was added.

## Verification

Run from the repository root:

```
node --test tests/*.test.js
python tools/static_hygiene_check.py
python tools/gallery_integrity_check.py
git diff --check
```

All 26 Node tests pass. Both repository static audits, Node syntax checks and diff whitespace checks also pass. Automated regression covers same-tab multi-campaign attribution, category filtering, eligible start timing, controlled analytics fields, accepted/error/honeypot event semantics, maximum messages/context, explicit fallback, stalled requests, duplicate pending submits, oversize rejection, legacy payloads and the Apps Script message cap/formula protection/deduplication. Every delivery provider is mocked.

Existing Playwright suites remain in `tests/`; the measurement suite now expects structured context and checks mobile contact visibility. Browser execution was attempted but Chromium could not launch because its process-singleton socket was denied in this environment, including the escalated attempt. Therefore new visual layout, touch/reflow, no-JS rendered behavior and Firefox navigation are **not revalidated** here. Run those suites on an approved browser-capable environment before preview publication or release.

The repository has no package/build pipeline or checked-in GitHub Actions workflow. Node syntax checks and the repository's two static audits were used in addition to regression tests.

## Other review findings, unchanged

- `isAllowedOrigin` still permits any HTTPS `*.vercel.app` origin. Restrict it only after the actual preview hosts are verified; origin/timing/honeypot checks are not complete abuse protection. Rate limiting remains a separate backend review.
- The API's successful response establishes provider acceptance, not inbox delivery, Sheet receipt or a confirmed booking. Sheet failure remains non-fatal after email acceptance.
- Consent withdrawal reloads the page to unload tags. Unsent form values are lost on that reload, and no personal form data is persisted. Decide any draft-preservation approach explicitly rather than silently storing email or project text.
- Team decisions remain necessary for response expectations, inclusions/quoting, optional email-first marketing, conversion ownership/deduplication and coordinated end-to-end testing.
