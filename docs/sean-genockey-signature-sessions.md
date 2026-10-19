# Sean Genockey Signature Sessions

## Review build

- Test page: https://salvation-studios-mockups-three.vercel.app/signature-sessions-sean-genockey/
- Deployment: `dpl_3Ucr7XH3EPysyRRaZAqipnRE6MUr` (staging, READY).
- Source branch: `feature/sean-genockey-signature-sessions-2026`.
- Source commit: `3a62c9d9a3376f594953b1d958fc1e681ba03bdb`.
- Live baseline retained: `dpl_GkEs219MWCKPXc6xmevYYSHSGHvR` on both `www.salvationstudios.co.uk` and `salvationstudios.co.uk`.

## Page and packages

The Phill Brown page was used as the template. The Single and EP inclusions are identical apart from the producer name. Sean’s supplied biography and credits are included; the longer biography is expandable. No session count was supplied for Sean, so Phill’s two-session scarcity claim is not carried over.

The page uses the existing campaign styling, with a small scoped stylesheet for Sean’s longer name and expandable biography. It is excluded from indexing and has not been added to the main navigation or sitemap.

## Enquiry connection

The existing form posts to `/api/enquiry` with Sean’s campaign name, selected package, music link and source path. A host-conditional rewrite forwards `/api/enquiry` on the canonical test hostname to the established live Salvation enquiry service. Production domains do not match that rule. This avoids copying production credentials to preview environments.

Workbook: https://docs.google.com/spreadsheets/d/1-uk-Y-Pb1C0wLwHBoIeCRVE5xBYGVxf_z7TME8fVfC4/edit

New tab: `Sean Genockey Signature Sessions` (`sheetId=1026202601`). It follows the existing Phill tab’s formatting, frozen header, filter and dimensions. Its A1 formula displays the main enquiry headers and filters incoming records by the Sean source path, including clean, trailing-slash and `.html` URLs. It shows an empty row when no matching enquiries exist. The authoritative records, status and notes are managed in `Enquiries`.

## Completed checks

- Package inclusions compared against the existing page: exact match after replacing producer name.
- Form labels, anchor targets and referenced local assets checked.
- Test page returns HTTP 200 with `X-Robots-Tag: noindex, nofollow`.
- Deployed page SHA-256 matches the local HTML.
- Both stylesheets return HTTP 200.
- A deliberately invalid-timing request through the test-host enquiry route returns the existing handler’s expected HTTP 400 validation response; no email or lead was sent.
- New Sheet formula and all 12 displayed column headers read back successfully.
- Both live aliases checked after test assignment: retain the original baseline.
- Browser visual QA unavailable: the computer-use tool reported no browsers. No full successful enquiry was submitted.

## Supplied photos added — 19 October 2026

Access to all six Drive files is now working. All six supplied photos replace the temporary studio photographs across the hero, biography and four-image gallery. Source mappings are recorded in `photos/campaign-sean-genockey-2026/sources.json`.

Images retain their original composition and have been resized to WebP, with 800px responsive alternatives. The hero shows Sean playing acoustic guitar; the biography shows him at the Neve console. Gallery images show electric-guitar recording, acoustic-guitar development, amplifier adjustment and a further guitar session. CSS focal positions keep Sean within the portrait and tall gallery frames. The social preview uses Sean’s acoustic live-room image on the test host; update that host when promoting to production.

Browser visual QA remains unavailable because no browsers are exposed by the computer-use tool. The package inclusions, biography, enquiry form and Sheets connection are unchanged by this photo update.

Only the test hostname was assigned. Publish to the official live domains after the user approves the completed review page. Before promotion, use production configuration so ordinary enquiries have the existing production email and Sheets variables.
