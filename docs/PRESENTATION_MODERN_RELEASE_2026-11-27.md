# Modern presentation design — 27 November 2026

## Request and content contract

Mathis requested a more modern, substantially improved slide design without changing content, and requested the profile photos from `linkedin.com/in/mathis-clement/` and `linkedin.com/in/joelfrei/` for the team page.

The authoritative original remains `~/.local/state/voltoshare/source-2026-11-24/Voltoshare_Slides_Final.pptx`, SHA-256 `1acd77e02c611e7e8bff836a790a47de6334cbbf0c526c7fe9f057bcf0bb7202`. It is untouched. All 51 source slides, their order, hidden flags, exact wording/paragraphs, notes, source media and native chart/table data remain the content master. No financial corrections or editorial summaries are introduced.

The design refinement operates on editable native source objects after the baseline layout pass:

- `scripts/presentation_modern_main.py` — VoltoShare slides 1–17.
- `scripts/presentation_modern_appendix.py` — retained original slides 18–51.
- `scripts/build-presentation.py` — integrates both passes and preserves original content.
- `scripts/export-presentation.py` — a single native Impress export supplies PDF and matching browser SVG artwork.

The Nov 25 integrated live financial step, controls, formulas and local scenario persistence are outside this cosmetic redesign and remain available. Static downloads do not contain live calculations.

## LinkedIn portrait status

Both exact public profile URLs returned LinkedIn HTTP 999 security/login responses without profile image metadata. Public search did not establish a verifiable matching portrait. No challenge or login restriction was bypassed, and no substitute or AI-generated portrait was used. Mathis was asked to attach the two photos while design work continued. The original team image/placeholder content remains unless subsequently supplied portraits are explicitly recorded here.

## Reproduction

Authoring uses Python with `python-pptx` and Pillow; the local existing environment is `/tmp/volto-redesign-venv/bin/python`. Rendering uses the locally extracted native LibreOffice Impress 25.2.3.2, not Microsoft PowerPoint:

```sh
export LD_LIBRARY_PATH=/tmp/volto-lo/root/usr/lib/aarch64-linux-gnu:/tmp/volto-lo/root/usr/lib/libreoffice/program
/tmp/volto-redesign-venv/bin/python scripts/build-presentation.py
python tests/presentation-fidelity.py --skip-browser
/tmp/volto-redesign-venv/bin/python scripts/export-presentation.py --office /tmp/volto-lo/root/usr/lib/libreoffice/program/soffice
python tests/presentation-fidelity.py
python scripts/build-website.py
```

Source emoji on one appendix slide require the monochrome **Noto Emoji** font in the rendering environment. Font and OFL license are installed locally under `~/.local/share/fonts/voltoshare-render/`, obtained from the Google Fonts `ofl/notoemoji` directory. The original emoji characters remain unchanged. Liberation Sans continues to be the main brand typeface. Renderer dependencies are not exposed as website code or installed into the tenant app.

## Verification and release

The independent first-pass native review covered all 51 pages and enlarged crowded diagrams/references. Final fixes clear diagram subtitles on 9/12, add process spacing on 13, remove stray connectors on 34, align icons on 37, clear the brochure subtitle on 43, reserve footer space on 47 and remove the inherited red outline on 50.

A native Impress rendering defect on slide 14 mirrored negative cash-flow bars above zero when `c:invertIfNegative` was enabled. Turning off that colour-style flag fixes the rendering without changing any cached values or embedded workbook data. A native single-slide proof and the unchanged-data audit established the fix before integration.

Final verification/deployment results follow below.


- Native output: LibreOffice Impress 25.2.3.2, all 51 pages including original hidden slides. Not a Microsoft PowerPoint rendering verification.
- Independent source-content audit: 460 checks before derivatives; 769 checks including exact browser transcript/revision. No source wording, paragraph, note, image occurrence, chart value, table or hidden flag differences.
- Browser regression on local staging: 393 presentation/finance checks and 74 focused financial/live-scenario checks passed. The only subsequent change is cosmetic spacing in the appendix slide 47 Costs column; final regenerated source/artwork checks are repeated.
- Main slides use larger typography, a photo-led cover, open agenda/team layouts, stronger market and finance figures and cleaner native diagrams/charts. Appendix styles remain consistent without dropping its original material.

## Published release

- Final targeted native visual review passed on slides 9, 12–14, 34, 37, 43, 47 and 50 after the full 51-page review. The last Costs-column overlap on 47 was removed using spacing/font changes only.
- Final regenerated deck/PDF/browser source audit: **769 checks passed**. Revision `8df176230642`, 51 native PDF pages and 51 SVG pages.
- Deployed website only on 27 November 2026. Rollback: `~/.local/state/voltoshare/releases/website-20261127T090357452238Z`. No app, account, service, DNS or tunnel changes.
- Public browser: **74 live financial/presentation checks passed** at `https://website-electromobility.mclement.ch`.
- Public manifest, PPTX, PDF, cover and last-corrected slide 47 artwork matched local SHA-256 hashes. Python urllib received HTTP403; normal curl fetched the public assets successfully. No authentication or challenge bypass was used.
- Temporary review PNG/JPEG files removed after inspection. Original source, brand-kit previews and final deliverables retained.
- **Outstanding:** Mathis and Joel portraits, pending the requested photo uploads. Existing exact-source placeholders remain; no guessed substitute images were added.

Published artifact hashes:
- `presentation-data.json`: `a110f5fd9b06f37e9a278bd9791905bd9cbe1cba90210f0a6215c3ccec9840b9`
- `downloads/VoltoShare-Praesentation.pptx`: `8df176230642f874ef1106ed84ea18689a401a84721739d2d543ca8d1caf6744`
- `downloads/VoltoShare-Praesentation.pdf`: `3e3c1afa131555187624ae05c4007bf3c6570b71af4404ebd3fd96b8f847a2d9`
- `assets/slides/slide-01.svg`: `61830aa906664f41ea0f378ee26cbc9cfdf54f6ad935f7bd1dcb37c6957521cd`
- `assets/slides/slide-47.svg`: `11d8b0b33533178a848de160615c251d7e20bb35abba5647701320cdd83352ac`
