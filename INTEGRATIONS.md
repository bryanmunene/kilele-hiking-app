# Free integration setup

The app works without these accounts. Activity-file imports and compressed image
uploads work with the existing database. No domain purchase is required for them.
Keys are not included in this repository. The administrator's **Integrations**
page reports configuration presence, not a successful provider verification.

## Email: Gmail API for a domain-free sender

Use one Gmail account owned by the organizer as the sender. App users do not
connect their mailboxes. The Gmail API sends over HTTPS, which works on Render
Free. Render Free blocks the usual SMTP ports, so a Gmail app password alone is
not sufficient on that host.

1. Create a Google Cloud project and enable the Gmail API. This setup does not
   require a billing account or a paid domain.
2. Configure Google Auth Platform branding and audience for your own sender
   account. Request only `https://www.googleapis.com/auth/gmail.send`.
3. Create an OAuth client of type **Desktop app** and download its client JSON.
4. Before long-term use, change the OAuth app's publishing status from Testing
   to In production. Testing-mode Gmail refresh tokens expire after seven days.
   Google may require additional verification depending on your app and scope;
   this sender authorization is for your own mailbox, not a public Google login.
5. Install the local helper dependency and run it from the repository:

   ```powershell
   python -m pip install "google-auth-oauthlib>=1.2,<2"
   python scripts/authorize_gmail.py --client-json "C:/path/client_secret.json" --sender "your-account@gmail.com"
   ```

6. Sign in to the **same Gmail sender account** in the browser. The script writes
   `.env.gmail.local`, which is ignored by Git. It never prints the credentials.
7. Import those four values into the Render backend environment:
   `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`, `FROM_EMAIL`.
8. Set `FRONTEND_URL` to
   `https://kilele-hiking-api.onrender.com`.
9. Deploy the backend. Request a reset for your own Kilele account in **Sign in >
   Reset password** and verify delivery, the link, and the new login. Existing
   sessions and old API access tokens are revoked after a successful reset.

The public organizer sender is `kileleexplorers@gmail.com`. After importing
credentials, use **Organizer > Operations > Send test to my inbox**, then confirm
receipt in that Kilele administrator account's inbox. A provider accepting a
message is not proof of delivery. Retry queued notifications from Operations
after the sender is authorized. No password or refresh token belongs in chat.

Mail is quota-limited. Consumer Gmail can block sending after more than 500
messages in a day; limits and abuse protections may be stricter for new accounts.
Do not use this setup for bulk marketing. Refresh tokens can also be revoked by
the account owner or by Google; the provider must remain authorized.

Existing SendGrid credentials still work through HTTPS without an extra SDK.
Brevo is also supported with `BREVO_API_KEY` and a verified `FROM_EMAIL`; it offers
300 sends/day on its free plan. Its domain-authentication requirements mean it is
not the default for this domain-free deployment. SMTP remains supported for
hosts that allow it, with TLS and connection timeouts.

Sources: [Gmail API sending](https://developers.google.com/workspace/gmail/api/guides/sending),
[Google OAuth audience](https://support.google.com/cloud/answer/15549945),
[Gmail limits](https://support.google.com/mail/answer/22839),
[Render Free restrictions](https://render.com/docs/free),
[Brevo free plan](https://help.brevo.com/hc/en-us/articles/208580669-FAQs-What-are-the-limits-of-the-Free-plan).

## Strava: use activity-file imports for the free setup

Strava changed its developer program on June 1, 2026. New Standard Tier developers
need a Strava subscription. Extended Access has no subscription requirement but
requires Strava approval; approval cannot be assumed. OAuth should stay disabled
for a strictly free deployment unless the account qualifies for that access.

The free alternative is **Wearables > Import**. Export an activity from your
device or Strava, then import GPX, FIT, or TCX. Tracks and statistics are saved even
without selecting a catalog trail, and importing the same file again does not
duplicate the session.

The old Bluetooth activity-sync prototype has been removed: it could not return
recorded activity data to Streamlit and did not implement watch-specific sync.
Direct Bluetooth watch synchronization is not supported by this deployment.

When you have an approved API application, set these on the Render backend:

```dotenv
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
STRAVA_REDIRECT_URI=https://kilele-hiking-api.onrender.com/Strava
```

Set the Strava application's Authorization Callback Domain to
`kilele-hiking-api.onrender.com`.
The repaired flow uses expiring, single-use state tied to the signed-in user.
It requests `read` and `activity:read`, excluding private activities and privacy
zone data. Reconnection is needed if an older authorization granted different
scopes. The app supports manual sync; automatic sync on a sleeping free service
is best effort, not immediate delivery.

Optional webhook subscriptions must use
`https://kilele-hiking-api.onrender.com/api/strava/webhook?token=YOUR_WEBHOOK_VERIFY_TOKEN`
as their callback URL and the same `STRAVA_WEBHOOK_VERIFY_TOKEN` for verification.
Webhook background work opens its own database session. Do not publish that URL
with its real token; manual sync and the hourly scheduler do not require webhooks.

Source: [Strava's June 2026 announcement](https://communityhub.strava.com/insider-journal-9/an-update-to-our-developer-program-13428).

## M-Pesa: free sandbox first, business approval for real payments

Create a Daraja account and sandbox app in
[Safaricom Daraja](https://developer.safaricom.co.ke/).
Add these values to Render, not Streamlit:

```dotenv
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_SHORTCODE=174379
MPESA_PASSKEY=
MPESA_TRANSACTION_TYPE=CustomerPayBillOnline
API_BASE_URL=https://kilele-hiking-api.onrender.com
```

Use the sandbox passkey and test details provided by Daraja. Only Kilele admins
can initiate sandbox payments, and sandbox success **never confirms a paid
booking**. Other users can still book free hikes.

The backend supplies a signed callback URL under
`https://kilele-hiking-api.onrender.com/api/payments/mpesa/callback/` for each
payment. Leave the old `MPESA_CALLBACK_URL` unset. Streamlit cannot receive
Daraja callbacks. The backend verifies the amount, phone and request identifiers,
then independently queries Daraja before accepting a payment result.

To accept real money, complete Daraja go-live approval using your own eligible
Till/Paybill and production passkey. Set `MPESA_ENVIRONMENT=production` and replace
all sandbox credentials. For a Till, confirm the correct shortcode, PartyB/till
number and transaction type with Safaricom; `MPESA_PARTY_B` and
`MPESA_TRANSACTION_TYPE=CustomerBuyGoodsOnline` are supported.
Business eligibility and transaction charges are separate from free web hosting.
We have not activated a merchant account or sent any real payment request.

The user can check a pending payment under **My Hikes > Upcoming**. Confirmed failures
can be retried. An ambiguous network failure is left unresolved and blocks a new
charge, because retrying without knowing the first result can charge twice.
If the service restarts before receiving a checkout ID, an organizer must reconcile
that request against Daraja. A free host can delay callbacks during a cold start.

Source: [Safaricom business requirements](https://www.safaricom.co.ke/images/Downloads/Lipa-na-M-PESA-Requirements-2024.pdf).

## Images

Cloudinary remains optional. Photos are oriented correctly, resized and compressed
before database storage. This uses the existing Neon allowance and survives
redeploys; a high-volume photo service would need a different storage budget.
To enable Cloudinary later, add `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY` and
`CLOUDINARY_API_SECRET` to Streamlit secrets (and Render if using API uploads).
