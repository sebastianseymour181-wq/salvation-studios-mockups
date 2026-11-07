# Eliza's landing-page revision, 6 November 2026

Scope: `/google-ads/` on `feature/google-ads-landing-2026-11-04`, test only. No production promotion, integration changes or real enquiry submissions.

## Changes

- Replaced the hero opening with Eliza's supplied wording and studio-of-choice sentence.
- Moved the enquiry section immediately after the hero/early testimonial. Its form markup is byte-for-byte unchanged from `e272d6b7e1e1a49876cc8272bd520a5de3d07d81`.
- Added a left-hand studio/services jump link beside the form.
- Removed planning and introductory services copy. Four services now use compact image/title cards, with an accessible/bespoke payment-plan callout.
- Merged the two studio sections using Eliza's two supplied paragraphs, with a small Brighton accommodation callout. No prices, accommodation guarantees or payment terms were invented.
- Added 35 rolling artist names. The existing studio-owned “Artists We've Worked With” list supplies 34 names; Eliza's email supplies Fontaines D.C. Producer career credits remain labelled and are not treated as studio clients.
- Added a keyboard-operable pause/resume control, pause on hovering the moving list, a static no-JavaScript fallback and live reduced-motion preference handling. Duplicated animation content is hidden from assistive technology.

Source: Eliza's 6 November 2026 email, “Re: Website Setup & Google Ads Integration”, message ID `1a1b0e8be1997512`; existing `salvation-studios.html` studio-client list.

## Verification

Passed locally:
- `node --test tests/*.test.js`: 29 tests, including five new layout/copy/credits logic regressions.
- JavaScript syntax checks for the new script and updated/new browser regressions.
- HTML nesting, duplicate IDs, form labels, fragment destinations and section-order checks.
- Exact form-markup comparison with baseline; all existing analytics CTA identifiers retained.
- Referenced local assets verified against the repository's complete committed tree, with the new script accounted for.
- Changed HTML/CSS whitespace checks.

Browser verification remains blocked: Chromium exits with `process_singleton_posix.cc: socket() failed: Operation not permitted`, including a reviewed escalated launch. Responsive rules are implemented, but rendered mobile/desktop fit, actual animation, browser navigation and interactive measurement have not been verified in this execution environment. New read-only `tests/landing-credits.browser.cjs` covers 1440, 1024, 768, 390 and 320 pixel layouts, motion preferences and no-JavaScript behavior. The existing navigation test now expects five post-hero sections and checks the new sidebar link.

On 7 November, verification was repeated against a full Git checkout. Static hygiene passed for all 36 HTML files, 22 sitemap routes and 63 old routes. Gallery integrity passed for 19 homepage images, 95 session images and 37 gear images. All 29 Node tests and `git diff --check` passed again. No gallery or existing assets changed. No real lead was submitted; all enquiry unit delivery was mocked.
