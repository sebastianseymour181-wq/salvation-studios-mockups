# Enquiry Email Setup

The site form submits to `/api/enquiry`, which sends enquiry emails through Resend.

Required Vercel production environment variables:

- `RESEND_API_KEY`: Resend API key with permission to send from the chosen sender domain.
- `ENQUIRY_FROM_EMAIL`: Verified sender address, such as `Salvation Studios <info@salvationstudios.co.uk>` or a verified subdomain sender.

Optional Vercel production environment variables:

- `ENQUIRY_TO_EMAIL`: Comma-separated recipient list. Defaults to `info@salvationstudios.co.uk`.

After adding or changing environment variables, redeploy production.

Recommended Vercel Firewall rule:

- Rate-limit `POST /api/enquiry` to roughly 5 requests per minute per IP, with a stronger block or challenge threshold above that.
