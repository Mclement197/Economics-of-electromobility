# Financial lab and live presentation — 25 November 2026

## User request

Improve the financial fields and overall visual design; allow assumptions to be changed during the presentation with a graph updating immediately. This supersedes the old interaction that hid the financial lab below the slides, but does not authorize changing the original slide text or numbers.

## Presentation interaction

- The browser player now includes an explicitly labelled **Live-Szenario** step immediately after original slide 14 (the VoltoShare calculation). Next enters this step, then continues with original slide 15. Previous from slide 15 returns through the live step.
- A persistent toolbar button and keyboard shortcut **F** open the live view from any slide. Finance slides 12–15 also show a contextual invitation to experiment.
- The live view occupies the presentation itself, including fullscreen. It is not a separate tab or modal. Arrows in editable fields/sliders remain field controls; arrow/Page navigation elsewhere controls the presentation.
- Escape or “Zurück zur Originalfolie” restores the source slide. Fullscreen remains available while changing assumptions. The original slide images, wording, chart data and speaker notes remain intact.
- `/praesentation/?live=1` opens directly on the live step associated with original slide 14. The same player appears on the homepage.
- PDF/PPTX downloads and print output retain all 51 original slides and are unchanged static artifacts. Live computation is a browser feature, not an embedded PowerPoint function.

## Financial interface

The shared component keeps the existing deterministic calculation engine, per-preset browser-local storage and synchronization contract. Zürich's per-apartment subscription and Cham's per-wallbox compensation remain distinct models. No financial formulas, default assumptions or resident accounting records are changed.

Four principal levers use sliders alongside precise number fields and explicit units. Other assumptions remain available through progressive disclosure. The chart compares current cumulative cashflow against the unchanged baseline over the same time horizon; summaries distinguish cash surplus, investment and simple payback. These remain scenario assumptions, not guaranteed forecasts.

## Verification

Verification and deployment results are recorded below. Browser checks cover both models, valid/invalid edits, slider-number synchronization, reset, persistence, live-step navigation, fullscreen, input keyboard behavior, all original slides, mobile widths and projection-sized layout.

### Reproducible checks

```sh
node --test website-src/finance-model.test.mjs
python scripts/build-website.py
# Serve build/website on loopback 18929, then:
node tests/interactive-presentation-browser.mjs
node tests/finance-live-browser.mjs
node tests/website-browser.mjs
```

The focused live-finance suite checks the actual SVG curve coordinates (not only labels), both model baselines, invalid/blank input retention, preset persistence, source-artwork identity, keyboard controls, and the projector-visible bounds. The original-slide suite checks all 51 source slides, reading-mode content and actual downloads. Temporary review screenshots are removed after inspection.


### Results

- 17 financial-engine unit tests passed; no changes to `finance-model.mjs` or its baseline values.
- 393 source-exact presentation/finance browser checks passed across all 51 original slides, text/chart access and downloads.
- 74 focused redesign/live-presentation checks passed on the final staged build, including the selected Cham model and saved assumptions transferring into the live view.
- 130 broader website checks passed, including other routes and 200% zoom regression.
- Final 360/768/1440 layouts visually reviewed; at 1280×720 fullscreen all four main controls, graph and complete KPI row fit without scrolling. Secondary assumptions and detailed calculations remain scrollable below.
- Visual review caught clipped projector results and small mobile graph labels; both were adjusted and rechecked. Browser tests caught reentrant change events during preset switching; shell-rebuild guards prevent stale-field events from being applied to the new model.
- Website-only deployment completed; rollback: `~/.local/state/voltoshare/releases/website-20261125T224308455707Z`. No app, database, service, DNS or tunnel changes. Source/public files match.
- The original manifest, slide artwork and PDF/PPTX binaries are unchanged. Temporary review screenshots were inspected and removed.

- All 74 focused browser checks also passed against the deployed HTTPS website, including live edits, model transfer and fullscreen navigation.
