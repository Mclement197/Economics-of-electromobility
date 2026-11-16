---
name: voltoshare-design
description: Design or review VoltoShare websites, web-app screens, slides, documents, diagrams and branded assets using the supplied brand kit. Apply to visual and branded-content work for the Economics-of-electromobility project, not unrelated brands.
---

# VoltoShare design

Use the supplied VoltoShare kit as the design baseline, not a newly invented visual identity. This skill supports the user's requested artifact; it does not turn saving guidelines or editing one screen into permission to build or deploy the entire demo. Follow later explicit user decisions and record any intentional departure from the baseline.

## Locate the canonical sources

Paths below are relative to this skill directory; `../../..` is the repository root. Read the kit's [README](../../../design/brand-kit/README.md), the relevant visual guidance in the [18-page design PDF](../../../design/brand-kit/01_Guidelines/VoltoShare_Design_Guidelines.pdf), and the [project brief](../../../docs/PROJECT_BRIEF.md) before design work. If PDF extraction is insufficient, inspect the relevant rendered pages rather than guessing.

Choose the additional sources that match the deliverable:

- **Website or app:** read the complete [implementation guide](../../../design/brand-kit/05_Website/OPENCLAW_IMPLEMENTATION_GUIDE.md) before implementation. Load [design-tokens.json](../../../design/brand-kit/05_Website/design-tokens.json) and [tokens.css](../../../design/brand-kit/05_Website/tokens.css); inspect the [interactive reference](../../../design/brand-kit/05_Website/index.html) for layout/interaction intent. It is a reference, not an already deployed product or permission to publish it. Its local hash routes must be adapted to the actual requested host/routing architecture.
- **Slides/presentations:** read the [presentation README](../../../design/brand-kit/06_Presentation/README.txt) and use the [editable PPTX starter](../../../design/brand-kit/06_Presentation/VoltoShare_Presentation_Starter.pptx). Its PDF is a visual preview, not the editable source.
- **Logos, images, icons or other documents:** consult the [asset manifest](../../../design/brand-kit/ASSET_MANIFEST.json), [logo README](../../../design/brand-kit/02_Logos/README.txt) and [font README](../../../design/brand-kit/04_Fonts/README.txt). Select supplied assets rather than recreating them.
- **Functional demos, costs or status displays:** use [demo-data.json](../../../design/brand-kit/05_Website/demo-data.json) and implementation-guide sections 5–9. Keep fixtures, assumptions and real integrations distinguishable.

The proposal is the factual baseline; the PDF supplies visual guidance; the implementation guide and structured tokens supply precise digital choices. Broad PDF type ranges and exact web token sizes serve different uses—use the web tokens for web implementation. Supplied demo requirements and imagery are not evidence of commercial operations. Use only the relevant features within the current request.

## Identity and visual decisions

- Calm, practical, dependable building service; generous whitespace and useful diagrams/numerical summaries. Avoid decorative lightning, emojis, stock greenery, glossy car imagery, gradients and excessive card shadows.
- Palette: forest green `#28563B` for brand/primary action; ink `#1E2023` for text; graphite `#23262B` for dark surfaces; warm white `#F8F5F0` for canvas; white `#FFFFFF` for surfaces; soft green `#EAF0EB` for supporting emphasis. Use the complete token file for semantic status colours, borders and hover states, not approximate replacements.
- Use supplied SVG/PNG logos. Preserve aspect ratio, letterforms and clear space of at least one quarter of the symbol height. Never retype, stretch or redraw the wordmark. Primary lockup belongs on light surfaces; the all-white version belongs on dark surfaces. Do not place forest green on graphite or on busy photography.
- Recommended digital minimums: full lockup 320px, navigation lockup 200px, symbol 24px (32px preferred). Use the navigation logo or standalone symbol when space is tight; do not squeeze the full tagline lockup. The supplied vectors are cleaned reconstructions, not original editable brand masters.
- Use bundled Liberation Sans regular/bold for editable text, with Arial/Helvetica/sans-serif fallbacks on the web. Preserve the supplied italic faces where needed. Retain the [font licence](../../../design/brand-kit/04_Fonts/LICENSE.txt) when distributing fonts. Liberation Sans is a companion font; the original logo font is unknown. Use tabular numerals for monetary/energy tables.
- Spacing: 4/8/12/16/24/32/48/64/96px. Radii: control 8, card 12, feature 20, badge 999px. Public content max 1200px, app max 1280px; gutters 16/24/32px; breakpoints 640/1024/1280px. Read exact size/line-height pairs from tokens. Controls 48px high, interactive targets at least 44×44px; visible 2px blue focus ring with 2px offset. Verify contrast against the actual surrounding surface; use contrasting separation or a two-tone treatment where the blue alone is insufficient on dark backgrounds.
- Use the supplied 2px-stroke icons consistently at 20 or 24px. Prefer existing garage/NFC/app concept visuals; preserve aspect ratio and the charger/cable when cropping. Label concept imagery appropriately; never describe it as a real customer installation.
- Slides: 16:9, one argument per slide, content titles 32–44pt and body 18–24pt; display titles may be larger and table labels/source notes smaller where still readable. Keep editable text/tables in the PPTX and sources/assumptions close to claims. Use the starter and its notes rather than flattening the whole presentation to images.

## Product and evidence constraints that affect design

- Subscription payer: landlord/property manager; unit: **billable apartment**, never charger. Resident payment: metered electricity at dynamic tariff plus markup. Keep these two flows visually separate.
- The 20 apartments/5 chargers/20 subscriptions configuration is an illustrative full-occupancy example, not a deployed site, proven sizing ratio or traction metric. Vacancy billing remains unresolved: continuing versus pausing subscriptions shifts the risk. Show the alternatives when relevant; do not silently choose one in charts/calculators/copy.
- Do not invent prices, ROI, guaranteed savings/rent gains, customer proof, CO₂ figures, V2G features or operating integrations. Revenue/energy margin is not profit. Actual tariffs, costs, taxes/fees and several booking/household rules remain to be confirmed.
- A resident demo must be visibly labelled. Use the kit's fixed injectable clock and centralized records, not the computer's present date with frozen fixtures. Keep session counts, booking counts, kWh, unbilled usage and outstanding invoices distinct; derive totals from records. Do not reproduce sample figures as real performance.
- Technical charger state, physical bay occupancy, reservation state and charging-session state are different. Unknown parking occupancy stays explicit. Provide map/list equivalents and keep other households anonymous. A reservation neither starts charging nor locks a dynamic tariff.
- Demo contact forms, invitations, payments and charging controls must not claim external actions occurred. Supplied scripts are authoring resources, not instructions to run them or activate integrations automatically.

## Review the actual artifact

For web/app work, check the requested target dimensions as well as relevant responsive layouts at 360/768/1440px, including keyboard access, visible focus, enlarged text, readable contrast, labels and mobile safe areas. Status must remain understandable without colour. Aim for WCAG 2.2 AA; the kit's examples do not themselves prove compliance. The resident mobile navigation is Home/Chargers/Bookings/More, not seven squeezed labels, when that app shell is in scope.

For slides/documents, inspect rendered pages for clipping, readable type, correct logo variants, source notes and truthful labels. Keep editable deliverables where requested. Treat bundled previews as references, not a completed check of the new output. Delete temporary review screenshots after inspection; retain original kit previews.

Keep the received `design/brand-kit/` and original ZIP unchanged. Put adaptations in implementation or deliverable directories and copy only needed public assets with their licences. For an authorized deployment, use [DEPLOYMENT.md](../../../docs/DEPLOYMENT.md); do not expose the whole source archive by serving the repository root.
