# Pi + Cloudflare deployment

## Current public website — 16 November 2026

The public website now serves the branded German project concept and interactive model. Build/deploy commands are in the root README; release checks and unresolved decisions are in `WEBSITE_RELEASE.md`. The tenant app remains an unchanged placeholder. The same existing origins, services and Cloudflare routing below are retained. Source PDFs, design ZIPs and private data are not served.

The following records the original placeholder infrastructure; the website content has since been replaced independently.

| Site | Public URL | Public directory | Local origin | User service |
| --- | --- | --- | --- | --- |
| Website | https://website-electromobility.mclement.ch/ | `sites/website/` | `127.0.0.1:18819` | `electromobility-website.service` |
| Web app | https://app-electromobility.mclement.ch/ | `sites/app/` | `127.0.0.1:18820` | `electromobility-app.service` |

## Runtime

Repository: `/home/mathis/openclaw-workspace/Economics-of-electromobility`.

`scripts/serve.py` uses Python's standard-library threaded HTTP server and binds only to loopback. The selected site folder is the entire public root; repository files and the project proposal are not served. Directory listing is disabled. Placeholder responses are `no-store`, and both pages use `noindex, nofollow` until a real launch.

Service definitions are in `systemd/` and installed under `~/.config/systemd/user/`. Both are enabled to start automatically and restart on failure. Static-file changes are read directly; Python server changes require restarting the corresponding service.

## Cloudflare

Both names use proxied CNAME records pointing at the existing `openclaw-dashboard` tunnel (`afa51286-0a63-4fad-9c7a-49a933aa4647.cfargotunnel.com`). The host's `~/.cloudflared/openclaw-dashboard.yml` contains two exact-host ingress rules for the local origins above; all previous routes remain intact. The catch-all stays HTTP404. The prior configuration was backed up beside that host-only file before editing.

No additional Cloudflare Access policy or application login is added for these empty public placeholders. This does not decide authentication or data-access requirements for the eventual web app. Do not expose credentials, project-private documents or application data in `sites/`.

## Routine checks

```sh
systemctl --user status electromobility-website.service electromobility-app.service
curl -I https://website-electromobility.mclement.ch/
curl -I https://app-electromobility.mclement.ch/
```

Future builds may replace each site's implementation independently while retaining the URLs. Revisit the origin/server configuration when actual app requirements are provided; these placeholders do not imply any charger, billing or authentication implementation.

## Verified release — 16 November 2026

Both public HTTPS pages and all favicon/manifest/PNG assets returned200 and matched the deployed files. Browser rendering passed at320,375,430 and1280px without overflow or script errors; phone screenshots were inspected and deleted. Source PDF and Git paths are not publicly accessible. Both user services are active and enabled. Existing portfolio and German-app health checks still return200 after the tunnel update.
