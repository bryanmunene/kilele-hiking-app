# Kilele Operations

## Hosting

The primary deployment uses one **free Render web service** for both Streamlit
and FastAPI, with persistent data in the existing **Neon PostgreSQL** database.
The existing Streamlit Community Cloud address can remain a fallback.

Render settings for the existing `kilele-hiking-api` service:

| Setting | Value |
| --- | --- |
| Root Directory | Empty (repository root) |
| Build Command | `pip install -r requirements-hosted.txt` |
| Start Command | `python scripts/serve_hosted.py` |
| Health Check Path | `/_ready` |
| Plan | Free |
| FRONTEND_URL | `https://kilele-hiking-api.onrender.com` |
| API_BASE_URL | `https://kilele-hiking-api.onrender.com` |
| CORS_ORIGINS | The Render URL and existing Streamlit URL, comma-separated |

Keep the existing DATABASE_URL and SECRET_KEY private in Render's environment
settings. Do not generate a new database or rotate the signing key during a normal
deployment. The supervisor starts Streamlit privately on loopback, proxies its
HTTP/WebSocket traffic, and exits if either child process dies. Render can then
restart the service. `/_ready` checks both the database and the website.

The free Render service sleeps after 15 idle minutes and automatically wakes on
a visit, typically taking about a minute. There is no Streamlit wake button at
the Render URL. This is a hobby/community deployment, **not an always-on service
or a production uptime guarantee**. Free hours, bandwidth, builds, Neon storage
and compute have limits. Keep one Render service and do not enable paid add-ons.
Do not store user files on Render's ephemeral disk. Images use bounded,
metadata-stripped database storage when Cloudinary is not configured.

Provider constraints: [Render Free](https://render.com/docs/free),
[Streamlit app management](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app).

## Backups And Recovery

`.github/workflows/backups.yml` runs daily at 02:17 UTC (05:17 Nairobi), and can
also be started from GitHub Actions. Repository secrets are BACKUP_DATABASE_URL
and BACKUP_ENCRYPTION_KEY. The database URL is used only in the runner environment;
credentials are not committed or supplied as command-line arguments.

Each run makes a consistent PostgreSQL custom-format snapshot, encrypts it with
Fernet authenticated encryption, restores it into a disposable PostgreSQL service,
and verifies core application tables. Only the encrypted artifact is uploaded.
Artifacts expire after seven days. A failed dump or restore fails the workflow;
it does not silently publish a successful backup. The implementation refuses
snapshots larger than 256 MB. Monitor database size and successful backup runs.

The recovery key is also saved in the ignored `.env.backup.local` file. Keep an
independent secure copy; GitHub cannot reveal an Actions secret to recover a lost
key. Never commit it, paste it into chat, or upload a decrypted snapshot.

To recover, download an encrypted artifact, provision an **empty** replacement
PostgreSQL database within available free limits, and set RESTORE_DATABASE_URL
and BACKUP_ENCRYPTION_KEY locally. With compatible PostgreSQL tools installed:

```sh
python backend/backup_service.py restore --file path/to/backup.enc
python scripts/verify_restore.py
```

Alternatively set PG_TOOLS_DOCKER=1 to use PostgreSQL 18 tools through Docker.
The restore command refuses an occupied target and never drops existing tables.
After validation, change the applications' DATABASE_URL to the restored database,
update the backup secret, and redeploy. Do not overwrite the live source while
testing recovery. A restore can recover data deleted since that backup, so apply
any outstanding privacy/deletion requests before reopening the app.

## Integrations That Need Owner Authorization

- **Email:** authorize an HTTPS provider. Gmail API support is implemented and
  avoids Render Free's blocked SMTP ports. Use `scripts/authorize_gmail.py` with
  an owner-created Google OAuth client. Configure the resulting credentials only
  in Render secrets. Gmail test-mode OAuth refresh tokens may expire after seven
  days; complete Google's appropriate publishing/verification steps before relying
  on unattended delivery. Test receipt of welcome, verification, recovery, booking
  and cancellation messages. No mail account is assumed authorized by the code.
- **M-Pesa:** Daraja sandbox credentials allow testing, not real checkout. Live
  payments require Safaricom approval and a valid business shortcode/passkey.
  Paid bookings remain disabled without production credentials. Refunds require
  organizer reconciliation; the app does not promise automatic refunds.
- **Strava:** use exported GPX/FIT/TCX files for the no-credential option. OAuth
  requires an approved developer app and any applicable current Strava access
  requirements. File imports do not depend on Strava API availability.
- **Cloudinary:** optional. Small validated uploads persist in Neon without it,
  but image storage counts against database limits.

Public support: **Kilele Explorers**, **kileleexplorers@gmail.com**.
Review the published privacy and terms pages for your actual organizing practices
before accepting public bookings. They are operational disclosures, not a legal
compliance certification. The hike log is manual; it is not background GPS,
automatic SOS dispatch, or offline navigation.

## Routine Checks

```sh
python -m pip install -r requirements-dev.txt
python -m compileall -q backend frontend scripts tests
python -m unittest discover -s tests -v
python deployment_check.py
```

Use only `tests/seed_browser_fixture.py` with a disposable SQLite database for
browser mutation tests. Never use its fixture account against production.
`tests/browser_layout.cjs` covers 20 routes at five desktop/mobile widths.
Passing tests verify the covered contracts; they do not establish that external
providers are authorized or guarantee performance under production load.

For incidents, check Render health/deploy logs, Neon availability/quotas, the
GitHub Tests and Encrypted backups runs, then the organizer inbox. The inbox
stores support requests, account blocks, moderation resolutions and unsent mail.
After restoring email credentials, Retry email delivery resumes exhausted retries.
For an application regression, use Render's previous successful deployment;
schema changes in this release are additive. Never restore the database merely
to roll back application code.
