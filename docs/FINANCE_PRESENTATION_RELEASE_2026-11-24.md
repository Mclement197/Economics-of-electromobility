# VoltoShare finance + presentation release — 24 November 2026

## Delivered

- Removed homepage FAQ and closing property-enquiry panel, with simplified header and hero action.
- Added **Finanzen** and **Präsentation** navigation; presentation is embedded immediately above the homepage footer.
- `/finanzen/`: supplied Zurich apartment-subscription and Cham wallbox-compensation models, explicitly separate. All original calculator inputs retained, live SVG cashflow comparison against source baseline, sensitivity, detailed annual tables, capacity checks, per-scenario local persistence and reset.
- `/praesentation/`: 17 VoltoShare slides plus one Cham appendix, overview, keyboard navigation, fullscreen with mobile fallback, notes and source links. On narrow screens slides reflow. Finance slides share saved assumptions with the financial page; static case slides are labelled source baselines.
- Downloadable 18-page PDF and editable 18-slide PPTX. Baseline downloads are snapshots. Browser print route additionally captures current saved finance assumptions. Native PowerPoint visual rendering unavailable on host (Impress absent); package/geometry/font-fit checked, not described as a native-rendered PDF.
- App sidebar and mobile **More** link to the same financial and presentation tools, with explicit separation from household bills. No account, booking, household, invoice, or charging-domain changes.

## Source decisions

Original slides18–51 are unrelated FlexRide/tourism material, so not included in the VoltoShare deck. Originals preserved privately with hashes in `PRESENTATION_CONTENT.md`; student numbers and unused portrait placeholders are not published. The original hidden Roadmap and Charging slides are included.

The supplied Zurich/Cham payer units differ: neither is silently substituted for the other. Charging-chart and text inconsistencies are visibly labelled. Source claims are attributed, not independently revalidated. Source baselines, vacancy adjustment, zero-demand handling and acquisition cash-flow correction are documented in `FINANCIAL_MODEL.md`.

## Verification

- 24 pure financial/calculator tests passed.
- 84 interactive finance/presentation browser checks passed on staging **and public HTTPS**: inputs, calculation/chart updates, rejected negatives, persistence, shared state, all18slides, no desktop clipping, fullscreen/keyboard, reset, zeroEV, 360/768/1440px layout, complete print rendering and real PDF/PPTX downloads.
- 127 existing website browser checks passed on staging, including routes/resources, keyboard mobile navigation, contact non-delivery behavior and 200% zoom.
- Desktop slide screenshots, mobile financial view, and 18-page PDF contact sheet visually inspected; temporary review images removed after review.
- Authenticated app project links verified first on a disposable database, then on the public fictional Sam persona, at desktop and360px through **More**. Only login/session creation; no business-record mutations.
- Public bytes matched 11 deployed HTML/module/CSS/data/download artifacts; source archive/repository paths remain403/404.
- Django system check: no issues. Both website/app services active; app health successful.

## Deployment / rollback

Website deployed with existing script, no tunnel/DNS changes. Rollback tree:
`~/.local/state/voltoshare/releases/website-20261124T100944222023Z`.

App online backup before collectstatic/restart:
`~/.local/state/voltoshare/backups/voltoshare-20261124T100954033454Z.sqlite3`.
Only one app source static file changed; no migrations or seeding. Existing private records retained. Website deployment validator now requires the new pages/modules/downloads before replacement.

## Reproduction

See README plus `scripts/build-presentation.py`, `scripts/build-presentation-pdf.mjs`, `tests/interactive-presentation-browser.mjs`, and `tests/project-links-browser.mjs`. The PPTX builder needs python-pptx; PDF/browser checks use existing Playwright Core and Chromium. These are authoring/test dependencies, not dependencies of the delivered static website.
