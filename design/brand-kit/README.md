# VoltoShare brand and implementation kit

Version 2.0 · 16 November 2026

This kit supports the VoltoShare website, resident demonstration and graded presentation. The supplied proposal is the factual basis. The supplied artwork defines the visual identity.

## Start here

- **AI / OpenClaw:** Read `05_Website/OPENCLAW_IMPLEMENTATION_GUIDE.md` in full before implementation. Use `05_Website/design-tokens.json`, `tokens.css` and `demo-data.json` as structured inputs.
- **Human design review:** Open `01_Guidelines/VoltoShare_Design_Guidelines.pdf`.
- **Local website reference:** Extract the entire ZIP, then open `05_Website/index.html`. No server or CDN is required. Keep the folder structure intact.
- **Presentation editing:** Install the fonts in `04_Fonts`, then open `06_Presentation/VoltoShare_Presentation_Starter.pptx`.

## Contents

| Folder | Purpose |
| --- | --- |
| `01_Guidelines` | 18-page visual PDF and reproducible PDF source |
| `02_Logos` | Seven cleaned SVG logo variants and seven transparent PNG exports |
| `03_Images` | Supplied garage, NFC-card and app-icon concept imagery; eight original line icons in SVG and PNG |
| `04_Fonts` | Liberation Sans regular, bold, italic and bold italic; licence notices |
| `05_Website` | Complete Markdown specification, matching HTML guide, interactive local demo, CSS and JSON |
| `06_Presentation` | Six-slide editable PPTX, PDF preview, six slide PNGs and authoring source |
| `07_References` | Original supplied artwork and proposal |

`ASSET_MANIFEST.json` records the file types, dimensions, roles and provenance. It helps an AI select the correct assets without guessing.

## Identity rules

- Forest green `#28563B`, ink `#1E2023`, graphite `#23262B`, warm white `#F8F5F0`, white `#FFFFFF`, soft green `#EAF0EB`.
- Use the supplied logo files. Do not retype the wordmark. Use the all-white logo on graphite or green.
- Preserve the aspect ratio. Clear space is at least one quarter of the symbol height.
- Recommended minimum digital widths: full lockup 320 px; navigation logo 200 px; standalone symbol 24 px, preferably 32 px.
- Use Liberation Sans for editable text. The original editable font cannot be identified conclusively from the raster references. The bundled font is a close Arial-compatible companion, not a claim of exact font identification.
- The SVGs are cleaned vector reconstructions traced from the supplied raster artwork. They contain native paths, with no retyped lettering or embedded raster image. They are not the original editable brand masters.

## Evidence and demonstration boundaries

The proposal describes a landlord/property-manager subscription per billable apartment, plus resident payments for metered electricity at a dynamic rate with a provider markup. The 20 apartments / 5 chargers / 20 subscriptions example assumes full occupancy. Vacancy billing, real prices and costs remain open.

The website demonstration uses a fixed clock, fictional Lindenhof building and fictional account records. It does not authenticate real residents, operate chargers, provision NFC access, send invitations or collect payments. Pending invitations are local demo records. Its default totals are 8 completed sessions, 112.0 kWh, CHF 35.84 unbilled November usage, 10 November bookings and CHF 28.40 outstanding from October.

The garage, NFC-card and app-icon pictures are supplied concept imagery. They are not evidence of deployed infrastructure or a real customer installation. No new third-party stock imagery was added. Rights and attribution for supplied material follow the source material; this kit does not grant additional third-party rights.

## What has been checked

- All 18 guideline pages were rendered and visually reviewed. The font is embedded and page text remains selectable.
- All seven logo SVGs use native paths. All seven logo PNGs have alpha transparency. The supplied logo appearance was checked at large and normal usage sizes.
- The six-slide starter was rendered and visually inspected. Text and numerical content are editable; slides 3 and 5 contain native PowerPoint tables. The PPTX passed package and geometry checks. The accompanying presentation PDF is an image-based visual preview.
- Website script syntax, relative asset links, JSON consistency and core booking/account flows were checked. A local DOM harness verified route rendering and numerical logic. A full browser rendering and accessibility audit was not available in this environment, so the implementation guide retains explicit browser acceptance checks.
- The ZIP inventory and archive integrity were checked before delivery.

## Sources

- `07_References/VoltoShare_Expose_DE(1).pdf`, page 1, 15 October 2026.
- Eight supplied artwork files preserved in `07_References`.
- User requirements for the public business-model website, resident app, design PDF and AI asset package.
- Liberation Fonts: <https://github.com/liberationfonts/liberation-fonts>.
- W3C WCAG 2.2: <https://www.w3.org/TR/WCAG22/>.
- Layouts, interface design, line icons, templates and demo fixtures are original work for this kit.

Use the proposal for factual claims, the guidelines for visual decisions, and the Markdown specification for implementation behaviour.
