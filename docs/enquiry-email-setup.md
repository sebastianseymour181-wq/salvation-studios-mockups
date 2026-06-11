# Enquiry Email Setup

The site form submits to `/api/enquiry`, which sends enquiry emails through Resend.

Required Vercel production environment variable:

- `RESEND_API_KEY`: Resend API key with permission to send from the chosen sender domain.

Optional Vercel production environment variables:

- `ENQUIRY_TO_EMAIL`: Comma-separated recipient list. Defaults to `info@salvationstudios.co.uk`.
- `ENQUIRY_FROM_EMAIL`: Verified sender address. Defaults to `Salvation Studios <onboarding@resend.dev>`, but production should use a verified Salvation sender such as `Salvation Studios <info@salvationstudios.co.uk>` or a verified subdomain sender.

After adding or changing environment variables, redeploy production.
