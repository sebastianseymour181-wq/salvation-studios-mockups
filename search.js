(function () {
  'use strict';

  // ─── SEARCH INDEX ────────────────────────────────────────────────────────────
  // [name, category, sub-description, url]
  const RAW = [
    // Console & multitrack
    ['Neve 8068','Console','1973 · 32-channel · fully restored','/equipment/'],
    ['Pro Tools HDX','Multitrack','Mac Studio (Apple Silicon)','/equipment/'],

    // Monitoring
    ['ATC SCM200asl','Monitoring','Soffit-mounted main monitors','/equipment/'],
    ['ATC SCM25A Pro','Monitoring','Near-field monitors','/equipment/'],
    ['ATC SCM0.1/15 Pro','Monitoring','Subwoofer','/equipment/'],
    ['Genelec 8040B','Monitoring','Studio monitors','/equipment/'],
    ['Genelec 8030C','Monitoring','3× studio monitors','/equipment/'],
    ['Yamaha NS10','Monitoring','Classic near-field reference','/equipment/'],
    ['Auratone Cube 5','Monitoring','Check mix speaker','/equipment/'],
    ['Focal Solo6 Be','Monitoring','Bunker monitors','/equipment/'],
    ['Antelope Audio Satori','Monitoring','Mastering monitor controller','/equipment/'],

    // Outboard – preamps & EQ
    ['API 312','Preamp','4× 500-series mic pre','/equipment/'],
    ['Telefunken V72b','Preamp','2× vintage mic pre','/equipment/'],
    ['Legendary Rosser M.A 75','Preamp','2× ex-Rockfield Studios','/equipment/'],
    ['Neve 54 Series Console','Preamp','12-channel Neve 34128','/equipment/'],
    ['API 3124','Preamp','4-channel API 312 pre','/equipment/'],
    ['Telefunken V72','Preamp','Bunker valve preamp','/equipment/'],
    ['A Designs REDDI','DI','Tube direct box','/equipment/'],
    ['Pultec EQM-1S3','EQ','2× mastering equaliser','/equipment/'],
    ['Manley Massive Passive','EQ','Stereo equaliser','/equipment/'],
    ['Thermionic Culture The Swift','EQ','2-channel valve EQ','/equipment/'],
    ['Maag EQ4','EQ','6-band with Air Band','/equipment/'],

    // Outboard – compression
    ['Urei 1176 LN Rev G','Compressor','2× FET compressor','/equipment/'],
    ['Tube-Tech CL 1B','Compressor','Optical compressor','/equipment/'],
    ['Empirical Labs Distressor','Compressor','2× multi-ratio compressor','/equipment/'],
    ['API 2500','Compressor','Bus compressor','/equipment/'],
    ['Smart Research C1','Compressor','Bus compressor','/equipment/'],
    ['Dbx 160','Compressor','2× VU-meter compressor','/equipment/'],
    ['ADL 1000','Compressor','2×','/equipment/'],
    ['Rupert Neve Designs Portico 543','Compressor','500-series compressor','/equipment/'],
    ['Crane Song STC-8','Compressor','Compressor / limiter','/equipment/'],
    ['Neve 2254/R','Compressor','2× limiter compressor','/equipment/'],
    ['Urei 1178','Compressor','Stereo compressor','/equipment/'],
    ['SSL G-Bus Compressor','Compressor','Lord SSL stereo bus','/equipment/'],
    ['Empirical Labs EL8 Distressor','Compressor','Multi-mode compressor','/equipment/'],

    // Outboard – reverbs & effects
    ['Bricasti M7','Reverb','Digital reverb','/equipment/'],
    ['Lexicon PCM 80','Reverb','Digital reverb','/equipment/'],
    ['EMT 140','Reverb','Stereo plate reverb','/equipment/'],
    ['Roland RE-201','Effects','Space Echo','/equipment/'],
    ['Roland Space Echo','Effects','RE-201 tape echo','/equipment/'],
    ['Eventide Harmonizer','Effects','Pitch / effects processor','/equipment/'],
    ['Watkins Copicat Mk2','Effects','Tape echo','/equipment/'],
    ['Klemt Echolette e51','Effects','Vintage tape echo','/equipment/'],
    ['Great British Spring Reverb','Reverb','Spring reverb unit','/equipment/'],
    ['Thermionic Culture Culture Vulture','Effects','Mastering harmonic saturator','/equipment/'],
    ['Telefunken Echomixer','Effects','Vintage mixer/echo','/equipment/'],
    ['Roland RE-201 Space Echo','Effects','Tape echo – Bunker','/equipment/'],
    ['TC Electronic 2290','Effects','Digital delay','/equipment/'],
    ['EHX Memory Man','Effects','Analogue delay','/equipment/'],
    ['Strymon Flint','Effects','Reverb & tremolo','/equipment/'],
    ['Thermionic Culture The Little Red Bustard','Summing','Valve summing mixer','/equipment/'],

    // Bunker DAW & playback
    ['Universal Audio Apollo x16','Interface','16-channel Thunderbolt interface','/equipment/'],
    ['Revox B77','Tape','¼" 2-track tape recorder','/equipment/'],
    ['Sony TC-134','Tape','SD cassette recorder','/equipment/'],
    ['Apple Mac Studio','Computer','M1 Max – Bunker DAW','/equipment/'],

    // MIDI
    ['Arturia KeyLab Essential 61','MIDI','61-key MIDI controller','/equipment/'],
    ['Arturia BeatStep','MIDI','Step sequencer / MIDI controller','/equipment/'],
    ['Emagic Unitor8','MIDI','MIDI interface','/equipment/'],
    ['Korg NanoKey2','MIDI','Compact MIDI keyboard','/equipment/'],

    // Microphones – large diaphragm
    ['Sony C-800G','Microphone','Flagship valve vocal condenser','/equipment/'],
    ['Neumann U87 Ai','Microphone','2× FET condenser','/equipment/'],
    ['Neumann U87ai','Microphone','3× studio condensers','/equipment/'],
    ['Flea 47 Vintage','Microphone','Vintage-style valve condenser','/equipment/'],
    ['Bock iFet','Microphone','Large diaphragm FET condenser','/equipment/'],
    ['Neumann CMV 563','Microphone','Vintage modular condenser','/equipment/'],
    ['AKG C414','Microphone','Pair + 1 multi-pattern condenser','/equipment/'],
    ['Soyuz 023 Bomblet','Microphone','Large diaphragm condenser','/equipment/'],
    ['Austrian Audio OC818','Microphone','Multi-pattern condenser','/equipment/'],
    ['Sound Deluxe U99','Microphone','Large diaphragm valve condenser','/equipment/'],
    ['Neumann M150','Microphone','2× guest mic (subject to availability)','/equipment/'],
    ['Neumann U47 FET','Microphone','2× guest mic (subject to availability)','/equipment/'],

    // Microphones – small diaphragm
    ['Neumann KM 184','Microphone','Matched pair small diaphragm','/equipment/'],
    ['Microtech Gefell M300','Microphone','Matched pair small diaphragm','/equipment/'],
    ['DPA 2011','Microphone','Small diaphragm cardioid','/equipment/'],

    // Microphones – dynamic & ribbon
    ['Shure SM7B','Microphone','Broadcast dynamic','/equipment/'],
    ['Shure SM57','Microphone','4× industry standard dynamic','/equipment/'],
    ['Shure SM58','Microphone','2× vocal dynamic','/equipment/'],
    ['Sennheiser MD421','Microphone','4× multi-purpose dynamic','/equipment/'],
    ['Beyerdynamic M160','Microphone','2× figure-8 ribbon','/equipment/'],
    ['Coles 4038','Microphone','2× BBC ribbon pair','/equipment/'],
    ['AEA R88','Microphone','Stereo ribbon','/equipment/'],
    ['Beyerdynamic M69','Microphone','Dynamic cardioid','/equipment/'],
    ['Vintage Shure 330 Uniron','Microphone','Vintage ribbon','/equipment/'],

    // Microphones – specialist / kick / overhead
    ['AKG D112','Microphone','Kick drum mic','/equipment/'],
    ['AKG D12','Microphone','Vintage kick drum mic','/equipment/'],
    ['AKG 451','Microphone','Small diaphragm condenser','/equipment/'],
    ['Electro-Voice RE20','Microphone','Broadcast / bass dynamic','/equipment/'],
    ['Shure Beta 52A','Microphone','Kick drum mic','/equipment/'],
    ['Shure Beta 91A','Microphone','Boundary kick drum mic','/equipment/'],
    ['Sennheiser e906','Microphone','2× guitar cab mic','/equipment/'],
    ['Audix D4','Microphone','3× tom / kick mic','/equipment/'],

    // Electric guitars
    ['1965 Fender Telecaster','Electric Guitar','Vintage Telecaster','/equipment/#full-inventory'],
    ['1963 Fender Jazzmaster','Electric Guitar','Vintage Jazzmaster','/equipment/#full-inventory'],
    ['Fender Stratocaster','Electric Guitar','American Custom Shop','/equipment/#full-inventory'],
    ['1983 Gibson ES-335','Electric Guitar','Semi-hollow body','/equipment/#full-inventory'],
    ['1978 Gibson Les Paul','Electric Guitar','25th Anniversary Edition','/equipment/#full-inventory'],
    ['1970 Gibson SG','Electric Guitar','Vintage SG','/equipment/#full-inventory'],
    ['Duesenberg Gran Royale','Electric Guitar','Semi-hollow','/equipment/#full-inventory'],
    ['Millman HSS Stratocaster','Electric Guitar','Custom build','/equipment/#full-inventory'],
    ['1989 Kramer Baretta','Electric Guitar','Vintage Kramer','/equipment/#full-inventory'],

    // Acoustic guitars
    ['Gibson The Firebird','Acoustic Guitar','Acoustic Firebird','/equipment/#full-inventory'],
    ['Taylor 214CE DLX','Acoustic Guitar','Electro-acoustic','/equipment/#full-inventory'],
    ['1963 Martin D12-35','Acoustic Guitar','Vintage 12-string Martin','/equipment/#full-inventory'],

    // Bass
    ['Sandberg California Forty-Eight','Bass Guitar','4-string bass','/equipment/#full-inventory'],
    ['Sandberg California TM5','Bass Guitar','5-string bass','/equipment/#full-inventory'],
    ['1982 Rickenbacker 4003','Bass Guitar','Vintage Rickenbacker','/equipment/#full-inventory'],
    ['Fender Precision Bass','Bass Guitar','American Deluxe','/equipment/#full-inventory'],

    // Guitar amps
    ['Marshall JCM 2000','Guitar Amp','Classic Marshall head','/equipment/#full-inventory'],
    ['Marshall JCM 2000 TSL60','Guitar Amp','50W Marshall combo','/equipment/#full-inventory'],
    ['1971 Marshall JMP 50','Guitar Amp','With matching Thames Dittons cab','/equipment/#full-inventory'],
    ['Marshall JTM45 Offset','Guitar Amp','1 of 300 · point-to-point re-issue','/equipment/#full-inventory'],
    ['1972 Marshall 2046','Guitar Amp','Reverb-Trem head','/equipment/#full-inventory'],
    ['1965 Vox AC30','Guitar Amp','Vintage Vox combo','/equipment/#full-inventory'],
    ['1964 Fender Bassman','Guitar Amp','Vintage Fender head','/equipment/#full-inventory'],
    ['1993 Fender Blues DeVille','Guitar Amp','American-made combo','/equipment/#full-inventory'],
    ['Fender Pro Reverb','Guitar Amp','1960s Fender combo','/equipment/#full-inventory'],
    ['Fender Super Sonic','Guitar Amp','Modern Fender amp','/equipment/#full-inventory'],
    ['1972 Hiwatt DR103','Guitar Amp','With matching cabinet','/equipment/#full-inventory'],
    ['1972 Orange OR120','Guitar Amp','Vintage Orange head','/equipment/#full-inventory'],
    ['Mesa Boogie Mark V','Guitar Amp','Multi-channel head','/equipment/#full-inventory'],
    ['ENGL Retro Tube 50','Guitar Amp','50W tube head','/equipment/#full-inventory'],
    ['1973 Sound City B120','Guitar Amp','With matching cabinet','/equipment/#full-inventory'],
    ['Overdrive Special Norbury','Guitar Amp','Dumble SLO replica','/equipment/#full-inventory'],
    ['Original Soldano GTO Supercharger','Guitar Amp','Pre-amp stage of Soldano SLO','/equipment/#full-inventory'],
    ['1962 Selmer Treble-n-Bass Fifty','Guitar Amp','Vintage Selmer with cab','/equipment/#full-inventory'],
    ['1963 Selmer Zodiac Twin 30','Guitar Amp','Vintage combo','/equipment/#full-inventory'],
    ['1972 Ampeg GU-12','Guitar Amp','Vintage Ampeg','/equipment/#full-inventory'],

    // Bass amps
    ['Ampeg B-15-N','Bass Amp','Portaflex flip-top','/equipment/#full-inventory'],
    ['1972 Ampeg V4B','Bass Amp','With matching cabinet','/equipment/#full-inventory'],
    ['Ampeg SVT-4 Pro','Bass Amp','Professional bass head','/equipment/#full-inventory'],
    ['Ampeg BA300','Bass Amp','Combo bass amp','/equipment/#full-inventory'],

    // Drums
    ['C&C Custom Kit','Drums','22" kick · 16" floor · 14" mid · 13" hi','/equipment/#full-inventory'],
    ['Tama Starclassic Maple','Drums','5-piece maple kit','/equipment/#full-inventory'],
    ['70s Ludwig Cortex','Drums','Vintage Ludwig 5-piece','/equipment/#full-inventory'],
    ['Craviotto Snare','Drums','14" custom snare','/equipment/#full-inventory'],
    ['Ludwig 404 Snare','Drums','14" classic snare','/equipment/#full-inventory'],
    ['Sonor Benny Greb','Drums','13" signature snare','/equipment/#full-inventory'],
    ['Zildjian K Cymbals','Drums','Full set of K cymbals','/equipment/#full-inventory'],

    // Keyboards & pianos
    ['Yamaha C3 Baby Grand','Piano','Baby grand piano','/equipment/#full-inventory'],
    ['Hammond B3','Keyboards','With Leslie 145 rotary cabinet','/equipment/#full-inventory'],
    ['Fender Rhodes Mark 1','Keyboards','Electric piano','/equipment/#full-inventory'],
    ['Hohner Clavinet D6','Keyboards','1971 vintage Clavinet','/equipment/#full-inventory'],
    ['Wurlitzer EP200A','Keyboards','1978 electric piano','/equipment/#full-inventory'],
    ['Nord Stage 2','Keyboards','Stage keyboard','/equipment/#full-inventory'],
    ['Dave Smith Prophet Rev 2','Synthesiser','Analogue poly synth','/equipment/#full-inventory'],
    ['Roland Juno-X','Synthesiser','Digital/analogue synth','/equipment/#full-inventory'],
    ['Roland Jupiter-4','Synthesiser','Vintage analogue synth','/equipment/#full-inventory'],
    ['Korg Trinity','Keyboards','Workstation keyboard','/equipment/#full-inventory'],
    ['Korg MS-20','Synthesiser','Semi-modular analogue synth','/equipment/#full-inventory'],
    ['Mellotron M4000D','Keyboards','Digital Mellotron','/equipment/#full-inventory'],
    ['Yamaha Reface DX','Synthesiser','FM desktop synth','/equipment/#full-inventory'],
    ['1970 Optigan','Keyboards','Optical organ','/equipment/#full-inventory'],
    ['Crumar Multiman-S','Keyboards','Vintage string machine','/equipment/#full-inventory'],
    ['EDP Wasp','Synthesiser','Vintage analogue mono synth','/equipment/#full-inventory'],
    ['Hohner Pianet T','Keyboards','Reed electric piano','/equipment/#full-inventory'],
    ['Sequential Circuits MultiTrak','Synthesiser','Vintage poly synth','/equipment/#full-inventory'],
    ['Siel Orchestra 2','Synthesiser','Vintage string/brass synth','/equipment/#full-inventory'],

    // Rooms
    ['Live Room','Room','13m vaulted 1910 hall · 9.4×8.2m · John Flynn acoustics','/rooms/live-room/'],
    ['Control Room','Room','Neve 8068 · ATC monitors · John Flynn design','/rooms/control-room/'],
    ['Vocal Booth','Room','Precision isolation · direct sightlines to control room','/rooms/live-room/'],
    ['Iso Booths','Room','2× retractable glass-fronted isolation booths','/rooms/live-room/'],
    ['Isolation Booths','Room','Simultaneous tracking · full separation','/rooms/live-room/'],
    ['Amp Booth','Room','Full isolation · guitar & bass at real volume','/rooms/live-room/'],
    ['The Bunker','Room','Self-contained writing & production wing','/rooms/the-bunker/'],
    ['Mezzanine Room','Room','Elevated writing room overlooking main studio','/rooms/the-bunker/#mezzanine-room'],
    ['Subterranean Room','Room','Underground writing & chill-out space','/rooms/the-bunker/#subterranean-room'],
    ['Writing Rooms','Room','Bunker writing wing with production setup','/rooms/writing-rooms/'],
    ['Main Studio','Room','The full Salvation complex — hall, control room & booths','/rooms/live-room/'],

    // Services
    ['Recording','Service','Full studio recording sessions','/services/recording/'],
    ['Mixing','Service','Mix on the Neve 8068 with ATC monitoring','/services/mixing/'],
    ['Mastering','Service','Mastering services','/services/mastering/'],
    ['Writing','Service','Writing rooms & writing camps','/rooms/writing-rooms/'],
    ['Live Videos','Service','Filmed live sessions','/services/live-videos/'],
    ['Accommodation','Service','On-site accommodation','/services/accommodation/'],
    ['Catering','Service','Locally prepared catering & hospitality','/services/catering/'],
    ['Hospitality','Service','Catering, lounge & session support','/services/catering/'],
    ['Dry Hire','Service','Bring your own team','/services/dry-hire/'],
    ['Lighting','Service','Configurable studio lighting for sessions & filming','/services/lighting/'],

    // Pages
    ['Equipment List','Page','Full gear inventory: console, mics, outboard, amps, drums, keys','/equipment/'],
    ['Gallery','Page','Photos from inside Salvation Studios','/gallery/'],
    ['Testimonials','Page','Artists and engineers on recording at Salvation','/testimonials/'],
    ['Spaces Overview','Page','Overview of all studio spaces','/spaces/'],
    ['Contact','Page','Enquire about your next session','/contact/'],
  ];

  const INDEX = RAW.map(([name, cat, sub, url]) => ({
    name, cat, sub, url,
    _name: name.toLowerCase(),
    _sub: sub.toLowerCase(),
    _cat: cat.toLowerCase(),
  }));

  // ─── SUGGESTIONS ─────────────────────────────────────────────────────────────
  const SUGGESTIONS = [
    'Neve 8068', 'Sony C-800G', 'Marshall', 'Hammond B3',
    'Fender Rhodes', 'Lexicon PCM 80', 'Live Room', 'Drums',
    'Microphones', 'Recording', 'The Bunker', 'Vox AC30',
    'Guitar amps', 'Mellotron',
  ];

  // ─── SEARCH LOGIC ────────────────────────────────────────────────────────────
  function search(raw) {
    const q = raw.trim().toLowerCase();
    if (!q) return [];
    const words = q.split(/\s+/);

    return INDEX
      .map(item => {
        let score = 0;
        for (const w of words) {
          if (item._name.startsWith(w)) score += 100;
          else if (item._name.includes(w)) score += 60;
          if (item._sub.includes(w)) score += 30;
          if (item._cat.includes(w)) score += 20;
        }
        return score > 0 ? { ...item, score } : null;
      })
      .filter(Boolean)
      .sort((a, b) => b.score - a.score)
      .slice(0, 24);
  }

  // ─── CSS ─────────────────────────────────────────────────────────────────────
  const CSS = `
.ss-btn {
  display: flex; align-items: center; justify-content: center;
  width: 38px; height: 38px; border-radius: 50%;
  background: rgba(124,58,237,0.1); border: 1px solid rgba(139,92,246,0.3);
  color: #D8B4FE; cursor: pointer; transition: background .2s, border-color .2s;
  flex-shrink: 0; margin-left: 16px;
}
.ss-btn:hover { background: rgba(124,58,237,0.22); border-color: rgba(157,95,245,0.6); color: #F5F3FF; }
.ss-overlay {
  position: fixed; inset: 0; z-index: 10000;
  background: rgba(7,0,15,0.82); backdrop-filter: blur(6px);
  display: flex; align-items: flex-start; justify-content: center;
  padding: 80px 16px 40px; opacity: 0; pointer-events: none;
  transition: opacity .2s;
}
.ss-overlay.open { opacity: 1; pointer-events: all; }
.ss-panel {
  width: 100%; max-width: 660px;
  background: #0D0020; border: 1px solid rgba(139,92,246,0.35);
  border-radius: 16px; overflow: hidden;
  box-shadow: 0 0 0 1px rgba(139,92,246,0.1), 0 24px 80px rgba(0,0,0,0.9);
  transform: translateY(-12px); transition: transform .2s;
}
.ss-overlay.open .ss-panel { transform: translateY(0); }
.ss-bar {
  display: flex; align-items: center; gap: 10px;
  padding: 16px 20px; border-bottom: 1px solid rgba(139,92,246,0.2);
}
.ss-bar svg { flex-shrink: 0; color: #9B7EC8; }
.ss-input {
  flex: 1; background: transparent; border: none; outline: none;
  color: #F5F3FF; font-size: 17px; font-family: 'Montserrat', sans-serif;
  font-weight: 400; caret-color: #C084FC;
}
.ss-input::placeholder { color: #9B7EC8; }
.ss-close {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 8px; border: none;
  background: rgba(124,58,237,0.1); color: #9B7EC8; cursor: pointer;
  transition: background .15s, color .15s; flex-shrink: 0;
}
.ss-close:hover { background: rgba(124,58,237,0.25); color: #F5F3FF; }
.ss-body { max-height: 60vh; overflow-y: auto; padding: 20px; }
.ss-body::-webkit-scrollbar { width: 4px; }
.ss-body::-webkit-scrollbar-track { background: transparent; }
.ss-body::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.3); border-radius: 4px; }
.ss-hint {
  font-size: 11px; font-family: 'Montserrat', sans-serif;
  letter-spacing: .09em; text-transform: uppercase;
  color: #9B7EC8; margin-bottom: 14px; text-align: center;
}
.ss-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.ss-chip {
  display: inline-block; padding: 7px 14px; border-radius: 100px;
  border: 1px solid rgba(139,92,246,0.3); background: rgba(124,58,237,0.07);
  color: #D8B4FE; font-size: 13px; font-family: 'Montserrat', sans-serif;
  cursor: pointer; transition: border-color .15s, background .15s, color .15s;
}
.ss-chip:hover { border-color: rgba(157,95,245,0.65); background: rgba(124,58,237,0.18); color: #F5F3FF; }
.ss-group-title {
  font-size: 10px; font-family: 'Montserrat', sans-serif;
  letter-spacing: .1em; text-transform: uppercase; color: #9B7EC8;
  margin: 18px 0 6px; padding-bottom: 6px;
  border-bottom: 1px solid rgba(139,92,246,0.15); text-align: center;
}
.ss-group-title:first-child { margin-top: 0; }
.ss-result {
  display: flex; align-items: baseline; gap: 12px;
  padding: 10px 12px; border-radius: 8px; text-decoration: none;
  transition: background .15s;
}
.ss-result:hover, .ss-result.focused { background: rgba(124,58,237,0.14); }
.ss-result-name { font-size: 14px; color: #F5F3FF; font-family: 'Montserrat', sans-serif; font-weight: 500; flex-shrink: 0; }
.ss-result-sub { font-size: 12px; color: #9B7EC8; font-family: 'Montserrat', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ss-empty { color: #9B7EC8; font-size: 14px; font-family: 'Montserrat', sans-serif; padding: 8px 0; }
`;

  // ─── HTML ─────────────────────────────────────────────────────────────────────
  const SEARCH_BTN_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>`;
  const CLOSE_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>`;

  // ─── INIT ─────────────────────────────────────────────────────────────────────
  function init() {
    // Inject CSS
    const styleEl = document.createElement('style');
    styleEl.textContent = CSS;
    document.head.appendChild(styleEl);

    // Inject search button into nav
    const nav = document.getElementById('nav');
    if (nav) {
      const btn = document.createElement('button');
      btn.className = 'ss-btn';
      btn.id = 'ssBtn';
      btn.setAttribute('aria-label', 'Search the site');
      btn.innerHTML = SEARCH_BTN_SVG;
      const navLogo = nav.querySelector('.nav-logo');
      if (navLogo) navLogo.appendChild(btn);
      else nav.prepend(btn);
    }

    // Inject search overlay
    const overlay = document.createElement('div');
    overlay.id = 'ssOverlay';
    overlay.className = 'ss-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Site search');
    overlay.innerHTML = `
      <div class="ss-panel" id="ssPanel">
        <div class="ss-bar">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
          <input class="ss-input" id="ssInput" type="search" autocomplete="off" spellcheck="false" placeholder="Search equipment, rooms, services…">
          <button class="ss-close" id="ssClose" aria-label="Close search">${CLOSE_SVG}</button>
        </div>
        <div class="ss-body" id="ssBody"></div>
      </div>`;
    document.body.appendChild(overlay);

    const input = document.getElementById('ssInput');
    const body  = document.getElementById('ssBody');

    // ── render helpers ─────────────────────────────────────────────
    function renderSuggestions() {
      const chips = SUGGESTIONS.map(s =>
        `<button class="ss-chip" data-query="${s}">${s}</button>`
      ).join('');
      body.innerHTML = `<p class="ss-hint">Popular searches</p><div class="ss-chips">${chips}</div>`;
      body.querySelectorAll('.ss-chip').forEach(c =>
        c.addEventListener('click', () => { input.value = c.dataset.query; input.dispatchEvent(new Event('input')); input.focus(); })
      );
    }

    function renderResults(results) {
      if (!results.length) {
        body.innerHTML = `<p class="ss-empty">Nothing found — try a brand, model name or room.</p>`;
        return;
      }
      // Group by category
      const groups = {};
      results.forEach(r => { (groups[r.cat] = groups[r.cat] || []).push(r); });
      let html = '';
      for (const [cat, items] of Object.entries(groups)) {
        html += `<div class="ss-group-title">${cat}</div>`;
        items.slice(0, 5).forEach(item => {
          html += `<a class="ss-result" href="${item.url}">
            <span class="ss-result-name">${item.name}</span>
            <span class="ss-result-sub">${item.sub}</span>
          </a>`;
        });
      }
      body.innerHTML = html;
    }

    // ── open / close ───────────────────────────────────────────────
    function openSearch() {
      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
      renderSuggestions();
      setTimeout(() => input.focus(), 50);
    }

    function closeSearch() {
      overlay.classList.remove('open');
      document.body.style.overflow = '';
      input.value = '';
    }

    // ── events ─────────────────────────────────────────────────────
    const btn = document.getElementById('ssBtn');
    if (btn) btn.addEventListener('click', openSearch);

    document.getElementById('ssClose').addEventListener('click', closeSearch);

    overlay.addEventListener('click', e => {
      if (!document.getElementById('ssPanel').contains(e.target)) closeSearch();
    });

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && overlay.classList.contains('open')) closeSearch();
      // cmd/ctrl + k to open
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        overlay.classList.contains('open') ? closeSearch() : openSearch();
      }
    });

    input.addEventListener('input', () => {
      const q = input.value.trim();
      if (!q) { renderSuggestions(); return; }
      renderResults(search(q));
    });

    // keyboard navigation in results
    input.addEventListener('keydown', e => {
      const results = body.querySelectorAll('.ss-result');
      if (!results.length) return;
      const focused = body.querySelector('.ss-result.focused');
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        const next = focused ? (focused.nextElementSibling?.classList.contains('ss-result') ? focused.nextElementSibling : results[0]) : results[0];
        focused?.classList.remove('focused');
        next?.classList.add('focused');
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        const prev = focused ? (focused.previousElementSibling?.classList.contains('ss-result') ? focused.previousElementSibling : results[results.length - 1]) : results[results.length - 1];
        focused?.classList.remove('focused');
        prev?.classList.add('focused');
      } else if (e.key === 'Enter' && focused) {
        e.preventDefault();
        focused.click();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
