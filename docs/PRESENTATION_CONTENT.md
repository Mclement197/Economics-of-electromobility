# Source-exact VoltoShare presentation — 27 November 2026 scope revision

Mathis explicitly instructed on 27 November 2026 to **cut the presentation after slide 17** and redesign those first 17 slides. This supersedes the prior requirement to publish all 51 source slides. Within the retained slides, the contract remains **exactly the original content, with cosmetic changes only**. Do not shorten, correct, reinterpret, remove or add their content without a new instruction.

## Authoritative source

Private original: `~/.local/state/voltoshare/source-2026-11-24/Voltoshare_Slides_Final.pptx`.
SHA-256: `1acd77e02c611e7e8bff836a790a47de6334cbbf0c526c7fe9f057bcf0bb7202`.

- Only **original slides 1–17**, in source order, are published in the editable PowerPoint, PDF and browser. Original slides 18–51 (FlexRide/tourism) are excluded from those artifacts, navigation and public artwork directories. The complete 51-slide private source remains untouched.
- The retained source's hidden flags (8, 13) remain in editable PowerPoint. The browser and PDF include these pages so all content can be inspected.
- Original wording, capitalization, typos, team details, student identifiers, placeholders, financial labels, source references, images, native chart data and notes are retained. No editorial corrections are applied—even where the old slides are inconsistent with the project brief.
- Charging chart includes all **three** source series, including the constant 45 kW limit. Original financial charts and their data are retained.
- The extra Cham slide and editorial discussion prompts from the previous output are removed. The separately supplied calculator remains available as a **separate interactive tool**, not inserted into the original deck.

## One visual source

`scripts/build-presentation.py` selects the first 17 original slides and styles their editable objects without replacing their content. Dropped slide relationships are removed before saving. The `presentation_premium_intro.py` and `presentation_premium_story.py` passes apply the current design after the baseline styling. The brand starter remains a visual reference; preserving the original object content takes precedence over importing those objects into a new starter.

`scripts/export-presentation.py` renders the redesigned PPTX through native LibreOffice Impress with `ExportHiddenSlides=true`, producing:

1. The downloadable, selectable-text 17-page PDF.
2. A vector SVG render per page in `website-src/assets/slides/` for the browser player.
3. `presentation-data.json`: exact source text, notes, chart tables and page metadata for the accessible reading mode.

The same render powers PDF and website; the editable PPTX retains original pictures, native text and charts. Browser SVGs are display artifacts, not the PowerPoint source. Fonts and the supplied brand files remain unchanged. A content hash versions artwork URLs. The manifest records `includedSourceSlides: [1, …, 17]`. Export and staging builds remove obsolete slide SVGs; deployment rejects a manifest or artwork directory that still includes the appendix.

## Interaction boundaries

- Keyboard navigation, slide overview and fullscreen operate on all 17 pages.
- Reading mode exposes the original text and chart data at readable phone sizes. The artwork itself remains fixed 16:9 to preserve the composition.
- The **Live-Szenario** is an integrated browser presentation step after original slide 14 (also available from the toolbar), using the existing financial model and browser-local saved assumptions. It does not overwrite source slide values, PDF or PPTX. The financial page and tenant application data are unchanged.
- Original notes remain separate from reading text. No editorial qualifications are inserted into the slide content.

## Build

```sh
# python-pptx and Pillow authoring environment; native Impress + pdftocairo required
python scripts/build-presentation.py
python scripts/export-presentation.py --office /path/to/libreoffice
python tests/presentation-fidelity.py
python3 scripts/build-website.py
BASE_URL=http://127.0.0.1:18929 node tests/interactive-presentation-browser.mjs
```

An isolated local Impress runtime may be used via `LIBREOFFICE`; the export wrapper `scripts/build-presentation-pdf.mjs` accepts `PRESENTATION_PYTHON` and forwards arguments to the Python exporter. There is no browser-CDN or office-runtime dependency in the deployed static site.

The original source is kept private; only the requested redesigned presentation and its display assets are published. The brand archive and unrelated application state are not published or changed.
