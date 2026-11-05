// Context has its own budget, outside the visitor's 4,000-character message.
const BOOKING_FIELDS = [
  ['preferred_room', 'Preferred room'],
  ['engineering_support', 'Engineer or support required'],
  ['duration', 'Approximate duration'],
];
const CAMPAIGN_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
const AD_KEYS = ['gclid', 'gbraid', 'wbraid'];

function contextText(payload) {
  const lines = [];
  BOOKING_FIELDS.forEach(([key, label]) => {
    const value = typeof payload[key] === 'string' ? payload[key].replace(/[\r\n]/g, ' ').trim().slice(0, 160) : '';
    if (value) lines.push(label + ': ' + value);
  });
  const attribution = payload.attribution;
  const consent = payload.attribution_consent;
  if (!attribution || typeof attribution !== 'object' || !consent || typeof consent !== 'object') return lines.join('\n');
  const permitted = [...(consent.analytics === true ? CAMPAIGN_KEYS : []), ...(consent.advertising === true ? AD_KEYS : [])];
  const campaign = [];
  permitted.forEach(key => {
    if (typeof attribution[key] !== 'string') return;
    const value = attribution[key].trim().slice(0, AD_KEYS.includes(key) ? 200 : 160);
    if (!value || /[@\r\n<>]/.test(value) || (AD_KEYS.includes(key) && !/^[A-Za-z0-9._~-]+$/.test(value))) return;
    campaign.push(key + ': ' + value);
  });
  if (campaign.length) {
    const landing = typeof attribution.landing_page === 'string' ? attribution.landing_page.slice(0, 300) : '';
    if (/^\/(?!\/)[^?\s#<>@]*$/.test(landing)) campaign.push('landing_page: ' + landing);
    lines.push('Campaign attribution (consented):\n' + campaign.join('\n'));
  }
  return lines.join('\n\n');
}

module.exports = { contextText };
