# Google Ads and sitewide measurement upgrade — 4 November 2026

## Scope and release sequence

Implement and review on the existing test alias first. Preserve Eliza’s supplied landing-page wording. Include Sean Genockey Signature Sessions and the existing test-site changes in the final release review. Production promotion follows that review, not this implementation step.

1. Improve landing hierarchy: genuine sound-focused proof near the hero, tighter mobile image/spacing, more compact secondary sections, useful optional room/support/duration fields and practical booking information grounded in the existing site.
2. Install GTM-TKKWMVXR across all HTML pages using one shared, synchronous head entry point. Use basic Consent Mode: optional Google scripts are blocked until consent. The no-JavaScript iframe stays inert because no consent can be obtained without JavaScript.
3. Provide Accept all, Reject optional and granular Analytics/Advertising preferences, remember an explicit choice for 180 days, and expose Cookie settings in every footer. Withdrawal clears first-party Google measurement cookies/attribution and reloads to unload tags.
4. Track only accepted enquiry responses as salvation_enquiry_submit. Keep clicks/starts separate, exclude form personal data from dataLayer, carry consented campaign information across pages, and include it with enquiries without changing the established Sheets schema. No booking-confirmation event is invented: bookings are arranged by the studio team after enquiry.
5. Update the privacy notice and CSP, document the exact event and consent contract for Ollie, and ensure staged/test events can be excluded using environment and hostname.
6. Validate every page’s installation, fresh/reject/accept/granular/withdraw consent, mobile/desktop interaction, no pre-consent Google requests, attribution, successful/error form UI, and the Sean/Phill package forms. Verify the real GTM endpoint and distinguish website installation from unpublished/missing tags in Ollie’s container.
7. Deploy to the test alias, verify the deployed bundle and retain production aliases. Present the review links and remaining account-side checks before promotion.

## Design decisions

Use Google’s basic Consent Mode to block optional tracking before consent. Defaults are denied for analytics_storage, ad_storage, ad_user_data and ad_personalization, before the container can run. Ollie owns GA4/Ads IDs, tags and account-side conversion configuration. Website events identify enquiries, not confirmed bookings. The test-host API forwards to the established live enquiry handler; optional fields and attribution therefore travel in the existing message field for backward-compatible email/Sheets delivery.

References: https://developers.google.com/tag-platform/security/concepts/consent-mode ; https://developers.google.com/tag-platform/security/guides/consent ; https://developers.google.com/tag-platform/security/guides/csp ; https://ico.org.uk/media2/about-the-ico/documents/4032419/cookie-letters-project-phase-2-template-letter.pdf

## Executed and verified

Website implementation is complete on the test alias: https://salvation-studios-mockups-three.vercel.app/google-ads/

- Deployed source: `4435187ce57ca1f690ff29458321b4c4135d3576`.
- Deployment: `dpl_Fs2PEpTDvRmtWZHKeTmo2D5hjFzp` (staging, READY).
- Sitewide installation verified in Chromium on all 36 pages, with no pre-consent tracking requests. Static hygiene, gallery integrity and the four existing Node tests pass.
- Fresh, reject, granular, remembered and withdrawn consent states pass browser checks. With real tags, Analytics-only creates `_ga` cookies without `_gcl_` advertising cookies. With full permission, GTM and GA4 scripts return HTTP 200; GA4 measurement endpoints return HTTP 204/200. The deployed security policy produces no blocked-resource events during this test.
- All seven enquiry forms (landing page plus six existing forms/campaigns) pass intercepted-response tests: validation, error recovery, successful response, one canonical event, correct campaign package, and no form personal data in dataLayer. No real email/Sheet lead was sent.
- Desktop/mobile widths 320, 375, 390, 768, 1024 and 1440 pass reflow/action checks. A native touch-input sequence scrolls the page. Cookie preferences close using Escape. The main enquiry now starts around 2,090px down at 1440px and 3,678px at 390px; the earlier draft was around 5,088px / 7,622px.
- Eliza’s supplied paragraphs are retained. New planning and consent copy was supplied/reviewed by Terra on high reasoning. Genuine Phill Brown sound-focused excerpts appear early and in the testimonial section.
- Both official domains were read back after the test deployment and retain `dpl_GkEs219MWCKPXc6xmevYYSHSGHvR`.

### Final review / production gate

Review the landing page, cookie choices on the main site, and Sean Genockey Signature Sessions. The website event contract and remaining account-side trigger setup are in `docs/google-ads-measurement-handoff.md`. Ollie must configure/confirm the successful-enquiry conversion in GA4/Ads; a real coordinated enquiry receipt in email/Sheets and account reporting has not been tested. After this final review, promote the complete reviewed bundle using production configuration so the existing enquiry service retains its production credentials. No production promotion or message to Ollie has occurred in this task.

## Firefox content visibility correction

The reported missing content and dead anchors were reproduced in Firefox using the actual EasyList cosmetic selectors `.ads-header` and `.ads-section` (source: https://github.com/easylist/easylist/blob/master/easylist/easylist_general_hide.txt). Those names were mistakenly used for the page’s header and all six main content sections. With the selectors applied, Firefox reported zero visible sections and a document no taller than its viewport; the enquiry anchor changed the fragment but could not reveal a hidden target. A clean Firefox session did not exhibit that failure.

The page’s layout classes and internal field IDs now use the specific `ss-landing-` namespace. Public fragment targets, the `google-ads-enquiry-form` measurement ID and existing analytics action values remain stable. The stylesheet URL has a new version to refresh cached styling. Tracking and consent behaviour are unchanged.

`tests/landing-navigation.browser.cjs` exercises Firefox and Chromium at desktop/mobile widths, both with and without the matching EasyList rules, including wheel scrolling, visible content, settled anchor destinations and the privacy-page link. It tests the matching cosmetic rules directly; it does not inspect or modify the user’s Firefox profile or extensions.
