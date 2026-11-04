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
