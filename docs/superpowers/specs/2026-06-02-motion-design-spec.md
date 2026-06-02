# Salvation Studios — Motion Design Spec
**Date:** 2026-06-02
**Scope:** Add premium motion & scroll animations to `salvation-studios.html`

---

## Libraries

| Library | Version | How loaded |
|---------|---------|------------|
| Lenis | latest | CDN (`@studio-freight/lenis`) |
| GSAP | 3.x | CDN (`gsap`) |
| ScrollTrigger | 3.x | CDN (GSAP plugin) |

No npm install required. Both added via `<script>` tags before the closing `</body>`.

---

## Animation Style

- **Intensity:** Cinematic & Bold (B)
- **Rooms treatment:** Staggered scroll reveal (A) — no pinning
- **Easing:** `power2.out` / `power3.out` (Apple-like deceleration)
- **Reduced motion:** All GSAP animations skipped if `prefers-reduced-motion: reduce`
- **Lenis on mobile:** Disabled below 768px for performance

---

## Section-by-Section

### 1. Lenis Setup
- Instantiate Lenis with `lerp: 0.08`, `duration: 1.2`, `easing: easeInOutCubic`
- Tick inside `requestAnimationFrame` loop
- Connect to GSAP ticker: `gsap.ticker.add((time) => lenis.raf(time * 1000))`
- Disable GSAP's `lagSmoothing`

### 2. Hero
- **On load sequence:** Nav fades in (0.6s) → "Welcome to" fades+slides up (0.8s) → Salvation logo scales 0.9→1 + fades in (1.0s, 0.2s delay) → CTA button fades up (0.6s, 0.4s delay)
- **Parallax:** `.hero-img` moves at `y: scrollY * 0.4` via ScrollTrigger scrub
- **Scroll fade-out:** `.hero-content` opacity 1→0 over first 30% of scroll via ScrollTrigger scrub
- **Mouse parallax:** Glow orbs move max ±20px on mousemove (0.05 lerp factor)

### 3. Welcome — "A labour of love"
- Headline (`h2-serif`) words split by spaces, each word animates `y: 40→0, opacity: 0→1`, 100ms stagger
- Body paragraphs: `y: 30→0, opacity: 0→1`, staggered 150ms, triggered when 80% in view
- Stats: counter animation from 0 to final value over 1.5s when in view (use GSAP `to` on a JS object)
- Photo stack: main photo clip-path `inset(0 100% 0 0)→inset(0 0% 0 0)` (curtain wipe), accent photo same effect 250ms later

### 4. Rooms
- Section header: `x: -40→0, opacity: 0→1` on scroll enter
- `.live-room-feature`: image scale `1.08→1.0` + fade in, text slides up 40px
- Room cards: stagger `y: 50→0, opacity: 0→1`, 80ms between each card
- Writing cards: same stagger treatment

### 5. Neve
- Image: clip-path curtain wipe left-to-right (same as photo stack)
- Text block: lines stagger up 60ms apart

### 6. In-Room
- Photos: parallax at 80% scroll speed (`y: scrollY * 0.2`)
- Text: stagger fade-up

### 7. Testimonials
- Quote cards: `y: 40→0, opacity: 0→1`, 100ms stagger
- Star ratings animate in first (scale 0→1), then quote text fades

### 8. Gallery
- Images: `scale: 0.95→1, opacity: 0→1`, wave stagger 60ms per image, triggered when group enters view

### 9. Services
- Service items: stagger `y: 30→0, opacity: 0→1`, 80ms apart

### 10. Booking Band
- Container: `scale: 0.97→1, opacity: 0→1` on scroll enter

---

## Implementation Notes

- All animation code lives in a single `<script>` block at the bottom of `salvation-studios.html`, after existing scripts
- Existing `.reveal` CSS class system replaced by GSAP (set initial states via GSAP, not CSS opacity:0)
- No new files created — single HTML file stays single HTML file
- `prefers-reduced-motion` check wraps entire animation init block

---

## Out of Scope

- Pinned sections (user chose stagger over pin)
- SplitText character-level reveals (requires paid GSAP)
- Horizontal scroll sections
- Page transition animations
