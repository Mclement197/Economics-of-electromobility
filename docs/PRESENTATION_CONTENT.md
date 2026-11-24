# VoltoShare presentation — 24 November 2026

## Content and sources

`website-src/presentation-data.json` is the shared content source for the browser presentation and editable PowerPoint export. It uses the first **17 VoltoShare slides** of the received `Voltoshare_Slides_Final.pptx`, plus one clearly labelled appendix for the separately supplied Cham profit calculator.

The supplied file actually contains 51 slides. Slides 18–51 are unrelated FlexRide/tourism/urban-rent material and are not included in the VoltoShare presentation. The supplied source file is preserved in the inbound attachment store; it is not copied into the public root. Source slides 8 (roadmap) and 13 (charging simulation), although hidden in the source, are included because they contain relevant VoltoShare content. Student identifiers and empty portrait placeholders are omitted from the public deck; all five team names remain.

| Source slide | Presentation ID | Content |
| --- | --- | --- |
| 1 | auftakt | Cover and five team members |
| 2 | agenda | Team, roadmap, market, product, case, discussion |
| 3 | team | Team names |
| 4 | grundidee | Financing, installation and recurring charges; home/shared charging |
| 5 | markt-zuerich | Population, apartments, rental share, vehicle fleet, vacancy, rationale |
| 6 | markt-elektro | EV stock, registrations, charging gap scenario, closed subsidy programme |
| 7 | markt-potenzial | Total/addressable/target market and subscription assumptions |
| 8 | roadmap | 2026–2030+ development phases, Zug pilot, marketplace vision |
| 9 | hardware | 20/5 illustrative configuration, metering, NFC and load management |
| 10 | plattform | Resident, landlord and operator product roles |
| 11 | ertragsmodell | Service promises, two payment flows and open vacancy decision |
| 12 | case-annahmen | 60 apartments, 15 points, 24 EVs, price/energy/vacancy assumptions |
| 13 | case-laden | Four-step journey and supplied native load curves |
| 14 | case-finanzierung | CHF 60,000 capex, CHF 15,900 operating surplus, cashflow |
| 15 | case-nutzen | Landlord/resident economics and CHF 15/25/35 sensitivity |
| 16 | diskussion | Q&A and thanks, with editorial discussion prompts |
| 17 | quellen | Original references and explicit team assumptions |
| HTML calculator | cham-alternative | Separate per-wallbox fee model; no silent change to the apartment model |

## Editorial precision

- Accidental “FlexRide” labelling on the VoltoShare business-model slide is corrected.
- Potential additional rent is explicitly an assumption, not a guaranteed outcome.
- The original “Ergebnis” of CHF 15,900 is described as an **operating cash surplus**: the source excludes tax, financing and depreciation. Revenue, energy margin, accounting earnings and cashflow must not be conflated.
- The roadmap remains a plan. A Zug pilot is retained alongside the Zürich market analysis; neither is a completed installation claim.
- The source includes charger-control categories as classification options, including bidirectional charging. The new deck does not infer a live V2G service from those labels.
- Slide 13 has inconsistent data: its text states a 59→45 kW peak, but the embedded chart is 53.7→45 kW. The source chart values are retained. Its hourly curves also do not sum to the textual 164 kWh/day; notes identify the curves as separate illustrative simulations. The source text and discrepancy are retained in speaker notes.
- The provided references are reproduced as source attributions, not independently reverified current statistics. Where the original supplies only a domain or publication name, no new article title or fabricated deep link is introduced.
- The optional Cham appendix is not a replacement for the core per-apartment contract model: its fixed fee is **per wallbox**, and its original calculator allocates that fee among charging users.

## Exports

```sh
# Build environment example (outside the repository):
python3 -m venv --system-site-packages /tmp/voltoshare-pptx-venv
/tmp/voltoshare-pptx-venv/bin/pip install python-pptx==1.0.2
/tmp/voltoshare-pptx-venv/bin/python scripts/build-presentation.py

# Optional native presentation render for PDF and review:
libreoffice -env:UserInstallation=file:///tmp/voltoshare-lo-profile \
  --headless --convert-to pdf --outdir /tmp/voltoshare-render \
  website-src/downloads/VoltoShare-Praesentation.pptx
```

The PowerPoint uses the supplied starter's masters/layouts, supplied logo assets and Liberation Sans. Text, shapes, tables and charts remain editable; it is not a slideshow of screenshots. Sources and detailed qualifications appear in speaker notes. The original brand starter and kit remain unchanged.

The downloadable PDF and PPTX are **baseline snapshots**, not exports of a visitor's unsaved interactive scenario. The browser presentation and finance page provide live assumptions and calculations. This distinction is visible in the shared data export note and finance-slide notes.

## Source preservation

Exact supplied originals are retained outside public site roots at `/home/mathis/.local/state/voltoshare/source-2026-11-24/`:

- `Voltoshare_Slides_Final.pptx`: SHA-256 `1acd77e02c611e7e8bff836a790a47de6334cbbf0c526c7fe9f057bcf0bb7202`.
- `VoltoShare_Profitrechner.zip`: SHA-256 `0d4723d76af8009400768ba43c25fbea31993c1cfb0af53446d60b1f851fc2ea`.

## Export checks

The generated PPTX reopens with python-pptx: 18 slides, 363 editable shapes (including table/chart containers), two native charts, valid ZIP members, and no shape outside the 16:9 slide bounds. All populated text boxes and table cells passed a Liberation Sans font-metric wrapping/height check after fixing short roadmap title boxes, charging-step text, finance value widths and source-note layout.

Native PowerPoint/Impress visual rendering was **not verified** on this host: LibreOffice is present, but its Impress component is not installed; even the unchanged supplied starter fails to load. No system package installation was performed. The downloadable PDF is generated and visually inspected separately using the shared browser presentation, so it is not represented as a native PowerPoint-rendered PDF.
