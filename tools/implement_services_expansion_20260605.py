#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SERVICE_LINKS = [
    ("Recording", "/services/recording/"),
    ("Mixing", "/services/mixing/"),
    ("Mastering", "/services/mastering/"),
    ("Live Videos", "/services/live-videos/"),
    ("Signature Sessions", "/services/signature-sessions/"),
    ("Giveaways & Offers", "/services/giveaways-offers/"),
    ("Accommodation and Hospitality", "/services/accommodation-hospitality/"),
]

SERVICE_DROPDOWN = """<li class=\"nav-dropdown\">
      <a href=\"/services/\" class=\"nav-dropdown-toggle\" aria-haspopup=\"true\">Services</a>
      <div class=\"nav-dropdown-menu\" aria-label=\"Studio services\">
        <a href=\"/services/recording/\">Recording</a>
        <a href=\"/services/mixing/\">Mixing</a>
        <a href=\"/services/mastering/\">Mastering</a>
        <a href=\"/services/live-videos/\">Live Videos</a>
        <a href=\"/services/signature-sessions/\">Signature Sessions</a>
        <a href=\"/services/giveaways-offers/\">Giveaways &amp; Offers</a>
        <a href=\"/services/accommodation-hospitality/\">Accommodation and Hospitality</a>
      </div>
    </li>"""

MOBILE_SERVICE_LINKS = """  <a href=\"/services/recording/\">Recording</a>
  <a href=\"/services/mixing/\">Mixing</a>
  <a href=\"/services/mastering/\">Mastering</a>
  <a href=\"/services/live-videos/\">Live Videos</a>
  <a href=\"/services/signature-sessions/\">Signature Sessions</a>
  <a href=\"/services/giveaways-offers/\">Giveaways &amp; Offers</a>
  <a href=\"/services/accommodation-hospitality/\">Accommodation and Hospitality</a>"""

SERVICES_FOOTER = """<div>
      <div class=\"footer-head\">Services</div>
      <ul class=\"footer-links\">
        <li><a href=\"/services/\">Services Overview</a></li>
        <li><a href=\"/services/recording/\">Recording</a></li>
        <li><a href=\"/services/mixing/\">Mixing</a></li>
        <li><a href=\"/services/mastering/\">Mastering</a></li>
        <li><a href=\"/services/live-videos/\">Live Videos</a></li>
        <li><a href=\"/services/signature-sessions/\">Signature Sessions</a></li>
        <li><a href=\"/services/giveaways-offers/\">Giveaways &amp; Offers</a></li>
        <li><a href=\"/services/accommodation-hospitality/\">Accommodation and Hospitality</a></li>
      </ul>
    </div>"""

STUDIO_FOOTER = """<div>
      <div class=\"footer-head\">Studio</div>
      <ul class=\"footer-links\">
        <li><a href=\"/spaces/\">Spaces Overview</a></li>
        <li><a href=\"/rooms/main-studio/\">Main Studio</a></li>
        <li><a href=\"/rooms/control-room/\">Control Room</a></li>
        <li><a href=\"/rooms/live-room/\">Live Room</a></li>
        <li><a href=\"/rooms/the-bunker/\">The Bunker</a></li>
        <li><a href=\"/rooms/writing-rooms/\">Writing Rooms</a></li>
        <li><a href=\"/equipment/\">Equipment</a></li>
      </ul>
    </div>"""

FIND_FOOTER = """<div>
      <div class=\"footer-head\">Find Us</div>
      <ul class=\"footer-links\">
        <li><a href=\"/contact/#enquiry-form\">Get in Touch</a></li>
        <li><a href=\"/contact/#enquiry-form\">Enquire about your next session</a></li>
        <li><a href=\"https://www.instagram.com/salvationmusicstudiosbtn/\">Instagram</a></li>
        <li><a href=\"https://www.facebook.com/profile.php?id=100093193308784\">Facebook</a></li>
        <li><a href=\"https://share.google/0pPGxHfIi8WZ4qw2y\">Brighton, UK</a></li>
      </ul>
    </div>"""

SERVICE_DATA = {
    "recording": {
        "title": "Recording Services Brighton | Salvation Studios",
        "description": "World-class recording sessions at Salvation Studios Brighton with the Main Studio live room, Neve control room, analogue equipment and in-house engineer support.",
        "eyebrow": "Recording",
        "headline": "World Class Recording.<br><em>Built For Sound.</em>",
        "subtitle": "Record your music in a purpose-built studio designed for clarity, character and performance.",
        "hero": "/photos/optimized/salvation-service-recording-hero.webp",
        "hero_alt": "Recording at Salvation Studios",
        "cta": "ENQUIRE ABOUT A RECORDING SESSION",
        "intro": "Record your music in a purpose-built studio designed for clarity, character and performance. From full band tracking to vocal sessions, Salvation offers an exceptional acoustic environment, world-class analogue equipment and experienced in-house engineers to support your session from start to finish.",
        "bullets": ["Access to the Main Studio live room and control room", "Vintage Neve console and world-class analogue outboard", "Extensive microphone and instrument collection", "Experienced in-house engineer or assistant included", "Flexible setup for bands, ensembles and overdubs"],
        "secondary": "For projects that require a more focused production or overdub environment, sessions can also take place in The Bunker, our dedicated production and mixing studio, built around vintage analogue gear and a modern hybrid workflow.",
        "why": "The studio was designed from the ground up for sound, combining the scale of a traditional recording space with the precision of modern acoustic design. Whether you're capturing a live performance or building a record layer by layer, the environment is built to help you get the best possible result.",
        "images": ["/photos/optimized/salvation-service-recording-what.webp", "/photos/optimized/salvation-service-recording-why.webp"],
    },
    "mixing": {
        "title": "Mixing Studio Brighton | Salvation Studios",
        "description": "Professional mixing at Salvation Studios Brighton using experienced in-house engineers, accurate monitoring and a hybrid analogue/digital workflow.",
        "eyebrow": "Mixing",
        "headline": "Mixes That Serve the Song.",
        "subtitle": "Professional mixing that brings your music into focus.",
        "hero": "/photos/optimized/salvation-service-mixing-hero.webp",
        "hero_alt": "Mixing room at Salvation Studios",
        "cta": "Enquire about a mix",
        "intro": "Professional mixing that brings your music into focus. Our in-house engineers work in a precision-tuned environment using a hybrid analogue and digital workflow to deliver mixes that sound balanced, detailed and ready for release.",
        "bullets": ["Mixing by experienced in-house engineers", "Hybrid analogue/digital workflow", "Access to high-end outboard and monitoring", "Revisions to refine your final mix"],
        "secondary": "We often offer preferential mixing rates when booked alongside recording sessions, allowing projects to move seamlessly from tracking through to final mixes. Every project is different, and we’re always happy to tailor the process to suit your needs.",
        "why": "Mixing is about more than balance, it’s about emotion, energy and translation. Working in an accurate listening environment with the right tools ensures your music sounds as intended across every system.",
        "images": ["/photos/optimized/salvation-service-mixing-what.webp", "/photos/optimized/salvation-service-mixing-room.webp", "/photos/optimized/salvation-service-mixing-why.webp"],
    },
    "mastering": {
        "title": "Mastering Brighton | Salvation Studios",
        "description": "Professional mastering support for Salvation Studios projects with trusted engineers, dedicated mastering environments and final release quality control.",
        "eyebrow": "Mastering",
        "headline": "Finishing Your Record, Properly.",
        "subtitle": "Give your music the final polish before release.",
        "hero": "/photos/optimized/salvation-service-mastering-hero.webp",
        "hero_alt": "Mastering service at Salvation Studios",
        "cta": "Enquire about mastering",
        "intro": "Give your music the final polish with professional mastering carried out in a dedicated mastering environment. We work with trusted mastering engineers using specialist equipment to ensure your track translates with clarity, consistency and impact.",
        "bullets": ["Professional mastering by experienced engineers", "Dedicated mastering suite and monitoring environment", "Optimisation for streaming and distribution", "Final quality control before release"],
        "secondary": "We often offer preferential mastering rates when booked alongside mixing or recording sessions, allowing your project to move smoothly through to its final stage. Every project is different, and we’re always happy to tailor the process to suit your needs.",
        "why": "Mastering is a critical step in the process. By working with dedicated mastering engineers and purpose-built rooms, your music receives the attention and precision it deserves before release.",
        "images": ["/photos/optimized/salvation-service-mastering-what.webp", "/photos/optimized/salvation-service-mastering-room.webp", "/photos/optimized/salvation-service-mastering-why.webp"],
    },
    "live-videos": {
        "title": "Live Video Sessions Brighton | Salvation Studios",
        "description": "Live performance video sessions at Salvation Studios Brighton combining studio audio capture, professional videography and tailored lighting.",
        "eyebrow": "Live Videos",
        "headline": "Bring Your Live Performance to Life.",
        "subtitle": "High-quality live performance videos recorded in a world-class studio environment.",
        "hero": "/photos/optimized/salvation-service-live-hero.webp",
        "hero_alt": "Live video sessions at Salvation Studios",
        "cta": "Enquire about Live Video sessions",
        "intro": "Stand out with high-quality live performance videos recorded in a world-class studio environment. Combining exceptional audio capture with professional videography, live sessions at Salvation are designed to showcase your music at its best.",
        "bullets": ["Multi-camera video production", "High-quality studio audio recording", "Access to the Main Studio live room", "Lighting and atmosphere tailored to your performance"],
        "secondary": "We work with a roster of experienced videographers and can tailor each session to suit a range of creative approaches and budgets. Dry hire is also available if you’d prefer to bring in your own team.",
        "why": "In a crowded digital space, quality matters. A great live video not only sounds incredible but visually reflects the level of your artistry, giving you content that cuts through and represents your music properly.",
        "images": ["/photos/optimized/salvation-service-live-what.webp", "/photos/optimized/salvation-service-live-why.webp"],
    },
}


def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def page_nav() -> str:
    return f'''<nav class="nav" id="nav">
  <div class="nav-logo"><a href="/"><img src="/logo.png" alt="Salvation Music Studios" width="600" height="300" decoding="async" loading="eager"></a></div>
  <ul class="nav-links">
    <li><a href="/">Home</a></li>
    <li class="nav-dropdown">
      <a href="/spaces/" class="nav-dropdown-toggle" aria-haspopup="true">Spaces</a>
      <div class="nav-dropdown-menu" aria-label="Studio spaces">
        <a href="/spaces/">Spaces Overview</a>
        <a href="/rooms/main-studio/">Main Studio</a>
        <a href="/rooms/control-room/">Control Room</a>
        <a href="/rooms/live-room/">Live Room</a>
        <a href="/rooms/the-bunker/">The Bunker</a>
        <a href="/rooms/the-bunker/#mezzanine-room">Mezzanine Room</a>
        <a href="/rooms/the-bunker/#subterranean-room">Subterranean Room</a>
      </div>
    </li>
    <li><a href="/equipment/">Equipment</a></li>
    <li><a href="/gallery/">Gallery</a></li>
    {SERVICE_DROPDOWN}
    <li><a href="/testimonials/">Testimonials</a></li>
  </ul>
  <a href="/contact/#enquiry-form" class="nav-cta">Enquire about your next session</a>
  <button class="nav-hamburger" id="hamburger" aria-label="Menu" aria-controls="mobileMenu" aria-expanded="false"><span></span><span></span><span></span></button>
</nav>
<div class="mobile-menu" id="mobileMenu" role="dialog" aria-modal="true" aria-label="Site navigation">
  <a href="/">Home</a>
  <a href="/spaces/">Spaces Overview</a>
  <a href="/rooms/main-studio/">Main Studio</a>
  <a href="/rooms/control-room/">Control Room</a>
  <a href="/rooms/the-bunker/">The Bunker</a>
  <a href="/equipment/">Equipment</a>
  <a href="/gallery/">Gallery</a>
{MOBILE_SERVICE_LINKS}
  <a href="/contact/#enquiry-form" class="mobile-cta">Enquire about your next session</a>
</div>'''


def footer() -> str:
    return f'''<footer>
  <div class="footer-top">
    <div>
      <div class="footer-logo"><a href="/"><img src="/logo.png" alt="Salvation Studios" width="140" height="70" decoding="async" loading="lazy"></a></div>
      <p class="footer-tagline">World-class recording, mixing and writing rooms in Brighton.<br>Built inside a restored 1910 hall moments from the seafront.</p>
    </div>
    {STUDIO_FOOTER}
    {SERVICES_FOOTER}
    {FIND_FOOTER}
  </div>
  <div class="footer-bottom"><span>© 2026 Salvation Studios. All Rights Reserved.</span><span>Designed in Brighton. Built for sound.</span></div>
</footer>'''

SCRIPT = '''<script>
document.documentElement.classList.add('js');
(function(){const nav=document.getElementById('nav');if(nav) window.addEventListener('scroll',()=>nav.classList.toggle('scrolled',window.scrollY>60),{passive:true});document.querySelectorAll('.reveal').forEach(el=>el.classList.add('visible'));const hamburger=document.getElementById('hamburger');const mobileMenu=document.getElementById('mobileMenu');let lastFocus=null;function setMenu(open){if(!hamburger||!mobileMenu)return;if(open)lastFocus=document.activeElement;mobileMenu.classList.toggle('open',open);hamburger.classList.toggle('open',open);hamburger.setAttribute('aria-expanded',open?'true':'false');document.body.style.overflow=open?'hidden':'';if(open){const first=mobileMenu.querySelector('a');if(first)first.focus({preventScroll:true});}else if(lastFocus&&typeof lastFocus.focus==='function')lastFocus.focus({preventScroll:true});}if(hamburger&&mobileMenu){hamburger.addEventListener('click',()=>setMenu(!mobileMenu.classList.contains('open')));mobileMenu.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>setMenu(false)));document.addEventListener('keydown',e=>{if(e.key==='Escape')setMenu(false);});}})();
</script><script src="/search.js" defer></script>'''


def service_page(slug: str, data: dict) -> str:
    bullets = "".join(f"<li>{html_escape(b)}</li>" for b in data["bullets"])
    cards = "".join(f'''<div class="feature-card"><div class="card-photo"><img src="{img}" alt="{html_escape(data['eyebrow'])} at Salvation Studios" width="1024" height="683" decoding="async" loading="lazy"></div><div class="card-body"><h3 class="card-title">Studio detail</h3><p class="card-desc">A supporting view of the Salvation environment used for this service pathway.</p></div></div>''' for img in data["images"])
    canonical = f"https://www.salvationstudios.co.uk/services/{slug}/"
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{data['title']}</title><link rel="stylesheet" href="/shared.css">
<meta name="description" content="{html_escape(data['description'])}"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:title" content="{html_escape(data['title'])}"><meta property="og:description" content="{html_escape(data['description'])}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="https://www.salvationstudios.co.uk{data['hero']}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{html_escape(data['title'])}"><meta name="twitter:description" content="{html_escape(data['description'])}"><meta name="twitter:image" content="https://www.salvationstudios.co.uk{data['hero']}">
<script type="application/ld+json">{{"@context":"https://schema.org","@graph":[{{"@type":["LocalBusiness","EntertainmentBusiness"],"@id":"https://www.salvationstudios.co.uk/#studio","name":"Salvation Studios","url":"https://www.salvationstudios.co.uk/","telephone":"+44 333 444 5508","address":{{"@type":"PostalAddress","streetAddress":"79 North Street","addressLocality":"Brighton and Hove","addressRegion":"Brighton","postalCode":"BN41 1DH","addressCountry":"GB"}},"email":"info@salvationstudios.co.uk"}},{{"@type":"WebPage","@id":"{canonical}#webpage","url":"{canonical}","name":"{html_escape(data['title'])}"}},{{"@type":"Service","@id":"{canonical}#service","name":"{html_escape(data['eyebrow'])}","provider":{{"@id":"https://www.salvationstudios.co.uk/#studio"}}}}]}}</script>
</head><body>{page_nav()}
<section class="page-hero"><div class="page-hero-img"><img src="{data['hero']}" alt="{html_escape(data['hero_alt'])}" width="1600" height="1067" decoding="async" fetchpriority="high"></div><div class="page-hero-overlay"></div><div class="page-hero-content"><span class="page-eyebrow">{html_escape(data['eyebrow'])}</span><h1 class="page-title">{data['headline']}</h1><p class="page-subtitle">{html_escape(data['subtitle'])}</p><div class="btn-row" style="margin-top:28px"><a href="/contact/#enquiry-form" class="btn-primary">{html_escape(data['cta'])}</a></div></div></section>
<section class="content-section bg-void reveal"><div class="two-col top"><div><span class="label">The service</span><h2 class="h2-serif">Built around the <em>music</em></h2><p class="body-text">{html_escape(data['intro'])}</p><h3 class="h3-serif" style="margin-top:34px">What You Get</h3><ul class="detail-list">{bullets}</ul></div><div class="photo-frame tall"><img src="{data['hero']}" alt="{html_escape(data['hero_alt'])}" width="1600" height="1067" decoding="async" loading="lazy"></div></div></section>
<section class="content-section bg-deep reveal"><div class="two-col top"><div><span class="label">Workflow</span><h2 class="h2-serif">A practical route through the studio.</h2><p class="body-text">{html_escape(data['secondary'])}</p></div><div><span class="label">Why Salvation?</span><h2 class="h2-serif">Rooms designed for <em>translation</em></h2><p class="body-text">{html_escape(data['why'])}</p></div></div><div class="card-grid" style="margin-top:54px">{cards}</div></section>
<div class="cta-band reveal"><h2 class="h2-serif">Not sure what you need?</h2><p class="body-text">Our team are always happy to talk through your project and help you plan the right session.</p><div class="btn-row"><a href="/contact/#enquiry-form" class="btn-primary">Enquire now</a></div></div>
{footer()}{SCRIPT}</body></html>'''


def signature_page() -> str:
    canonical = "https://www.salvationstudios.co.uk/services/signature-sessions/"
    bullets = ["Studio time at Salvation Studios", "Collaboration with an established producer or engineer", "Access to the extensive Salvation Backline and equipment", "Engineering support throughout the session", "A focused, high-level creative experience", "Your tracks professionally mixed and mastered", "Accommodation (if needed)"]
    lis = "".join(f"<li>{html_escape(b)}</li>" for b in bullets)
    desc = "Signature Sessions connect artists with respected producers and engineers in a world-class Brighton studio environment."
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Signature Sessions Brighton | Salvation Studios</title><link rel="stylesheet" href="/shared.css"><meta name="description" content="{desc}"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:title" content="Signature Sessions Brighton | Salvation Studios"><meta property="og:description" content="{desc}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="https://www.salvationstudios.co.uk/photos/client-notes-2026-06-05/signature-sessions.jpg"><meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">{{"@context":"https://schema.org","@graph":[{{"@type":["LocalBusiness","EntertainmentBusiness"],"@id":"https://www.salvationstudios.co.uk/#studio","name":"Salvation Studios","url":"https://www.salvationstudios.co.uk/","telephone":"+44 333 444 5508","address":{{"@type":"PostalAddress","streetAddress":"79 North Street","addressLocality":"Brighton and Hove","addressRegion":"Brighton","postalCode":"BN41 1DH","addressCountry":"GB"}},"email":"info@salvationstudios.co.uk"}},{{"@type":"WebPage","@id":"{canonical}#webpage","url":"{canonical}","name":"Signature Sessions Brighton | Salvation Studios"}}]}}</script></head><body>{page_nav()}<section class="page-hero"><div class="page-hero-img"><img src="/photos/client-notes-2026-06-05/signature-sessions.jpg" alt="Signature Sessions at Salvation Studios" width="1024" height="683" decoding="async" fetchpriority="high"></div><div class="page-hero-overlay"></div><div class="page-hero-content"><span class="page-eyebrow">Signature Sessions</span><h1 class="page-title">Create With<br><em>The Best</em></h1><p class="page-subtitle">Signature Sessions are a unique offering at Salvation, designed to connect artists with some of the most respected producers and engineers in the industry.</p><div class="btn-row" style="margin-top:28px"><a href="/contact/#enquiry-form" class="btn-primary">Enquire about your Signature Session</a></div></div></section><section class="content-section bg-void reveal"><div class="two-col top"><div><span class="label">Create With The Best</span><h2 class="h2-serif">A focused, high-level <em>creative experience</em>.</h2><p class="body-text">Signature Sessions are a unique offering at Salvation, designed to connect artists with some of the most respected producers and engineers in the industry. Built around collaboration, these sessions give artists the opportunity to step into a high-level creative environment and make music alongside experienced professionals, using world-class facilities and equipment.</p><p class="body-text">Each Signature Session is centred around a carefully curated collaboration between artist and producer. Whether you're developing ideas, recording a release-ready track or exploring a new direction, the focus is on creating something meaningful in a supportive and inspiring environment.</p></div><div class="photo-frame tall"><img src="/photos/client-notes-2026-06-05/signature-sessions.jpg" alt="Signature Sessions at Salvation Studios" width="1024" height="683" decoding="async" loading="lazy"></div></div></section><section class="content-section bg-deep reveal"><span class="label">What You Get</span><h2 class="h2-serif">Built around <em>collaboration</em>.</h2><ul class="detail-list">{lis}</ul><div style="margin-top:54px;max-width:760px"><h3 class="h3-serif">Previous Signature Sessions</h3><p class="body-text">We’ve been privileged to host sessions with some of the industry’s most respected producers and engineers.</p></div></section><div class="cta-band reveal"><h2 class="h2-serif">Talk through your Signature Session.</h2><p class="body-text">Send the team a project brief and they can confirm the right creative route.</p><div class="btn-row"><a href="/contact/#enquiry-form" class="btn-primary">Enquire about your Signature Session</a></div></div>{footer()}{SCRIPT}</body></html>'''


def giveaways_page() -> str:
    canonical = "https://www.salvationstudios.co.uk/services/giveaways-offers/"
    desc = "Current Salvation Studios giveaways, artist opportunities and limited studio offers."
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Giveaways &amp; Offers | Salvation Studios</title><link rel="stylesheet" href="/shared.css"><meta name="description" content="{desc}"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:title" content="Giveaways &amp; Offers | Salvation Studios"><meta property="og:description" content="{desc}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="https://www.salvationstudios.co.uk/photos/optimized/studio-sfpb.webp"><meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">{{"@context":"https://schema.org","@graph":[{{"@type":["LocalBusiness","EntertainmentBusiness"],"@id":"https://www.salvationstudios.co.uk/#studio","name":"Salvation Studios","url":"https://www.salvationstudios.co.uk/","telephone":"+44 333 444 5508","address":{{"@type":"PostalAddress","streetAddress":"79 North Street","addressLocality":"Brighton and Hove","addressRegion":"Brighton","postalCode":"BN41 1DH","addressCountry":"GB"}},"email":"info@salvationstudios.co.uk"}},{{"@type":"WebPage","@id":"{canonical}#webpage","url":"{canonical}","name":"Giveaways & Offers | Salvation Studios"}}]}}</script></head><body>{page_nav()}<section class="page-hero"><div class="page-hero-img"><img src="/photos/optimized/studio-sfpb.webp" alt="Salvation Studios live room" width="2200" height="1467" decoding="async" fetchpriority="high"></div><div class="page-hero-overlay"></div><div class="page-hero-content"><span class="page-eyebrow">Giveaways &amp; Offers</span><h1 class="page-title">Opportunities for<br><em>Artists.</em></h1><p class="page-subtitle">Studio time giveaways, collaborative sessions and limited offers from Salvation Studios.</p></div></section><section class="content-section bg-void reveal"><div class="two-col top"><div><span class="label">Current opportunities</span><h2 class="h2-serif">Opportunities for <em>artists</em>.</h2><p class="body-text">This page is where you’ll find everything currently happening at Salvation, from studio time giveaways to collaborative sessions and limited offers. Each initiative is designed to create opportunities, support new music and give more artists access to a world-class recording environment. Check below to see what have on currently.</p><p class="body-text">We don’t have any active offers right now, but new opportunities are announced regularly. Follow us on Instagram or check back soon to stay up to date.</p><div class="btn-row" style="margin-top:32px"><a href="https://www.instagram.com/salvationmusicstudiosbtn/" class="btn-primary">Follow on instagram</a><a href="/contact/#enquiry-form" class="btn-outline">Get In Touch</a></div></div><div class="photo-frame tall"><img src="/photos/optimized/studio-sfpb.webp" alt="Salvation Studios live room" width="2200" height="1467" decoding="async" loading="lazy"></div></div></section>{footer()}{SCRIPT}</body></html>'''


def accom_page(slug="accommodation-hospitality") -> str:
    canonical = f"https://www.salvationstudios.co.uk/services/{slug}/"
    title = "Accommodation and Hospitality | Salvation Studios"
    desc = "Accommodation and hospitality guidance for longer Salvation Studios sessions in Brighton, including practical stay planning for artists, producers and teams."
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><link rel="stylesheet" href="/shared.css"><meta name="description" content="{desc}"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="https://www.salvationstudios.co.uk/photos/optimized/studio-u590.webp"><meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">{{"@context":"https://schema.org","@graph":[{{"@type":["LocalBusiness","EntertainmentBusiness"],"@id":"https://www.salvationstudios.co.uk/#studio","name":"Salvation Studios","url":"https://www.salvationstudios.co.uk/","telephone":"+44 333 444 5508","address":{{"@type":"PostalAddress","streetAddress":"79 North Street","addressLocality":"Brighton and Hove","addressRegion":"Brighton","postalCode":"BN41 1DH","addressCountry":"GB"}},"email":"info@salvationstudios.co.uk"}},{{"@type":"WebPage","@id":"{canonical}#webpage","url":"{canonical}","name":"{title}"}}]}}</script></head><body>{page_nav()}<section class="page-hero"><div class="page-hero-img"><img src="/photos/optimized/studio-u590.webp" alt="Longer-session support space at Salvation Studios" width="2200" height="1467" decoding="async" fetchpriority="high"></div><div class="page-hero-overlay"></div><div class="page-hero-content"><span class="page-eyebrow">Accommodation and Hospitality</span><h1 class="page-title">Stay close to<br><em>the session.</em></h1><p class="page-subtitle">Practical stay and hospitality guidance for artists, producers and teams booking longer sessions at Salvation Studios.</p><div class="btn-row" style="margin-top:28px"><a href="/contact/#enquiry-form" class="btn-primary">Enquire about accommodation and hospitality</a></div></div></section><section class="content-section bg-void reveal"><div class="two-col top"><div><span class="label">Longer sessions</span><h2 class="h2-serif">Plan the practical side <em>properly</em>.</h2><p class="body-text">For longer recording blocks, writing camps and multi-day projects, the studio can help you think through the practical details around staying in Brighton, team size, room needs, session flow and day-to-day comfort.</p><p class="body-text">Salvation is minutes from Brighton and Hove transport links, hotels, the seafront and local amenities, making it a practical base for visiting artists, producers and writing teams.</p></div><div class="photo-frame tall"><img src="/photos/optimized/studio-u591.webp" alt="The Bunker writing and production wing" width="1600" height="1067" decoding="async" loading="lazy"></div></div></section><section class="content-section bg-deep reveal"><span class="label">What to include</span><h2 class="h2-serif">Tell the team what your project needs.</h2><div class="card-grid three-col"><div class="feature-card"><div class="card-body"><h3 class="card-title">Dates and duration</h3><p class="card-desc">Share preferred dates, expected length of stay and whether the booking is fixed or flexible.</p></div></div><div class="feature-card"><div class="card-body"><h3 class="card-title">Team size</h3><p class="card-desc">Let the studio know who is travelling, who needs to be on-site and any production support required.</p></div></div><div class="feature-card"><div class="card-body"><h3 class="card-title">Session flow</h3><p class="card-desc">Outline whether the project is recording, writing, mixing, live video or a combination of services.</p></div></div></div></section><div class="cta-band reveal"><h2 class="h2-serif">Enquire about accommodation and hospitality.</h2><p class="body-text">Send a brief with dates, session type, team size and practical requirements.</p><div class="btn-row"><a href="/contact/#enquiry-form" class="btn-primary">Enquire now</a></div></div>{footer()}{SCRIPT}</body></html>'''


def services_accordion() -> str:
    panels = []
    for slug in ["recording", "mixing", "mastering", "live-videos"]:
        d = SERVICE_DATA[slug]
        open_attr = " open" if slug == "recording" else ""
        summary = "Live Videos" if slug == "live-videos" else d["eyebrow"]
        bullets = "".join(f"<li>{html_escape(b)}</li>" for b in d["bullets"])
        imgs = "".join(f'<div class="service-photo"><img src="{img}" alt="{html_escape(summary)} at Salvation Studios" width="1024" height="683" decoding="async" loading="lazy"></div>' for img in [d["hero"], *d["images"]])
        panels.append(f'''  <details class="service-panel" id="service-{slug}"{open_attr}>
    <summary>{summary}</summary>
    <div class="service-content service-grid">
      <div class="service-copy"><h2>{d['headline']}</h2><p>{html_escape(d['intro'])}</p><div class="service-actions"><a href="/contact/#enquiry-form" class="btn-primary">{html_escape(d['cta'])}</a></div><h3>What You Get</h3><ul class="service-list">{bullets}</ul><p>{html_escape(d['secondary'])}</p><h3>Why Salvation?</h3><p>{html_escape(d['why'])}</p><h3>Not sure what you need?</h3><p>Our team are always happy to talk through your project and help you plan the right session.</p><div class="service-actions"><a href="/contact/#enquiry-form" class="btn-primary">Enquire now</a><a href="/services/{slug}/" class="btn-outline">Open service page</a></div></div>
      <div>{imgs}</div>
    </div>
  </details>''')
    panels.append('''  <details class="service-panel" id="service-signature-sessions">
    <summary>Signature Sessions</summary>
    <div class="service-content service-grid">
      <div class="service-copy"><h2>Create With The Best</h2><p>Signature Sessions are a unique offering at Salvation, designed to connect artists with some of the most respected producers and engineers in the industry. Built around collaboration, these sessions give artists the opportunity to step into a high-level creative environment and make music alongside experienced professionals, using world-class facilities and equipment.</p><div class="service-actions"><a href="/contact/#enquiry-form" class="btn-primary">Enquire about your Signature Session</a></div><p>Each Signature Session is centred around a carefully curated collaboration between artist and producer. Whether you're developing ideas, recording a release-ready track or exploring a new direction, the focus is on creating something meaningful in a supportive and inspiring environment.</p><h3>What You Get</h3><ul class="service-list"><li>Studio time at Salvation Studios</li><li>Collaboration with an established producer or engineer</li><li>Access to the extensive Salvation Backline and equipment</li><li>Engineering support throughout the session</li><li>A focused, high-level creative experience</li><li>Your tracks professionally mixed and mastered</li><li>Accommodation (if needed)</li></ul><h3>Previous Signature Sessions</h3><p>We’ve been privileged to host sessions with some of the industry’s most respected producers and engineers.</p><div class="service-actions"><a href="/services/signature-sessions/" class="btn-outline">Open service page</a></div></div>
      <div><div class="service-photo"><img src="/photos/client-notes-2026-06-05/signature-sessions.jpg" alt="Signature Sessions at Salvation Studios" width="1024" height="683" decoding="async" loading="lazy"></div></div>
    </div>
  </details>''')
    panels.append('''  <details class="service-panel" id="service-giveaways-offers">
    <summary>Giveaways &amp; Offers</summary>
    <div class="service-content service-grid">
      <div class="service-copy"><h2>Opportunities for Artists.</h2><p>This page is where you’ll find everything currently happening at Salvation, from studio time giveaways to collaborative sessions and limited offers. Each initiative is designed to create opportunities, support new music and give more artists access to a world-class recording environment. Check below to see what have on currently.</p><p>We don’t have any active offers right now, but new opportunities are announced regularly. Follow us on Instagram or check back soon to stay up to date.</p><div class="service-actions"><a href="https://www.instagram.com/salvationmusicstudiosbtn/" class="btn-primary">Follow on instagram</a><a href="/contact/#enquiry-form" class="btn-outline">Get In Touch</a><a href="/services/giveaways-offers/" class="btn-outline">Open service page</a></div></div>
      <div><div class="service-photo"><img src="/photos/optimized/studio-sfpb.webp" alt="Salvation Studios artist opportunities" width="2200" height="1467" decoding="async" loading="lazy"></div></div>
    </div>
  </details>''')
    panels.append('''  <details class="service-panel" id="service-accommodation-hospitality">
    <summary>Accommodation and Hospitality</summary>
    <div class="service-content service-grid">
      <div class="service-copy"><h2>Stay close to<br><em>the session.</em></h2><p>For longer recording blocks, writing camps and multi-day projects, the studio can help you think through the practical details around staying in Brighton, team size, room needs, session flow and day-to-day comfort.</p><p>Salvation is minutes from Brighton and Hove transport links, hotels, the seafront and local amenities, making it a practical base for visiting artists, producers and writing teams.</p><div class="service-actions"><a href="/contact/#enquiry-form" class="btn-primary">Enquire about accommodation and hospitality</a><a href="/services/accommodation-hospitality/" class="btn-outline">Open service page</a></div></div>
      <div><div class="service-photo"><img src="/photos/optimized/studio-u590.webp" alt="Longer-session support space at Salvation Studios" width="2200" height="1467" decoding="async" loading="lazy"></div></div>
    </div>
  </details>''')
    return "<section class=\"services-accordion\" aria-label=\"Salvation Studios services accordion\">\n" + "\n".join(panels) + "\n</section>"


def patch_nav_footer_and_ctas(path: Path) -> None:
    text = path.read_text(errors="ignore")
    original = text
    # Skip concept pages for structural nav; they are noindex demos, but still remove catering wording later.
    if not path.name.startswith("concept-"):
        if 'aria-label="Studio services"' not in text:
            text = text.replace('    <li><a href="/services/">Services</a></li>', '    ' + SERVICE_DROPDOWN)
        # Mobile menu: insert services if not present.
        if 'href="/services/signature-sessions/"' not in text.split('</div>', 1)[0] and '<div class="mobile-menu"' in text:
            text = text.replace('  <a href="/gallery/">Gallery</a>\n', '  <a href="/gallery/">Gallery</a>\n' + MOBILE_SERVICE_LINKS + '\n')
        # Footer services blocks.
        text = re.sub(r'<div>\s*<div class="footer-head">Services</div>\s*<ul class="footer-links">.*?</ul>\s*</div>', SERVICES_FOOTER, text, flags=re.S)
        # Contact-ish CTAs to form anchors.
        text = text.replace('href="/contact/" class="nav-cta"', 'href="/contact/#enquiry-form" class="nav-cta"')
        text = text.replace('href="/contact/" class="mobile-cta"', 'href="/contact/#enquiry-form" class="mobile-cta"')
        text = text.replace('href="/contact/" class="btn-primary"', 'href="/contact/#enquiry-form" class="btn-primary"')
        text = text.replace('href="/contact/" class="btn-outline"', 'href="/contact/#enquiry-form" class="btn-outline"')
        text = text.replace('href="/contact/">Get in Touch', 'href="/contact/#enquiry-form">Get in Touch')
        text = text.replace('href="/contact/">Enquire about your next session', 'href="/contact/#enquiry-form">Enquire about your next session')
        text = text.replace('href="/contact/">Enquire', 'href="/contact/#enquiry-form">Enquire')
        text = text.replace('href="/contact/">Start an Enquiry', 'href="/contact/#enquiry-form">Start an Enquiry')
        if path.name == "index.html":
            # Homepage CTAs should scroll to the local form.
            text = text.replace('href="/contact/#enquiry-form" class="nav-cta"', 'href="#home-enquiry" class="nav-cta"')
            text = text.replace('href="/contact/#enquiry-form" class="mobile-cta"', 'href="#home-enquiry" class="mobile-cta"')
            text = text.replace('href="/contact/#enquiry-form" class="btn-primary hero-book-btn"', 'href="#home-enquiry" class="btn-primary hero-book-btn"')
            text = text.replace('href="/contact/#enquiry-form" class="section-link"', 'href="#home-enquiry" class="section-link"')
        # Generic visible old service labels/links.
        text = text.replace('/services/catering/', '/services/accommodation-hospitality/')
        text = text.replace('/services/accommodation/">Accommodation</a>', '/services/accommodation-hospitality/">Accommodation and Hospitality</a>')
    # Remove user-facing Catering terms where possible without touching concepts structurally.
    text = text.replace('Catering &amp; Hospitality', 'Accommodation and Hospitality')
    text = text.replace('Catering and Hospitality', 'Accommodation and Hospitality')
    text = text.replace('catering and hospitality', 'hospitality')
    text = text.replace('catering, accommodation or filming needs', 'accommodation, hospitality or filming needs')
    text = text.replace('Pair accommodation planning with catering and hospitality requirements for smooth full-day sessions.', 'Pair accommodation planning with practical hospitality requirements for smooth full-day sessions.')
    text = text.replace('Catering', 'Hospitality')
    text = text.replace('catering', 'hospitality')
    if text != original:
        path.write_text(text)


def update_services_page() -> None:
    path = ROOT / "services.html"
    text = path.read_text()
    text = re.sub(r'<section class="services-accordion" aria-label="Salvation Studios services accordion">.*?</section>', services_accordion(), text, flags=re.S)
    text = text.replace('Explore Salvation Studios services: recording, mixing, mastering, live videos, Signature Sessions, giveaways and offers in a world-class Brighton studio.', 'Explore Salvation Studios services: recording, mixing, mastering, live videos, Signature Sessions, giveaways, offers, accommodation and hospitality in a world-class Brighton studio.')
    path.write_text(text)


def update_homepage_services() -> None:
    path = ROOT / "index.html"
    text = path.read_text()
    pills = '''  <div class="svc-pills reveal">
    <a href="/services/recording/" class="svc-pill">Recording</a>
    <a href="/services/mixing/" class="svc-pill">Mixing</a>
    <a href="/services/mastering/" class="svc-pill">Mastering</a>
    <a href="/services/live-videos/" class="svc-pill">Live Videos</a>
    <a href="/services/signature-sessions/" class="svc-pill">Signature Sessions</a>
    <a href="/services/giveaways-offers/" class="svc-pill">Giveaways &amp; Offers</a>
    <a href="/services/accommodation-hospitality/" class="svc-pill">Accommodation and Hospitality</a>
  </div>'''
    text = re.sub(r'  <div class="svc-pills reveal">.*?</div>\n  <div class="services-grid featured-services reveal"', pills + '\n  <div class="services-grid featured-services reveal"', text, flags=re.S)
    cards = '''  <div class="services-grid featured-services reveal" aria-label="Featured Salvation services">
    <a href="/services/recording/" class="svc-card" style="text-decoration:none;color:inherit;"><div class="svc-photo"><img src="/photos/optimized/studio-client-service-recording.webp" alt="Recording at Salvation Studios" width="1024" height="683" decoding="async" loading="lazy"></div><div class="svc-body"><div class="svc-name">Recording</div><p class="svc-desc">Record your music in a purpose-built studio designed for clarity, character and performance, from full band tracking to focused vocal sessions.</p></div></a>
    <a href="/services/mixing/" class="svc-card" style="text-decoration:none;color:inherit;"><div class="svc-photo"><img src="/photos/optimized/studio-client-service-mixing.webp" alt="Mixing at Salvation Studios" width="1024" height="683" decoding="async" loading="lazy"></div><div class="svc-body"><div class="svc-name">Mixing</div><p class="svc-desc">Professional mixing in a precision-tuned environment, using a hybrid analogue and digital workflow to bring your music into focus.</p></div></a>
    <a href="/services/mastering/" class="svc-card" style="text-decoration:none;color:inherit;"><div class="svc-photo"><img src="/photos/client-notes-2026-06-05/mastering.jpg" alt="Mastering service at Salvation Studios" width="1024" height="576" decoding="async" loading="lazy"></div><div class="svc-body"><div class="svc-name">Mastering</div><p class="svc-desc">Give your music the final polish with professional mastering support, dedicated monitoring and final quality control before release.</p></div></a>
    <a href="/services/live-videos/" class="svc-card" style="text-decoration:none;color:inherit;"><div class="svc-photo"><img src="/photos/client-notes-2026-06-05/live-videos.jpg" alt="Live video sessions at Salvation Studios" width="1024" height="819" decoding="async" loading="lazy"></div><div class="svc-body"><div class="svc-name">Live Videos</div><p class="svc-desc">High-quality live performance videos combining exceptional studio audio capture with professional videography and tailored atmosphere.</p></div></a>
    <a href="/services/signature-sessions/" class="svc-card" style="text-decoration:none;color:inherit;"><div class="svc-photo"><img src="/photos/client-notes-2026-06-05/signature-sessions.jpg" alt="Signature Sessions at Salvation Studios" width="1024" height="683" decoding="async" loading="lazy"></div><div class="svc-body"><div class="svc-name">Signature Sessions</div><p class="svc-desc">A unique opportunity to create alongside respected producers and engineers in a focused, high-level creative environment.</p></div></a>
    <a href="/services/giveaways-offers/" class="svc-card" style="text-decoration:none;color:inherit;"><div class="svc-photo"><img src="/photos/optimized/studio-sfpb.webp" alt="Salvation Studios artist opportunities" width="2200" height="1467" decoding="async" loading="lazy"></div><div class="svc-body"><div class="svc-name">Giveaways &amp; Offers</div><p class="svc-desc">Current artist opportunities, studio time giveaways, collaborative sessions and limited offers from Salvation Studios.</p></div></a>
    <a href="/services/accommodation-hospitality/" class="svc-card" style="text-decoration:none;color:inherit;"><div class="svc-photo"><img src="/photos/optimized/studio-u590.webp" alt="Longer-session support space at Salvation Studios" width="2200" height="1467" decoding="async" loading="lazy"></div><div class="svc-body"><div class="svc-name">Accommodation and Hospitality</div><p class="svc-desc">Practical stay and hospitality guidance for artists, producers and teams booking longer recording or writing sessions in Brighton.</p></div></a>
  </div>'''
    text = re.sub(r'  <div class="services-grid featured-services reveal" aria-label="Featured Salvation services">.*?</div>\n</section>', cards + '\n</section>', text, flags=re.S)
    path.write_text(text)


def update_shared_css() -> None:
    for rel in ["shared.css", "index.html"]:
        path = ROOT / rel
        text = path.read_text()
        if 'aria-label="Studio services"' not in text and '.nav-dropdown-menu[aria-label="Studio services"]' not in text:
            marker = '.nav-dropdown-menu a:hover, .nav-dropdown-menu a:focus { color: var(--white); background: rgba(124,58,237,.16); }'
            if marker in text:
                text = text.replace(marker, marker + '\n.nav-dropdown-menu[aria-label="Studio services"] { width: 292px; }\n.nav-dropdown-menu[aria-label="Studio services"] a { padding: 8px 11px; font-size: 11px; }')
        elif '.nav-dropdown-menu[aria-label="Studio services"]' not in text:
            marker = '.nav-dropdown-menu a:hover, .nav-dropdown-menu a:focus { color: var(--white); background: rgba(124,58,237,.16); }'
            text = text.replace(marker, marker + '\n.nav-dropdown-menu[aria-label="Studio services"] { width: 292px; }\n.nav-dropdown-menu[aria-label="Studio services"] a { padding: 8px 11px; font-size: 11px; }')
        path.write_text(text)


def update_config_and_sitemap() -> None:
    config_path = ROOT / "vercel.json"
    config = json.loads(config_path.read_text())
    redirects = config.get("redirects", [])
    # Remove old catering redirect and add new route aliases.
    redirects = [r for r in redirects if r.get("source") not in {"/catering", "/services/catering", "/accommodation"}]
    additions = [
        {"source": "/accommodation", "destination": "/services/accommodation-hospitality", "permanent": True},
        {"source": "/services/accommodation", "destination": "/services/accommodation-hospitality", "permanent": True},
        {"source": "/catering", "destination": "/services/accommodation-hospitality", "permanent": True},
        {"source": "/services/catering", "destination": "/services/accommodation-hospitality", "permanent": True},
        {"source": "/signature-sessions", "destination": "/services/signature-sessions", "permanent": True},
        {"source": "/giveaways-offers", "destination": "/services/giveaways-offers", "permanent": True},
    ]
    redirects = additions + redirects
    config["redirects"] = redirects
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    sitemap = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://www.salvationstudios.co.uk/</loc><lastmod>2026-06-05</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/recording-studio-brighton/</loc><lastmod>2026-06-02</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/rooms/main-studio/</loc><lastmod>2026-06-05</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/rooms/live-room/</loc><lastmod>2026-06-05</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/rooms/control-room/</loc><lastmod>2026-06-02</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/rooms/writing-rooms/</loc><lastmod>2026-06-02</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/rooms/the-bunker/</loc><lastmod>2026-06-03</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/equipment/</loc><lastmod>2026-06-04</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/gallery/</loc><lastmod>2026-06-02</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/testimonials/</loc><lastmod>2026-06-04</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/contact/</loc><lastmod>2026-06-02</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/spaces/</loc><lastmod>2026-06-04</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/services/</loc><lastmod>2026-06-05</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/services/recording/</loc><lastmod>2026-06-05</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/services/mixing/</loc><lastmod>2026-06-05</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/services/mastering/</loc><lastmod>2026-06-05</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/services/live-videos/</loc><lastmod>2026-06-05</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/services/signature-sessions/</loc><lastmod>2026-06-05</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/services/giveaways-offers/</loc><lastmod>2026-06-05</lastmod></url>
  <url><loc>https://www.salvationstudios.co.uk/services/accommodation-hospitality/</loc><lastmod>2026-06-05</lastmod></url>
</urlset>
'''
    (ROOT / "sitemap.xml").write_text(sitemap)


def update_hygiene_script() -> None:
    p = ROOT / "tools/static_hygiene_check.py"
    text = p.read_text()
    text = text.replace('    "services/dry-hire.html",\n    "services/mastering.html",\n    "services/lighting.html",\n    "services/live-videos.html",\n    "services/accommodation.html",\n    "services/catering.html",', '    "services/mastering.html",\n    "services/live-videos.html",\n    "services/signature-sessions.html",\n    "services/giveaways-offers.html",\n    "services/accommodation-hospitality.html",')
    text = text.replace('    "/services/recording", "/services/mixing", "/services/dry-hire",\n    "/services/mastering", "/services/lighting", "/services/live-videos", "/services/accommodation", "/services/catering",', '    "/services/recording", "/services/mixing",\n    "/services/mastering", "/services/live-videos", "/services/signature-sessions", "/services/giveaways-offers", "/services/accommodation-hospitality",')
    p.write_text(text)


def main() -> None:
    # Structural patches first.
    for path in ROOT.rglob("*.html"):
        if any(part in {".git", ".vercel", "node_modules"} for part in path.parts):
            continue
        patch_nav_footer_and_ctas(path)
    update_shared_css()
    update_homepage_services()
    update_services_page()
    # Full approved service pages.
    for slug, data in SERVICE_DATA.items():
        (ROOT / "services" / f"{slug}.html").write_text(service_page(slug, data))
    (ROOT / "services" / "signature-sessions.html").write_text(signature_page())
    (ROOT / "services" / "giveaways-offers.html").write_text(giveaways_page())
    (ROOT / "services" / "accommodation-hospitality.html").write_text(accom_page("accommodation-hospitality"))
    # Remove old visible pages from production route set; redirects preserve legacy hits.
    for rel in ["services/catering.html", "services/accommodation.html", "services/dry-hire.html", "services/lighting.html"]:
        p = ROOT / rel
        if p.exists():
            p.unlink()
    update_config_and_sitemap()
    update_hygiene_script()
    # Final pass for legacy visible terms in source pages outside deleted files.
    for path in ROOT.rglob("*.html"):
        if any(part in {".git", ".vercel", "node_modules"} for part in path.parts):
            continue
        text = path.read_text(errors="ignore")
        text = text.replace('/services/accommodation/', '/services/accommodation-hospitality/')
        text = text.replace('/services/catering/', '/services/accommodation-hospitality/')
        text = text.replace('Catering &amp; Hospitality', 'Accommodation and Hospitality')
        text = text.replace('Catering and Hospitality', 'Accommodation and Hospitality')
        text = text.replace('Catering', 'Hospitality')
        text = text.replace('catering', 'hospitality')
        path.write_text(text)

if __name__ == "__main__":
    main()
