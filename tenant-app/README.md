# VoltoShare tenant app

A persistent, server-authorised resident application. This is separate from the static German public website. The latest [app brief](../docs/APP_IMPLEMENTATION_BRIEF.md) takes precedence over the older brand-kit reference for English UI, relative-date demo fixtures, shared household access, non-cancelled reservation counts and the simplified flat sample tariff.

## Stack and boundaries

Django 5.2 LTS provides authentication/password hashing, sessions, CSRF protection, validated invitation-only registration, ORM and migrations. Django Axes limits failed password sign-ins. SQLite is a persistent relational database; two Gunicorn workers share it. WhiteNoise serves collected local assets. No frontend framework or additional service is needed for five small screens.

`core/models.py` and `core/migrations/` define referentially protected records; `services.py` owns booking/billing rules; `provider.py` is the replaceable charger adapter; `views.py` derives household access from active authenticated membership for every API/export/print request. `static/app/app.mjs` and `.css` implement the interface. API contract: [APP_API_CONTRACT.md](../docs/APP_API_CONTRACT.md).

- Reservations reserve access; they never generate sessions or energy charges.
- Sessions record energy and final cost; active readings are explicitly provisional.
- Invoices request payment; tenants cannot mark them paid.
- No real hardware, NFC, email delivery, payment service, dynamic tariff, landlord subscription, tax calculation or property management console is enabled.

## Local setup

Requires Python 3.11+ and a virtual environment. From `tenant-app/`:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p private
# Set a random local secret in your shell; never commit it.
export VOLTO_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
export VOLTO_DB="$PWD/private/app.sqlite3"
export VOLTO_DEMO=1
export VOLTO_APP_URL=http://127.0.0.1:18930
export VOLTO_HOSTS=127.0.0.1,localhost
export VOLTO_CSRF_ORIGINS=http://127.0.0.1:18930
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/gunicorn --bind 127.0.0.1:18930 --workers 2 config.wsgi:application
```

Open `http://127.0.0.1:18930/login/`. The Pi uses `/home/mathis/.local/share/voltoshare-venv/bin/` rather than a repo-local virtualenv. Real secrets, SQLite files, collected static files and local env files are excluded from Git. `.env.example` contains placeholders only; Django reads actual environment variables, not `.env` automatically.

## Authentication and fictional demo

`VOLTO_DEMO` defaults to **0**. With explicit `VOLTO_DEMO=1`, the login page exposes Alex (owner), Sam (member in the same household), and Jordan (owner of another household). Their seeded passwords are unusable; the CSRF-protected demo-entry endpoint accepts only four fixed seeded identities and refuses accounts that have usable passwords. No real credentials are published. The fourth fixture, Taylor, is available through an invitation/login test, not displayed as an initial resident.

**The deployment at the app hostname is deliberately a public fictional demonstration, not a production tenant system.** Changes persist and can be seen by other visitors choosing the same demo persona. Users are told to enter fictional information. Public demo identities must never coexist with real household data; use a separate database and `VOLTO_DEMO=0` before real onboarding. Demo mode is an explicit environment opt-in, not the software default.

An owner creates an email-bound, 48-hour, single-use link. Only its SHA-256 token hash is stored; the full link is returned once. No email is sent. An existing authenticated account must match the invited email; a new account can register only through a valid link, using Django's password validators and hashing. Accepting links is atomic. Revocation/removal immediately disables household access; outstanding invitations for a removed member are also revoked. Historical records remain. Last-owner removal is blocked; ownership transfer is a trusted operator task.

### Trusted real-owner setup

Configure a **separate non-demo database**, property, bays, chargers and tariff using trusted operator tooling/Django ORM. Unknown/stale hardware status must not be treated as free. Provision an initial owner via:

```sh
python manage.py provision_owner --property 1 --apartment A-12 \
  --household 'Example household' --username example-owner \
  --email owner@example.invalid --name 'Example Owner'
```

This command refuses demo mode, prompts securely for an initial password, validates it and refuses to overwrite an existing account/apartment. There is no public signup that can claim an arbitrary apartment. Operator identity, actual tax/invoice details, contact and production integrations must be configured before genuine service use.

## Booking rules, persistence and time

All create/change operations validate and commit in a database transaction. SQLite `transaction_mode=IMMEDIATE` acquires its writer lock **before** conflict reads; a property row lock is also used for a future PostgreSQL implementation. Competing workers cannot both reserve the same interval. API POST membership checks and mutations share a transaction to avoid a removal race.

- UTC-aware timestamps stored; Europe/Zurich used for display/reporting.
- Naive local date-times are checked by timezone round trips; nonexistent and ambiguous DST times are rejected with explanatory messages. Explicit-offset timestamps are unambiguous.
- Defaults: 30-minute increments, 30-minute minimum, 8-hour maximum, starts within 30 days, start strictly in the future. Configurable on Property.
- Half-open `[start,end)` conflicts checked for charger and vehicle; adjacent slots allowed.
- Offline/unknown, stale real status and incompatible vehicles blocked. An active charge has an **unconfirmed** near-term release bound, not a guarantee that the parking bay will be empty.
- Failed edits preserve originals. Changes/cancellation only before start. Idempotency keys cover create and change; repeating the same request does not duplicate reservations.
- Archived vehicles retain historical records. Current/future reservations and active sessions must be resolved before archiving.
- Parking availability refreshes every 20 seconds while the page is visible; failed refreshes are shown. Charger state, reservation occupancy and unknown physical bay occupancy remain distinct. Cross-household occupancy contains only charger/time/kind/ownership flags, no names, plates or invoice identifiers.

## Billing and reports

Completed sessions belong to reporting periods by **end time in the property timezone**. Non-cancelled reservations are counted by start month. Outstanding and overdue balances include all issued periods, independent of the selected month. Session cost is never added again to invoice totals as spending.

Energy uses 3 decimal places, tariff CHF/kWh uses 4. Ingestion snapshots tariff and vehicle/driver descriptions. Cost is calculated with Python Decimal as `energy_kwh × tariff_chf × 100`, rounded once `ROUND_HALF_UP` to integer CHF cents. Issued invoice line items and totals are snapshots; later tariff or vehicle edits cannot rewrite them. A session belongs to at most one invoice. Invoice due dates are evaluated in the property timezone. Partial payments are outside scope.

Trusted server command for completed calendar months:

```sh
python manage.py issue_invoices 2026-10
# Optional household selector: see `python manage.py issue_invoices --help`.
```

Repeated generation returns existing invoices without duplication. Current-month sessions stay unbilled. **Late sessions arriving after a period's invoice was issued are preserved as unbilled and require an operator adjustment workflow; this version does not silently reopen issued invoices.** No automatic real invoicing or payment-status mutation endpoint is exposed. Historical sample invoice payment states are seeded only.

History CSV exports and print-friendly invoices require the same household authorization as the app. CSV cells are protected against spreadsheet formula injection. Browser Print / Save as PDF produces the invoice document. No production tax treatment is asserted.

## Seed and future integrations

```sh
python manage.py seed_demo
python manage.py seed_demo --date 2026-11-16T14:30:00+01:00
# Destructive to fictional fixtures: explicit operator-only reset, guarded by demo mode.
python manage.py seed_demo --reset
```

Seed uses the seed date, not the old brand-kit's fixed fixture clock. It creates two households, owners/member identities, three vehicles, 20 parking bays, five chargers, future/past/cancelled reservations, active/completed sessions across months and reconciled paid/unpaid/overdue invoices. It is repeatable and refuses to reset mixed/non-demo records. No public reset endpoint exists.

`MockChargingProvider` is demo-only. `ingest_session()` accepts stable provider event IDs, is idempotent, preserves completed event snapshots, and allows a matching active event to finalise. `ingest_mock` is a demo-only server CLI; see `--help`. Future hardware needs authenticated provider webhooks/polling, trustworthy freshness, measured energy, connector status and explicit authorization. Payment and email providers need separate trusted server integrations; no UI simulates a successful payment or actual charger response.

## Brand assets

Guidelines: `../design/brand-kit/01_Guidelines/VoltoShare_Design_Guidelines.pdf`, complete `05_Website/OPENCLAW_IMPLEMENTATION_GUIDE.md`, `design-tokens.json` and `tokens.css`; mandatory skill `../.agents/skills/voltoshare-design/SKILL.md`.

Assets copied into `static/brand/`: `logo-navigation.svg` from `02_Logos/voltoshare-logo-navigation.svg`; `logo-white.svg` from the approved white lockup; `symbol.svg` from the green symbol. These logos remain artwork with original proportions. `fonts/LiberationSans-Regular.ttf` and `LiberationSans-Bold.ttf` are supplied fonts, accompanied by `LICENSE.txt`. `icons/icon-*.svg` are approved kit icons. `tokens.css` changes only local font paths. Mobile icons derive from the supplied symbol; no font or branding substitution. The dashboard avoids decorative photography. Printable invoices use the same logo/font/tokens.

## Tests

```sh
VOLTO_AXES=0 python manage.py test core.tests_domain core.tests_auth
```

Tests use separate test databases, not deployed records. Domain coverage includes a subprocess with a file-backed SQLite database and separate concurrent connections (one successful booking, one conflict), DST, edits/idempotency, invoice/ingestion reconciliation, snapshot preservation and archive restrictions. Auth tests cover household boundaries, exports, print, membership revocation, invitations, role permissions, CSRF, no paid endpoint and production-disabled demo entry. See `../docs/APP_RELEASE.md` for completed browser/release evidence.

## Pi deployment, persistence and backup

- Public origin: `https://app-electromobility.mclement.ch/`, existing Cloudflare route to `127.0.0.1:18820`.
- Unit: `electromobility-app.service`, definition under `../systemd/`.
- Private env: `~/.config/voltoshare/app.env`, mode 0600; private state `~/.local/state/voltoshare/app/` (0700), database `app.sqlite3`.
- Venv: `~/.local/share/voltoshare-venv/`.
- Database persists across refreshes, worker/service restarts and code deployments. Never seed/reset production automatically.

To deploy an updated source checkout, load the private environment without printing it, install pinned requirements, back up the existing DB, run migrations and `collectstatic`, then restart the app service. Check `/health/`, login and authenticated flows afterward. For secure-cookie production settings, local HTTP probes should use `X-Forwarded-Proto: https`; real traffic terminates HTTPS at Cloudflare.

```sh
set -a
. "$HOME/.config/voltoshare/app.env"
set +a
cd /home/mathis/openclaw-workspace/Economics-of-electromobility/tenant-app
/home/mathis/.local/share/voltoshare-venv/bin/pip install -r requirements.txt
/home/mathis/.local/share/voltoshare-venv/bin/python manage.py backup_db --directory "$HOME/.local/state/voltoshare/backups"
/home/mathis/.local/share/voltoshare-venv/bin/python manage.py migrate --noinput
/home/mathis/.local/share/voltoshare-venv/bin/python manage.py collectstatic --noinput
systemctl --user restart electromobility-app.service
```

`voltoshare-backup.timer` runs a daily consistent SQLite online backup at 04:15 host time. Backups remain private outside the repository/web root, mode 0600, with an integrity check. Keep encrypted off-host backups as an operator follow-up; this implementation provides local backups, not a claim of complete disaster recovery. Retention is manual. To restore: stop the service, preserve the current DB, restore a verified backup to the configured DB path, ensure ownership/0600 and restart. Never publish a backup or SQLite file.

Demo cookies are secure and HttpOnly for sessions, CSRF protected with SameSite=Lax; data responses are no-store. The application uses no third-party analytics. Hosting access metadata may still be processed by Cloudflare/the server. Invitation links are bearer secrets and should be shared privately.
