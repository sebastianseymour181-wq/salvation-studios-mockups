#!/usr/bin/env python3
"""Idempotently install the shared, consent-gated GTM entrypoint on static pages."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
HEAD='''\n<!-- Sitewide Google Tag Manager GTM-TKKWMVXR: consent defaults run before the container. -->
<script src="/site-consent.js?v=20261104" data-gtm-container="GTM-TKKWMVXR"></script>
<link rel="stylesheet" href="/site-consent.css?v=20261104">
'''
BODY='''\n<!-- Google Tag Manager (noscript): inert without an explicit optional-cookie choice. -->
<noscript><iframe data-consent-src="https://www.googletagmanager.com/ns.html?id=GTM-TKKWMVXR" height="0" width="0" title="Google Tag Manager" style="display:none;visibility:hidden"></iframe></noscript>
'''
files=[]
for p in ROOT.rglob('*.html'):
 if any(part in {'.git','.qa','node_modules','.vercel'} for part in p.relative_to(ROOT).parts):continue
 s=p.read_text()
 if 'data-gtm-container="GTM-TKKWMVXR"' not in s:
  # Keep the encoding declaration first; execute consent before any other scripts.
  s,n=re.subn(r'(<meta\s+charset=[^>]+>)',lambda m:m[0]+HEAD,s,count=1,flags=re.I)
  if not n:s=re.sub(r'(<head[^>]*>)',lambda m:m[0]+HEAD,s,count=1,flags=re.I)
  s=re.sub(r'(<body\b[^>]*>)',lambda m:m[0]+BODY,s,count=1,flags=re.I)
 s=re.sub(r'/enquiry\.js\?v=[^"\s]+','/enquiry.js?v=20261104-measurement',s)
 p.write_text(s);files.append(str(p.relative_to(ROOT)))
print(f'Installed on {len(files)} HTML pages')
