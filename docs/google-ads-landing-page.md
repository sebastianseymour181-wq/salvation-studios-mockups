# Google Ads landing page — first draft, 4 November 2026

Review URL: https://salvation-studios-mockups-three.vercel.app/google-ads/

Deployment: `dpl_83cJKT2uBmc8nudqHYsoDNiXSApn` (staging, READY). Source commit: `438d05fe39061ee4a905bf5fd602489665df4213`, branch `feature/google-ads-landing-2026-11-04`.

## Copy and design

Eliza's seven-section structure and all 37 supplied headings/copy passages are retained verbatim apart from typographic apostrophes and visual emphasis. Terra (`gpt-6.1-terra`, high reasoning), explicitly requested by the user, supplied only additional CTA labels, optional booking-details text, dates help and the project placeholder. Its initial rewritten prose was not used.

The page extends the existing shared purple palette, serif headings, Nunito body text and button treatment. It uses genuine existing studio photography and contiguous excerpts from the existing Gavin Monaghan and Phill Brown testimonials. No prices, turnaround promises or new claims have been added.

Reference review:

- Strongroom: https://www.strongroom.com/studio/strongroom-1/ — clear studio context, testimonials, visible booking CTA, dates and practical requirements make enquiries actionable.
- Metropolis: https://www.thisismetropolis.com/contact/ — service categories and tailored follow-up fields qualify distinct booking needs.
- Shoreditch Recording Works: https://www.shoreditchrecordingworks.com/ — approachable project-led enquiry direction, as described in Eliza's brief; initial site retrieval succeeded, subsequent retrievals timed out.

The form uses Salvation's established enquiry endpoint and source-page attribution, with name/email/project required, a service choice defaulting to not sure, optional dates, and optional artist/company and phone under a disclosure. Existing enquiry start/submit/error analytics events are reused. No new advertising conversion tag or advertising campaign was configured.

## Verification

- All supplied copy passages checked against extracted page text.
- HTML assets, fragment targets, unique IDs and form labels checked.
- Static hygiene check passes after classifying this campaign and the existing Sean campaign as noindex.
- Gallery integrity check passes; all four existing Node enquiry tests pass.
- Published page and 20 referenced assets return HTTP 200 and byte-match source; noindex header verified.
- Invalid-timing enquiry request returns expected HTTP 400; no successful lead was sent.
- Responsive rules cover mobile/tablet layouts, single-column form/cards, readable 16px input text, reduced motion, focus visibility and responsive AVIF/WebP hero sources.
- Browser visual and interactive verification was unavailable: computer-use inventory returned no apps or browsers. Mobile appearance and a successful end-to-end enquiry remain unverified.

Only the test alias was assigned. Both `www.salvationstudios.co.uk` and `salvationstudios.co.uk` were read back after deployment and retain baseline `dpl_GkEs219MWCKPXc6xmevYYSHSGHvR`. The page is excluded from the navigation and sitemap and marked noindex. Promotion to live has not been requested.
