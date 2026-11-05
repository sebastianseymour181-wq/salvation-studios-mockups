# Enquiry improvements, 5 November 2026

## Current release scope

The revised implementation is frontend-only, based on `e45069ded89b1505a2900f457f22a8543a0a2ed3` on `feature/google-ads-landing-2026-11-04`. The API, Sheet helper, Apps Script and Vercel configuration are unchanged from that baseline. An earlier, undeployed structured-context patch was prepared, but it is not the implementation selected for this release.

The test alias routes enquiries to the established live API. The revised frontend uses that API's supported message field and respects both its 4,000-character combined-message limit and its 12,000-byte whole-request limit. There is no API/Apps Script rollout dependency for this version and no production code/configuration change.

**Important limit:** the project text, optional session answers and consented campaign context share the 4,000-character transport budget. A 4,000-character project can only be accepted if no additional context is required and the whole request fits the byte limit. If either limit is exceeded, validation explains that the visitor needs to shorten the details, keeps every field and offers a complete manual email fallback. Nothing is silently cut or omitted and no request is sent.

## Implemented changes

- Attribution uses last tagged arrival: a new campaign replaces the record, including landing page, so an old GCLID/UTM is not mixed with a later campaign. Untagged navigation preserves the current consented record. Analytics/advertising categories remain separately gated.
- A pre-consent focus does not consume the start event. The first new eligible focus/input/change sends one start; starts and errors include the form ID. No pre-consent interactions are replayed.
- Optional room/support/duration and consented attribution are included completely with the message, within the existing transport limits. Only supported fields are sent to the endpoint, avoiding duplicated context and private details in the request.
- Manual fallback includes original project text and the same optional/campaign details exactly once. It offers a complete copyable version for mail apps with URI limits and never opens automatically. Form values remain after failure or size validation.
- A 20-second client deadline restores the submit button and explains that delivery is uncertain because the enquiry may already have arrived. It never automatically resubmits. Concurrent pending submissions are suppressed.
- Shared form limits match the established API. The frontend validates assembled fields before sending; the unchanged API still has its historical truncation behavior for callers that bypass the browser. The landing project field retains its 3,000-character maximum, subject to the combined budget above.
- Mobile call/email options are visible; field borders exceed 3:1 contrast; date/project prompts are flexible; and copy distinguishes enquiries from bookings. Existing testimonial career credits are labelled and existing real studio photography is more prominent on mobile. Supplied paragraphs and business facts remain intact.
- With JavaScript disabled, the landing form displays an email/phone alternative and hides unusable submission controls.
- Both shared-script URL versions are updated across all HTML pages to prevent old/new tracking API skew.

No email-first capture, marketing opt-in, automatic retry, new commercial promise, conversion-account configuration or production deployment is included.

## Verification and publication status

Run from the repository root:

```
node --test tests/*.test.js
python tools/static_hygiene_check.py
python tools/gallery_integrity_check.py
git diff --check
```

Regression uses mocked delivery only. It covers multi-campaign attribution, category filtering, eligible starts, controlled analytics fields, success/error/honeypot semantics, exact message/context inclusion, character/UTF-8 byte limits, explicit fallback, stalled response bodies and duplicate pending submits. Repository static hygiene and gallery integrity checks are also required.

The Playwright measurement suite now checks complete bounded context and mobile contact visibility. Chromium could not launch in this environment because process-singleton sockets were denied, including the escalated launch attempt. New rendered layout, touch/reflow, no-JS behavior and Firefox navigation therefore require verification in an authorized browser-capable environment. Do not label source/unit tests a browser pass.

Publication has not yet occurred. Vercel metadata identifies the test project as `prj_irEokg6rEuf4PEHyAIsYWO3Rn5pp` in `team_uhiiLvDavq3mfahrblbHjjT3` (`lpd22664s-projects`). An explicit scoped read returned 403 requiring the user to approve team access. No credentials, permissions or access restrictions were bypassed.

The user approved one clearly labelled real enquiry to the normal studio enquiry inbox and connected Sheet. It must wait until the reviewed test deployment is ready, use a unique test marker, and not be repeated if the result is uncertain. Verify actual receipt separately from HTTP success. No real submission has been sent during implementation.

## Other findings, unchanged

- The API still permits any HTTPS `*.vercel.app` origin. Restrict only after actual preview hosts are verified; origin/timing/honeypot checks alone are not complete abuse protection. Rate limiting remains a backend review.
- API success means provider acceptance, not inbox delivery, Sheet receipt or confirmed booking. Sheet failure remains non-fatal after email acceptance.
- A repeated browser submit is not idempotent: a new submission ID can create another email and row. Webhook deduplication applies only to the same ID.
- Consent withdrawal reloads the page to unload tags; unsent form values are lost. No personal draft data is persisted. Agree any persistence behavior explicitly rather than silently storing email/project text.
- Response-time promises, inclusions/quoting, optional email-first marketing and conversion ownership remain team decisions. Account-side reporting requires separate verification by someone with access.
