# Design QA — Phill Brown Signature Sessions

## Comparison target

- Source visual truth paths:
  - `/home/acm/Downloads/Screenshot 2026-09-10 at 17.58.14.png`
  - `/home/acm/Downloads/Screenshot 2026-09-10 at 17.58.26.png`
  - `/home/acm/Downloads/Screenshot 2026-09-10 at 17.58.31.png`
  - `/home/acm/Downloads/Screenshot 2026-09-10 at 17.59.01.png`
- Implementation route: `/signature-sessions-phill-brown/`
- Implementation screenshot paths:
  - `.qa/phill-brown-desktop-pass1.png`
  - `.qa/phill-brown-desktop-tall-pass4.png`
  - `.qa/phill-brown-mobile-hero-pass1.png`
  - `.qa/phill-brown-mobile-tall-pass2.png`
- State: public dark campaign page, default/idle form state, no authentication.

## Viewport and normalization

- Each source screenshot is `3838 × 1932` pixels and appears to be a `@2x` capture, corresponding to approximately `1919 × 966` CSS pixels.
- The hero source was normalized to `1920 × 966` pixels in `.qa/reference-hero-1920x966.png` for comparison with the `1920 × 966` Firefox implementation capture at density `1`.
- Desktop long-page review used a `1920 × 8000` CSS-pixel Firefox viewport at density `1`; crops were taken at native scale for focused comparison.
- Responsive review used `390 × 844` and `390 × 8000` CSS-pixel Firefox viewports at density `1`. No mobile source was supplied, so mobile was reviewed for hierarchy, overflow and touch usability rather than pixel fidelity.

## Evidence

- Full-view comparison: `.qa/full-comparison-pass2.png` places the four-screen source overview beside an implementation overview. `.qa/hero-comparison-pass1.png` provides the normalized above-the-fold comparison.
- Focused form comparison: `.qa/form-comparison-pass2.png` places the normalized source form beside the implementation form at native desktop scale.
- Focused gallery iteration: `.qa/gallery-comparison-fixed.png` places the pre-fix empty gallery capture beside the post-fix loaded gallery at the same `1920 × 8000` viewport and crop.

## Findings

- No actionable P0, P1 or P2 findings remain.
- Fonts and typography: the implementation preserves the source's cream display hierarchy and lightweight supporting copy. Cormorant Garamond provides the editorial display treatment; Nunito keeps the compact labels and body copy legible. Wrapping remains intentional at desktop and mobile.
- Spacing and layout rhythm: the source's sparse, offset composition is retained while the long fixed canvas is reorganized into responsive sections. Square borders, tight labels and generous black space remain consistent. No overlap or horizontal clipping was visible at `1920px` or `390px` widths.
- Colors and visual tokens: near-black, charcoal, smoke-grey and warm cream map directly to the source. The generated halftone/grunge texture remains low contrast behind readable content. No campaign-specific gradients or generic rounded cards were introduced.
- Image quality and asset fidelity: authentic Salvation Studios and Phill Brown photography is used throughout with correct dimensions and intentional crops. The only generated bitmap is the non-semantic background texture; it contains no text, logos or substitute imagery.
- Copy and content: the source offer, credit list, Single package, EP package and enquiry fields are present. Extra headings and supporting copy clarify the conversion path without changing the offer.
- Accessibility and behavior: semantic headings, labelled required fields, a fieldset/legend for package choice, visible focus styles, a skip link, descriptive alt text and practical mobile tap targets are present. The primary CTA, package CTAs and form targets resolve; shared enquiry-handler structure and required fields pass the repository checks. A real enquiry was not submitted during QA to avoid creating a production lead.

## Comparison history

1. Pass 1 — P2: the three lower proof images remained deferred in the unusually tall full-page browser capture, leaving bordered empty frames and exposed alt text. Evidence: `.qa/phill-brown-gallery-detail-pass2.png`.
2. Fix — removed native lazy loading from the three compact gallery assets (approximately 816 KB combined) so campaign proof appears reliably while retaining asynchronous decoding.
3. Pass 2 — the same `1920 × 8000` viewport and crop show all three images rendered with correct crops, labels and borders. Evidence: `.qa/phill-brown-gallery-detail-pass4.png` and `.qa/gallery-comparison-fixed.png`.

## Open questions

- New Phill photography mentioned by the client has not yet been supplied. The current build uses genuine existing project assets and can accept direct asset swaps without restructuring the page.
- The supplied Box link currently does not resolve publicly; the matching local Phill drum-session asset already in the repository is used instead.

## Implementation checklist

- [x] Match the source campaign palette, texture and typographic hierarchy.
- [x] Preserve the source offer details and form fields.
- [x] Use authentic project photography and responsive crops.
- [x] Validate desktop and mobile layouts.
- [x] Verify clean routing, no-index protection and shared enquiry-form structure.
- [x] Run repository hygiene, gallery and Node tests.

## Follow-up polish

- Replace or expand the current photo set when the client's new Phill photography arrives.

final result: passed
