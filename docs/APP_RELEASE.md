# Tenant app release — 16 November 2026

## Deployed result

- App: https://app-electromobility.mclement.ch/ — choose **Explore as Alex**.
- Website: https://website-electromobility.mclement.ch/ — its App-Demo links now open the working app.
- Source and exact run/build/test/deploy commands: [tenant-app README](../tenant-app/README.md).
- Latest functionality authority: [app implementation brief](APP_IMPLEMENTATION_BRIEF.md); API documentation: [contract](APP_API_CONTRACT.md).

The app uses the supplied logo artwork, Liberation Sans fonts, forest/warm-white tokens and approved icons. It has five responsive sections: dashboard, parking/reservations, charging history, household/vehicles and billing. All figures derive from persisted records. Reservations, metered/simulated sessions and invoices remain separate.

Implemented journeys include vehicle creation/editing/archiving; selectable parking map and accessible list; booking review, creation, changes and confirmed cancellation; expiring email-bound household invitations; owner-only member removal; filtered history/CSV; invoice details and print/Save as PDF. Availability refreshes every 20 seconds while parking is visible. Empty, error and validation states are included. Reduced motion, keyboard focus, dialog trapping and mobile navigation are supported.

## Verification evidence

Completed against the release source and deployed service:

| Check | Result |
| --- | --- |
| Django domain and authorization suite | **24 tests passed**: 10 domain, 14 authorization |
| Concurrent file-backed SQLite booking attempts | Exactly one success; the competing request returns conflict |
| Booking/accounting rules | Adjacent intervals, vehicle overlaps, DST rejection, failed-edit preservation, idempotency, invoice/session reconciliation and immutable snapshots covered |
| Household privacy | Foreign private records/exports/print and unauthorized mutations denied; membership revocation and invitation restrictions covered |
| Desktop/tablet/mobile layout | Five sections at 360, 768 and 1440 pixels; no horizontal overflow, broken assets, failed fonts or console errors |
| Mobile end-to-end journeys | Vehicle add/edit/archive; booking create/change/cancel; invitation create/copy/revoke; history filters; session and invoice dialogs; printable invoice passed |
| Keyboard and reflow | Charger selection, list controls, dialog focus trap/Escape return, skip link and 200% content zoom passed across five sections |
| Public app smoke | **55 checks passed including service restart**; authenticated session and household/vehicles/bookings/sessions/invoices fingerprint survived unchanged |
| Final public app smoke after final styling | **51 checks passed** (same suite without the four optional restart checks) |
| Website after connecting the app | **104 browser checks passed**, both staged and public |
| Database backup | Consistent SQLite online backup completed with integrity check; daily timer enabled |

The public app smoke is reproducible with `node tests/app-public-smoke.mjs` from the repository root. `RESTART=1` adds an actual restart of `electromobility-app.service` and persistence comparison; use it only from the authorized Pi operator context. `BASE_URL`, `PLAYWRIGHT_MODULE` and `CHROMIUM_PATH` are configurable. The browser uses fictional demo identities and does not create bookings or change accounting records. Mutation journeys were exercised on a separate local preview database, not the public seed.

Review screenshots were visually inspected and removed. No screenshot contains real customer data; the release includes only fictional seed records.

## Deployment and recovery

- Existing Cloudflare hostname still targets loopback `127.0.0.1:18820`; no tunnel/DNS changes were needed.
- `electromobility-app.service` now runs Django/Gunicorn from `tenant-app/`. The original `sites/app/` placeholder is retained but is not served.
- Private environment: `~/.config/voltoshare/app.env`, mode 0600; its signing secret was generated locally, not committed.
- Persistent database: `~/.local/state/voltoshare/app/app.sqlite3`, outside the repository and public roots.
- Consistent local backups: `~/.local/state/voltoshare/backups/`; `voltoshare-backup.timer` runs at 04:15 host time. Retention is manual. Off-host encrypted backup remains an operator follow-up.
- Previous app unit: `~/.local/state/voltoshare/releases/app-before-django.service`. Restoring it serves the original blank placeholder; preserve the database separately.
- Website rollback before the app-link update: `~/.local/state/voltoshare/releases/website-20261116T154642949537Z`.

Both application services and the backup timer were active at verification. Secure/HttpOnly session cookies, CSRF, authenticated household scoping and no-store data responses were checked. This is focused release verification, not a claim of an independent security audit.

## Explicit demo boundary and remaining decisions

The deployed app is intentionally a **public, fictional, persistent demonstration**. People choosing the same demo persona share that persona's records. The UI asks visitors to enter fictional information. Demo mode defaults off in source and is explicitly enabled for this deployment. Real onboarding requires a separate database, disabled demo entry, trusted owner provisioning and confirmed operating details.

- No real charger/NFC operation, electricity meter connection, payment processing or email sending. Invitations are copyable links, not claimed emails.
- Flat CHF sample tariff is a labelled app simplification. The website still correctly describes the proposed dynamic tariff plus provider markup and landlord per-apartment subscription.
- Website enquiries remain local-only demo interactions; no message is sent or stored.
- Vacancy billing, commercial subscription/markup amounts, verified operator/contact details and production tax treatment remain unresolved.
- Issued invoices are immutable. Sessions arriving after a month's invoice was issued remain unbilled for an operator adjustment workflow; this version does not reopen invoices automatically.
- Before real service use, configure hardware freshness/meter integration, trusted payment events, genuine household identities and approved operator/privacy information. No real customer data or credentials are included in the repository.
