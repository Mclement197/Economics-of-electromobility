# Pi + Cloudflare deployment

## Current public website — 16 November 2026

The public website serves the branded German project concept and interactive model. Build/deploy commands are in the root README; website release checks and unresolved decisions are in `WEBSITE_RELEASE.md`. The tenant app is a persistent, explicitly fictional Django demonstration; its instructions and release evidence are in `../tenant-app/README.md` and `APP_RELEASE.md`. Existing origins and Cloudflare routing are retained. Source PDFs, design ZIPs and private data are not served.

Both originally blank placeholders have been replaced independently:

| Site | Public URL | Public directory | Local origin | User service |
| --- | --- | --- | --- | --- |
| Website | https://website-electromobility.mclement.ch/ | `sites/website/` | `127.0.0.1:18819` | `electromobility-website.service` |
| Web app | https://app-electromobility.mclement.ch/ | Django `tenant-app/` (not a public directory) | `127.0.0.1:18820` | `electromobility-app.service` |

## Runtime

Repository: `/home/mathis/openclaw-workspace/Economics-of-electromobility`.

The website's `scripts/serve.py` uses Python's standard-library threaded HTTP server and binds only to loopback. `sites/website/` is its entire public root; repository files and the project proposal are not served. Directory listing is disabled. The app runs Django through two Gunicorn workers with WhiteNoise for collected public assets; authenticated data responses are private/no-store. Both surfaces are presentation previews, not a commercial launch.

Service definitions are in `systemd/` and installed under `~/.config/systemd/user/`. Both are enabled to start automatically and restart on failure. Website static-file changes are read directly. App changes require the migration/collectstatic/restart procedure in its README. Private app state is outside the repository; the daily backup timer is also defined in `systemd/`.

## Cloudflare

Both names use proxied CNAME records pointing at the existing `openclaw-dashboard` tunnel (`afa51286-0a63-4fad-9c7a-49a933aa4647.cfargotunnel.com`). The host's `~/.cloudflared/openclaw-dashboard.yml` contains two exact-host ingress rules for the local origins above; all previous routes remain intact. The catch-all stays HTTP404. The prior configuration was backed up beside that host-only file before editing.

No Cloudflare Access policy is required for the public concept/demo. The app itself requires Django authentication for household records and mutations. Its opt-in fictional demo personas are not a production authentication policy. Do not expose credentials, project-private documents or application data in `sites/`.

## Routine checks

```sh
systemctl --user status electromobility-website.service electromobility-app.service
curl -I https://website-electromobility.mclement.ch/
curl -I https://app-electromobility.mclement.ch/
```

Each surface may be updated independently while retaining its URL. No real charging hardware, payment service or enquiry-delivery integration is enabled.

## Historical placeholder verification — 16 November 2026

Both public HTTPS pages and all favicon/manifest/PNG assets returned200 and matched the deployed files. Browser rendering passed at320,375,430 and1280px without overflow or script errors; phone screenshots were inspected and deleted. Source PDF and Git paths are not publicly accessible. Both user services are active and enabled. Existing portfolio and German-app health checks still return200 after the tunnel update.


## Tenant app replaced placeholder — 16 November 2026

The same app hostname and loopback port 18820 now serve Django/Gunicorn from `tenant-app/`, not `sites/app/`. The latter is retained only as a rollback artifact. The app unit changed; Cloudflare routing did not. Private SQLite state and environment live outside the repo. See `tenant-app/README.md` and `APP_RELEASE.md`. The public website links to the demo and discloses its flat-tariff simplification.
