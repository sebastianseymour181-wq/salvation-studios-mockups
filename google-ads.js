/* Progressive enhancement for the landing page's artist credits only. */
(() => {
  'use strict';
  const credits = document.querySelector('[data-artist-credits]');
  if (!credits || !window.matchMedia) return;
  const toggle = credits.querySelector('.ss-landing-credits-toggle');
  if (!toggle) return;
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused = false;
  const render = () => {
    credits.classList.toggle('is-animated', !motion.matches);
    credits.classList.toggle('is-paused', paused);
    toggle.hidden = motion.matches;
    toggle.textContent = paused ? 'Resume artist credits' : 'Pause artist credits';
  };
  toggle.addEventListener('click', () => { paused = !paused; render(); });
  if (motion.addEventListener) motion.addEventListener('change', render);
  else if (motion.addListener) motion.addListener(render);
  render();
})();
