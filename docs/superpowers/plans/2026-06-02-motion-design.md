# Motion Design Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Lenis smooth scroll and GSAP ScrollTrigger animations to `salvation-studios.html` following the approved motion design spec.

**Architecture:** All animation code lives in a single new `<script>` block at the bottom of `salvation-studios.html`. A CSS override block kills conflicting existing CSS animations. The existing IntersectionObserver reveal system is superseded by immediately marking all `.reveal` elements as `.visible`, so GSAP inline styles (higher specificity than CSS class rules) control the animation state throughout. The vanilla hero parallax scroll listener is removed and replaced with a ScrollTrigger scrub.

**Tech Stack:** Lenis 1.0.42 (CDN, @studio-freight/lenis), GSAP 3.12.5 (CDN), ScrollTrigger 3.12.5 (CDN plugin), single HTML file.

---

## File Structure

Single file modified: `salvation-studios.html`

Changes by area:
- `<head>`: new `<style>` block overriding conflicting CSS animations
- Existing `<script>` block (~line 1647): remove vanilla hero parallax listener, update anchor scroll to support Lenis
- Before `</body>`: three CDN `<script>` tags + one new GSAP `<script>` block

---

### Task 1: CSS override block

**Files:**
- Modify: `salvation-studios.html` — insert before `</head>` (line 923)

The existing CSS has `animation: fadeUp` on `.hero-tag`, `.hero-h1`. GSAP will replace these. The `scroll-behavior: smooth` on `html` must be `auto` so Lenis controls scrolling.

- [ ] **Step 1: Insert CSS override block before `</head>`**

  Add these lines immediately before line 923 (`</head>`):
  ```html
  <style>
  /* GSAP motion design — kill conflicting CSS animations */
  html      { scroll-behavior: auto; }
  .hero-img { animation: none; }
  .hero-tag { animation: none; opacity: 0; }
  .hero-h1  { animation: none; opacity: 0; }
  </style>
  ```

- [ ] **Step 2: Open in browser and confirm hero text is invisible on load**

  Open `salvation-studios.html` in a browser. Before JS runs, the hero tag and h1 should be invisible (opacity: 0 from CSS). The "Book a Session" button and "Explore the Rooms" button will still be visible — GSAP will set their initial state in Task 4.

---

### Task 2: Remove vanilla hero parallax + update anchor scroll

**Files:**
- Modify: `salvation-studios.html` — existing `<script>` block starting at line 1647

The existing vanilla `scroll` listener on `.hero-img` (around line 1716) will conflict with GSAP ScrollTrigger's scrub. Remove it. Also update anchor scroll to use Lenis when available.

- [ ] **Step 1: Remove the vanilla hero parallax listener**

  Find and delete this block (around lines 1715–1724):
  ```js
  // ── Subtle parallax on hero image ──
  const heroImg = document.querySelector('.hero-img');
  if (heroImg) {
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      if (y < window.innerHeight) {
        heroImg.style.transform = `scale(1) translateY(${y * 0.25}px)`;
      }
    }, { passive: true });
  }
  ```

- [ ] **Step 2: Update anchor scroll to support Lenis**

  In the smooth anchor scroll block (around lines 1661–1675), replace:
  ```js
  target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  ```
  With:
  ```js
  if (window.lenisInstance) {
    window.lenisInstance.scrollTo(target, { offset: 0 });
  } else {
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  ```

- [ ] **Step 3: Add three CDN scripts after the closing `</script>` of the existing script block**

  After the existing `</script>` tag (line 1742), add:
  ```html
  <!-- Lenis smooth scroll -->
  <script src="https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.42/dist/lenis.min.js"></script>
  <!-- GSAP core -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <!-- ScrollTrigger plugin -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
  ```

- [ ] **Step 4: Verify CDN scripts load**

  Open in browser → DevTools Console → type `gsap`. Should return the GSAP object. Type `Lenis`. Should return the Lenis class. No 404 errors in the Network tab.

---

### Task 3: GSAP init + Lenis setup + reduced motion gate

**Files:**
- Modify: `salvation-studios.html` — new `<script>` block after the three CDN tags, before `</body>`

- [ ] **Step 1: Open the GSAP script block with reduced motion gate**

  After the three CDN `<script>` tags, add:
  ```html
  <script>
  (function () {
    gsap.registerPlugin(ScrollTrigger);

    // Skip all animations if user prefers reduced motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
      return;
    }

    // Supersede existing IntersectionObserver: mark .reveal elements visible now.
    // GSAP inline styles have higher specificity than the .reveal.visible CSS rule,
    // so GSAP controls opacity/transform on elements it animates.
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
  ```

- [ ] **Step 2: Init Lenis (desktop only) and connect to GSAP**

  Continue inside the IIFE:
  ```js
    // ─── LENIS SETUP ───────────────────────────────────────────
    const isMobile = window.innerWidth < 768;
    let lenis = null;

    if (!isMobile) {
      lenis = new Lenis({
        lerp: 0.08,
        duration: 1.2,
        easing: t => t < 0.5
          ? 4 * t * t * t
          : 1 - Math.pow(-2 * t + 2, 3) / 2
      });
      window.lenisInstance = lenis;

      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(time => lenis.raf(time * 1000));
      gsap.ticker.lagSmoothing(0);
    }
  ```

- [ ] **Step 3: Verify Lenis is running**

  Reload in browser. Scrolling should feel inertia-based (momentum after releasing the scroll). DevTools: `window.lenisInstance` returns the Lenis object. On a viewport narrower than 768px (mobile emulation) it should scroll normally.

---

### Task 4: Hero load sequence

**Files:**
- Modify: `salvation-studios.html` — inside the new GSAP script block

- [ ] **Step 1: Set initial states for elements that lack CSS opacity:0**

  GSAP needs to set `.nav`, `.hero-book-btn`, and `.hero-btns` to invisible before animating them in. `.hero-tag` and `.hero-h1` are already `opacity: 0` via the CSS override from Task 1.

  Add inside the IIFE:
  ```js
    // ─── HERO INITIAL STATES ────────────────────────────────────
    gsap.set('.nav', { opacity: 0 });
    gsap.set('.hero-book-btn, .hero-btns', { opacity: 0, y: 28 });
  ```

- [ ] **Step 2: Split "Welcome to" text into its own span**

  The `.hero-h1` contains a bare text node "Welcome to\n" followed by the Salvation logo span. Wrap the text node in a span so it can be animated separately from the logo:
  ```js
    const h1 = document.querySelector('.hero-h1');
    const firstText = [...h1.childNodes].find(n => n.nodeType === 3 && n.textContent.trim());
    const welcomeSpan = document.createElement('span');
    welcomeSpan.textContent = firstText.textContent;
    h1.replaceChild(welcomeSpan, firstText);
  ```

- [ ] **Step 3: Build the hero load sequence timeline**

  ```js
    const heroTl = gsap.timeline({ defaults: { ease: 'power2.out' } });
    heroTl
      .to('.nav',               { opacity: 1, duration: 0.6 })
      .from('.hero-tag',        { y: 28, opacity: 0, duration: 0.8 }, 0.2)
      .from(welcomeSpan,        { y: 28, opacity: 0, duration: 0.8 }, 0.4)
      .from('.hero-salvation-wrap', { scale: 0.9, opacity: 0, duration: 1.0, ease: 'power3.out' }, 0.6)
      .to('.hero-book-btn',     { opacity: 1, y: 0, duration: 0.6 }, 1.0)
      .to('.hero-btns',         { opacity: 1, y: 0, duration: 0.6 }, 1.1);
  ```

- [ ] **Step 4: Verify hero load sequence in browser**

  Reload page. Elements should appear in sequence: nav fades in → "Brighton, UK" tag slides up → "Welcome to" slides up → Salvation logo scales in → buttons fade up. Timing should feel cinematic, roughly 1.5s total.

---

### Task 5: Hero parallax, scroll fade-out, and mouse orb parallax

**Files:**
- Modify: `salvation-studios.html` — inside the new GSAP script block

- [ ] **Step 1: Hero image parallax via ScrollTrigger scrub**

  ```js
    // ─── HERO PARALLAX ──────────────────────────────────────────
    gsap.to('.hero-img', {
      y: '40%',
      ease: 'none',
      scrollTrigger: {
        trigger: '.hero',
        start: 'top top',
        end: 'bottom top',
        scrub: true
      }
    });
  ```

- [ ] **Step 2: Hero content fades out over first 30% of scroll**

  ```js
    gsap.to('.hero-content', {
      opacity: 0,
      ease: 'none',
      scrollTrigger: {
        trigger: '.hero',
        start: 'top top',
        end: '30% top',
        scrub: true
      }
    });
  ```

- [ ] **Step 3: Mouse parallax on glow orbs**

  ```js
    // ─── MOUSE ORB PARALLAX ─────────────────────────────────────
    const orb1 = document.querySelector('.orb-1');
    const orb2 = document.querySelector('.orb-2');
    if (orb1 && orb2) {
      let tx1 = 0, ty1 = 0, tx2 = 0, ty2 = 0;
      let mx = 0, my = 0;
      document.addEventListener('mousemove', e => {
        mx = (e.clientX / window.innerWidth  - 0.5) * 2;
        my = (e.clientY / window.innerHeight - 0.5) * 2;
      });
      gsap.ticker.add(() => {
        tx1 += (mx * 20 - tx1) * 0.05;
        ty1 += (my * 20 - ty1) * 0.05;
        tx2 += (-mx * 20 - tx2) * 0.05;
        ty2 += (-my * 20 - ty2) * 0.05;
        gsap.set(orb1, { x: tx1, y: ty1 });
        gsap.set(orb2, { x: tx2, y: ty2 });
      });
    }
  ```

- [ ] **Step 4: Verify in browser**

  - Scroll down slowly from hero — background image moves at slower pace than the page (parallax depth).
  - Hero text and buttons fade out as you scroll through the first ~30% of the page.
  - Move mouse around hero area — purple glow orbs follow with a ~0.05 lerp lag (smooth, not instant).

---

### Task 6: Welcome section animations

**Files:**
- Modify: `salvation-studios.html` — inside the new GSAP script block

- [ ] **Step 1: Word-by-word headline stagger**

  This utility splits a heading's child nodes into per-word `<span>` elements while preserving `<br>` and `<em>` tags:
  ```js
    // ─── WELCOME SECTION ────────────────────────────────────────
    function splitIntoWordSpans(el) {
      const nodes = [...el.childNodes];
      el.innerHTML = '';
      nodes.forEach(node => {
        if (node.nodeType === 3) {
          node.textContent.split(' ').forEach((word, i, arr) => {
            if (!word) return;
            const span = document.createElement('span');
            span.style.display = 'inline-block';
            span.textContent = word;
            el.appendChild(span);
            if (i < arr.length - 1) el.appendChild(document.createTextNode(' '));
          });
        } else if (node.nodeName === 'BR') {
          el.appendChild(document.createElement('br'));
        } else {
          const wrap = document.createElement('span');
          wrap.style.display = 'inline-block';
          wrap.appendChild(node.cloneNode(true));
          el.appendChild(wrap);
        }
      });
      return el.querySelectorAll('span');
    }

    const welcomeH2 = document.querySelector('.welcome .h2-serif');
    const h2Words = splitIntoWordSpans(welcomeH2);

    gsap.from(h2Words, {
      y: 40,
      opacity: 0,
      duration: 0.8,
      stagger: 0.1,
      ease: 'power2.out',
      scrollTrigger: { trigger: welcomeH2, start: 'top 80%' }
    });
  ```

- [ ] **Step 2: Body paragraph stagger**

  ```js
    gsap.from('.welcome .body-text p', {
      y: 30,
      opacity: 0,
      duration: 0.8,
      stagger: 0.15,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.welcome .body-text', start: 'top 80%' }
    });
  ```

- [ ] **Step 3: Stats counter from 0**

  The three `.stat-n` elements contain "6", "5yr", "13m". Animate the numeric portion:
  ```js
    const statDefs = [
      { el: document.querySelectorAll('.stat-n')[0], end: 6,  suffix: ''   },
      { el: document.querySelectorAll('.stat-n')[1], end: 5,  suffix: 'yr' },
      { el: document.querySelectorAll('.stat-n')[2], end: 13, suffix: 'm'  }
    ];
    statDefs.forEach(({ el, end, suffix }) => {
      const counter = { val: 0 };
      ScrollTrigger.create({
        trigger: el,
        start: 'top 85%',
        once: true,
        onEnter() {
          gsap.to(counter, {
            val: end,
            duration: 1.5,
            ease: 'power2.out',
            onUpdate() { el.textContent = Math.round(counter.val) + suffix; }
          });
        }
      });
    });
  ```

- [ ] **Step 4: Photo stack curtain wipe**

  ```js
    ScrollTrigger.create({
      trigger: '.welcome-photo-stack',
      start: 'top 75%',
      once: true,
      onEnter() {
        gsap.fromTo('.wp-main',
          { clipPath: 'inset(0 100% 0 0)' },
          { clipPath: 'inset(0 0% 0 0)', duration: 1.2, ease: 'power3.out' }
        );
        gsap.fromTo('.wp-accent',
          { clipPath: 'inset(0 100% 0 0)' },
          { clipPath: 'inset(0 0% 0 0)', duration: 1.2, ease: 'power3.out', delay: 0.25 }
        );
      }
    });
  ```

- [ ] **Step 5: Verify welcome section in browser**

  Scroll to the welcome section. Headline words ("A", "labour", "of", "love") should stagger up one by one. Paragraphs fade up in sequence. Stats count from 0 up to their final values. Main photo reveals with a left-to-right curtain wipe; accent photo follows 250ms later.

---

### Task 7: Rooms section animations

**Files:**
- Modify: `salvation-studios.html` — inside the new GSAP script block

- [ ] **Step 1: Section header slides in from left**

  ```js
    // ─── ROOMS SECTION ──────────────────────────────────────────
    gsap.from('.rooms-header', {
      x: -40,
      opacity: 0,
      duration: 0.9,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.rooms-header', start: 'top 85%' }
    });
  ```

- [ ] **Step 2: Live Room feature card**

  ```js
    gsap.from('.live-room-feature img', {
      scale: 1.08,
      opacity: 0,
      duration: 1.2,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.live-room-feature', start: 'top 80%' }
    });
    gsap.from('.live-room-info', {
      y: 40,
      opacity: 0,
      duration: 0.9,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.live-room-feature', start: 'top 65%' }
    });
  ```

- [ ] **Step 3: Room card stagger**

  ```js
    gsap.from('.room-card', {
      y: 50,
      opacity: 0,
      duration: 0.8,
      stagger: 0.08,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.rooms-grid', start: 'top 80%' }
    });
  ```

- [ ] **Step 4: Writing card stagger**

  ```js
    gsap.from('.writing-card', {
      y: 50,
      opacity: 0,
      duration: 0.8,
      stagger: 0.08,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.writing-rooms', start: 'top 80%' }
    });
  ```

- [ ] **Step 5: Verify rooms in browser**

  Scroll to rooms. "Every room, purpose-built" header should slide in from the left. Live Room image scales 1.08→1 as it arrives, then text info slides up. Three room cards stagger up left-to-right at 80ms intervals. Writing room cards do the same.

---

### Task 8: Neve + In-Room animations

**Files:**
- Modify: `salvation-studios.html` — inside the new GSAP script block

- [ ] **Step 1: Neve image curtain wipe**

  ```js
    // ─── NEVE SECTION ────────────────────────────────────────────
    ScrollTrigger.create({
      trigger: '.neve-bg',
      start: 'top 75%',
      once: true,
      onEnter() {
        gsap.fromTo('.neve-bg > img',
          { clipPath: 'inset(0 100% 0 0)' },
          { clipPath: 'inset(0 0% 0 0)', duration: 1.4, ease: 'power3.out' }
        );
      }
    });
  ```

- [ ] **Step 2: Neve text block stagger**

  ```js
    gsap.from(['.neve-eyebrow', '.neve-title', '.neve-body', '.neve-facts > div'], {
      y: 30,
      opacity: 0,
      duration: 0.9,
      stagger: 0.07,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.neve-content', start: 'top 75%' }
    });
  ```

- [ ] **Step 3: In-Room section header**

  ```js
    // ─── IN-ROOM SECTION ─────────────────────────────────────────
    gsap.from('.in-room > .reveal', {
      y: 40,
      opacity: 0,
      duration: 0.9,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.in-room', start: 'top 80%' }
    });
  ```

- [ ] **Step 4: In-Room photos parallax**

  ```js
    document.querySelectorAll('.in-room-photo img').forEach(img => {
      gsap.to(img, {
        y: '20%',
        ease: 'none',
        scrollTrigger: {
          trigger: img.closest('.in-room-photo'),
          start: 'top bottom',
          end: 'bottom top',
          scrub: true
        }
      });
    });
  ```

- [ ] **Step 5: In-Room photos fade up stagger**

  ```js
    gsap.from('.in-room-photo', {
      y: 40,
      opacity: 0,
      duration: 0.9,
      stagger: 0.12,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.in-room-grid', start: 'top 80%' }
    });
  ```

- [ ] **Step 6: Verify Neve + In-Room in browser**

  Scroll to Neve — Neve console photo should wipe in left-to-right over ~1.4s. Label, title, body, and facts stagger up in sequence. Scroll to In-Room — photos fade in staggered. As you scroll through them, the images should visibly move at a slower rate than the page (parallax depth).

---

### Task 9: Testimonials, Gallery, Services, Booking Band — close IIFE

**Files:**
- Modify: `salvation-studios.html` — inside the new GSAP script block

- [ ] **Step 1: Testimonials section header**

  Note: individual testimonial `.testi-card` elements live inside a continuously scrolling CSS marquee. Adding ScrollTrigger reveals to marquee cards conflicts with the infinite CSS animation, so only the section header is animated with GSAP.

  ```js
    // ─── TESTIMONIALS ────────────────────────────────────────────
    gsap.from('.testi-header', {
      y: 40,
      opacity: 0,
      duration: 0.9,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.testi-header', start: 'top 80%' }
    });
  ```

- [ ] **Step 2: Gallery wave stagger**

  ```js
    // ─── GALLERY ─────────────────────────────────────────────────
    gsap.from('.gp', {
      scale: 0.95,
      opacity: 0,
      duration: 0.8,
      stagger: 0.06,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.gallery-mosaic', start: 'top 80%' }
    });
  ```

- [ ] **Step 3: Services cards stagger**

  ```js
    // ─── SERVICES ────────────────────────────────────────────────
    gsap.from('.svc-card', {
      y: 30,
      opacity: 0,
      duration: 0.8,
      stagger: 0.08,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.services-grid', start: 'top 80%' }
    });
  ```

- [ ] **Step 4: Booking Band**

  ```js
    // ─── BOOKING BAND ────────────────────────────────────────────
    gsap.from('.booking-content', {
      scale: 0.97,
      opacity: 0,
      duration: 1.0,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.booking-band', start: 'top 75%' }
    });
  ```

- [ ] **Step 5: Close the IIFE and script tag**

  ```js
  })();
  </script>
  ```

- [ ] **Step 6: Full page scroll-through test**

  Scroll from top to bottom verifying each section:
  - [ ] Hero: load sequence plays on page load (nav → tag → "Welcome to" → logo → buttons)
  - [ ] Hero: background photo moves slower than page (parallax)
  - [ ] Hero: text fades out as you leave the hero section
  - [ ] Hero: glow orbs follow mouse with soft lag
  - [ ] Welcome: "A labour of love" words stagger up one by one
  - [ ] Welcome: body paragraphs fade up in sequence
  - [ ] Welcome: stats count 0→6, 0→5yr, 0→13m
  - [ ] Welcome: photos reveal with curtain wipe, accent follows 250ms later
  - [ ] Rooms: header slides in from left
  - [ ] Rooms: Live Room image scales 1.08→1, info slides up
  - [ ] Rooms: three room cards stagger up at 80ms intervals
  - [ ] Rooms: writing cards stagger up
  - [ ] Neve: console photo wipes in left-to-right
  - [ ] Neve: text lines stagger up
  - [ ] In-Room: photos fade in staggered, images parallax as you scroll through
  - [ ] Testimonials: section header fades up
  - [ ] Gallery: images wave-stagger in at 60ms intervals, scale 0.95→1
  - [ ] Services: six cards stagger up at 80ms intervals
  - [ ] Booking: content scales 0.97→1 and fades in
