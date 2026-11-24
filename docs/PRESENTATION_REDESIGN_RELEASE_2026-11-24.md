# Cosmetic-only presentation redesign — 24 November 2026

## Request and completion

Mathis requested nicer slides with **exactly the same content as the supplied original PowerPoint**, changing cosmetics only. This supersedes the editorial decisions in the earlier finance/presentation release.

- Redesigned the original 51-slide PPTX, with focused editorial layouts for the 17 VoltoShare slides and typography/palette/wrapping repairs for the remaining original material.
- Preserved source order, original notes, three native charts with every series/data value, picture payloads, tables, all text (including source inconsistencies/placeholders) and original hidden flags.
- Produced the PDF through an isolated local native Impress renderer; generated vector browser slide artwork from that same PDF. No system packages installed, no Microsoft PowerPoint rendering claimed.
- Replaced the editorial browser reconstruction with the matching artwork, plus accessible original-text/chart-data reading mode, overview, keyboard/fullscreen navigation and a separately labelled interactive finance lab. Changing scenarios never edits source slide content.
- Removed the previously added Cham appendix slide; its scenario remains available in the separate lab and financial page.
- Website changes only. App project links continue to reach the same presentation; accounts, bookings and billing are untouched.

## Verification evidence

- `python3 tests/presentation-fidelity.py`: **769 checks passed** against the original, including browser transcript and final PPTX revision.
- 24 existing pure financial/calculator checks passed.
- 129 existing website browser checks passed on staging.
- All main slides and appendix contact sheets visually reviewed through native PDF renders. Repaired hard wraps, content overlaps, chart palette, source table title clipping and diagram-label contrast. Final native pages 27 and 47 inspected after the last fixes.
- Interactive presentation browser checks cover every slide/artwork, exact accessible text, chart series, hidden labels, finance lab live updates/persistence/reset, focus trap, fullscreen/Escape, phone/tablet/desktop layouts, print51 and actual downloads. Final outcomes recorded below after execution.

## Reproduction and source

See `PRESENTATION_CONTENT.md`. Final editable PowerPoint SHA-256:
`afb18798e918c00128496d2b7e8014f4723849a799b5fb7325fd61d6a6917772`.

Renderer: locally extracted Debian LibreOffice Impress under `/tmp/volto-lo`; native export includes original hidden slides. Authoring dependencies are not deployed. Temporary review images are removed after inspection.

## Final deployment results

- **394** interactive source-exact presentation/finance browser checks passed on staging and again on public HTTPS, including the repaired modal keyboard focus trap.
- Public bytes match all five primary artifacts: manifest, viewer JS/CSS, native PDF and editable PPTX.
- Both website and app services active. No app/service/DNS/tunnel changes.
- Deployment rollback: `~/.local/state/voltoshare/releases/website-20261124T121530375543Z`.
- Temporary original/redesign/contact-sheet review images removed after inspection.
