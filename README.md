# VoltoShare

A German-language public concept website for shared charging in rental apartment buildings. Built with static HTML, shared brand CSS and small native ES modules; Python 3 builds the pages without frontend dependencies. The separate tenant app is now an interactive, persistent fictional demo; see [tenant-app/README.md](tenant-app/README.md).

- Website: https://website-electromobility.mclement.ch/
- Resident app demo: https://app-electromobility.mclement.ch/
- [Project baseline](docs/PROJECT_BRIEF.md), [original proposal](docs/VoltoShare_Expose_DE.pdf), [current website brief](docs/WEBSITE_IMPLEMENTATION_BRIEF.md)
- [Brand archive and provenance](design/README.md), [mandatory design skill](.agents/skills/voltoshare-design/SKILL.md)
- [Deployment infrastructure](docs/DEPLOYMENT.md), [website release verification](docs/WEBSITE_RELEASE.md), [app release verification and limitations](docs/APP_RELEASE.md)

## Build and preview

From the repository root:

```sh
python3 scripts/build-website.py
python3 -m http.server 18929 --bind 127.0.0.1 --directory build/website
```

Visit `http://127.0.0.1:18929`. Direct routes have generated directory indexes: `/`, `/geschaeftsmodell/`, `/kontakt/`, `/impressum/`, `/datenschutz/`. Requests without trailing slashes redirect normally. HTML contains the content without JavaScript; JS adds menu, calculator and local enquiry validation. No CMS, database, authentication, analytics or external fonts.

Build writes only into the staging output (default `build/website`, ignored by Git), never directly into the live root. Use `--out /absolute/staging/path` to choose another location. The builder mirrors responsive media layouts as container queries to preserve reflow under content zoom. All original kit files remain unchanged.

## Source organisation and configuration

- `website-src/config.json`: canonical URL, language, project status, app URL/status, enquiry mode/destination, downloads, page metadata.
- `website-src/pages/`: German content fragments. The FAQ and closing enquiry panel were removed on 24 November 2026.
- `website-src/site.css`, `site.mjs`: shared presentation and navigation.
- `website-src/calculator.mjs`, `calculator.css`: pure financial helpers plus accessible UI.
- `website-src/contact.mjs`, `contact.css`: local-only demo enquiry.
- `website-src/finance-model.mjs`, `finance-ui.mjs`, `finance.css`: shared Zurich and Cham scenarios, local browser persistence, live charts.
- `website-src/presentation-data.json`, `presentation.mjs`, `presentation.css`: 17-slide source-exact presentation, keyboard/fullscreen controls, accessible reading mode and integrated live financial scenarios.
- `website-src/downloads/`: approved baseline PDF and editable PPTX; build/source details in `docs/PRESENTATION_CONTENT.md`.
- `website-src/assets/`: only the public assets needed by this site.
- `sites/website/`: generated deployed files, tracked for review; **do not hand-edit**.
- `sites/app/`: retained original placeholder for rollback; the app service now runs `tenant-app/`.

Only German is implemented; no incomplete English switch. Only `contactMode: "demo"`, `contactDestination: null`, and `appStatus: "placeholder"` or `"demo"` are supported. The build rejects other modes to prevent accidental misrepresentation. Enabling real enquiries requires an explicitly configured receiving operator/backend, server validation and abuse protection, privacy updates, and delivery tests—not merely flipping a setting. No environment secrets or `.env` are needed. The approved draft presentation is downloadable as PDF and editable PowerPoint; only generated public deliverables are exposed, not the original source deck or archive.

The visible app link is **App-Demo**, pointing to the working, explicitly fictional resident demonstration. The landing-page interface is a clearly marked, noninteractive conceptual preview with fictional building/booking information. The app uses a labelled flat sample tariff as a first-version simplification of the proposal’s dynamic tariff plus provider markup.

## Assets and brand sources

Read `design/brand-kit/01_Guidelines/VoltoShare_Design_Guidelines.pdf`, `05_Website/OPENCLAW_IMPLEMENTATION_GUIDE.md`, `design-tokens.json` and `tokens.css`. The newer website brief determines website-only features and German routes.

| Supplied source under `design/brand-kit/` | Website asset |
| --- | --- |
| `02_Logos/voltoshare-logo-navigation.svg` | `website-src/assets/logo-navigation.svg` |
| `02_Logos/voltoshare-logo-white.svg` | `website-src/assets/logo-white.svg` |
| `02_Logos/voltoshare-symbol-green.svg` | `website-src/assets/symbol.svg`, deployed `favicon.svg` |
| `02_Logos/voltoshare-symbol-green.png` | Source for padded apple-touch/192/512 icons |
| `02_Logos/voltoshare-logo-primary.png` | Centred unmodified logo on warm-white `assets/social.png` |
| `03_Images/voltoshare-charger-garage.jpg` | `assets/garage.webp`, 1400 × 781 optimised concept visual |
| `03_Images/icons/*.svg` | `assets/icons/*.svg` |
| `04_Fonts/LiberationSans-Regular.ttf`, `LiberationSans-Bold.ttf` | `assets/fonts/`, self-hosted with original `LICENSE.txt` |
| `05_Website/tokens.css` | `assets/tokens.css`, only font URLs adapted |

No font is missing. Original logo proportions/colours are preserved; no redrawn wordmark or stock imagery. Concept photography is explicitly not a customer installation. Prepared asset files are checked in, so ordinary builds require only Python's standard library. Original images were resized with Pillow, originals preserved. Font licence accompanies the distributed fonts.

## Focused verification

```sh
node --test website-src/calculator.test.mjs
BASE_URL=http://127.0.0.1:18929 node tests/website-browser.mjs
```

Browser checks use the Pi's existing Playwright Core and Chromium. To run elsewhere, provide `PLAYWRIGHT_MODULE=/path/to/playwright-core` and `CHROMIUM_PATH=/path/to/chromium`; no browser dependency is added to the website. `SCREENSHOTS=1` writes temporary review images under `/tmp/volto-*`; inspect and remove them afterward.

## Deploy on the existing Pi

After building and passing checks:

```sh
python3 scripts/deploy-website.py build/website
BASE_URL=https://website-electromobility.mclement.ch node tests/website-browser.mjs
systemctl --user is-active electromobility-website.service electromobility-app.service
```

The deploy script stages and replaces **only** `sites/website`, preserves a dated rollback directory under `~/.local/state/voltoshare/releases/`, and restores the previous root if the replacement rename fails. Existing `scripts/serve.py` reads static files directly; no restart, tunnel, DNS, credentials or app changes are necessary. The replacement is two local directory renames; an in-flight request in that very short interval may need a retry. For rollback, copy the printed backup to a new staging directory and replace `sites/website` with that tree, retaining the failed release outside the public root. The initial blank placeholder backup has no subpages, so restore it directly rather than through the full-release validator.

Public preview remains `noindex, nofollow`. This is not a commercial launch. Operator identity/contact details and commercial terms still need confirmation before real enquiries or operations.

## Financial scenarios and presentation — 24 November 2026

`/finanzen/` offers the supplied Zürich per-apartment case and separate Cham per-wallbox alternative. All source calculator controls are retained; scenario edits stay in this browser and do not affect app invoices. `/praesentation/` and the homepage's final section use one HTML slide player. The resident app links to these project tools under More and in the sidebar.

At Mathis’s explicit 27 November request, the redesigned deck now ends after original slide 17. These 17 VoltoShare slides retain their original content; the later FlexRide/tourism appendix is excluded from the PPTX, PDF and browser. The complete private original remains untouched. Original slide values are never replaced by scenarios. Fullscreen supports arrows/Home/End and Escape, with a viewport fallback. Mobile reading mode exposes original text and chart tables; an integrated Live-Szenario after original slide 14 provides live assumptions without altering source slide content (also accessible anytime from the toolbar). PDF and browser artwork share a native Impress render of the editable PowerPoint. The player uses 2560px PNG derivatives to avoid Chromium SVG glyph-paint instability; vector PDF and editable PowerPoint remain available.

```sh
node --test website-src/calculator.test.mjs website-src/finance-model.test.mjs
python3 scripts/build-website.py
# With staging preview running on port18929:
node scripts/build-presentation-pdf.mjs
python3 scripts/build-website.py
node tests/interactive-presentation-browser.mjs
node tests/website-browser.mjs
```

See `docs/FINANCIAL_MODEL.md` for model corrections and limitations. PPTX text/tables/charts remain editable. The revised deck is rendered through an isolated native Impress runtime for PDF and browser artwork; Microsoft PowerPoint itself is not available on this host. See `docs/PRESENTATION_CONTENT.md` for the source-exact contract and export procedure.

## Presentation viewport update — 27 November 2026

Fullscreen now gives the entire viewport to the slide, preserving its 16:9
aspect ratio without reserving a header or footer. Floating controls appear at
the screen edges (or on Tab/touch) and hide after inactivity. Arrow keys still
navigate, F opens the interactive scenario, and Escape returns/exits. Browsers
without the Fullscreen API use the same viewport-filling layout.

The live finance step is a bounded presentation layout, not an embedded page:
four editable levers sit beside the cashflow chart and three headline metrics.
“Weitere Annahmen” and “Rechenweg & Daten” replace the main content pane instead
of extending the slide. On narrow screens only that pane scrolls. Presets,
reset, validation and shared scenario state remain available; the standalone
finance page and the original PDF/PPTX/artwork are unchanged.

Focused viewport/interaction regression (native and fallback fullscreen,
1280×720, 1440×900, 1920×1080, 768×1024 and 360×800):

```sh
node tests/presentation-viewport-browser.mjs
```

Set `SCREENSHOTS=1` for temporary `/tmp/volto-viewport-*` review images; inspect
and remove them after checking. Controls in the live view float at the bottom
so they cannot cover the return button or form header.
