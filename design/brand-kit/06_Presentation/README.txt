VOLTOSHARE PRESENTATION STARTER

Files
- VoltoShare_Presentation_Starter.pptx: six editable 16:9 slides.
- VoltoShare_Presentation_Starter_Preview.pdf: visual preview for sharing.
- previews/: six individual 1920 x 1080 PNG slides.
- source/: reproducible JavaScript authoring source and PDF-preview script.

Editing
Install Liberation Sans Regular and Bold from ../04_Fonts before editing.
All headings, body copy, numerical examples, and tables are native editable
PowerPoint content. The supplied logos and concept visuals remain images.
Use the PPTX as the working file. The PDF is an image-based visual preview.

Purpose
This is a presentation starter, not a complete evaluated pitch. Replace the
cover subtitle with team details and add your research, evidence and analysis
as needed. Slides 3 and 5 contain native tables. Unknown monetary assumptions
are deliberately marked To be confirmed. The 20 / 5 / 20 illustration is the
proposal example at full occupancy, not a verified deployed installation.

Sources
The factual content follows the supplied VoltoShare_Expose_DE(1).pdf, page 1.
Speaker notes record source boundaries and distinguish user-brief features
from proposal facts. Supplied charger and NFC-card images are concept visuals.
The logo uses the original supplied flat artwork with a native image crop,
so the original lettering is preserved.

Rebuilding
Requires Node.js with @oai/artifact-tool available in the module resolution
path and the included Liberation Sans fonts installed. Keep the kit folder
structure intact, then run:
  node source/build-presentation.mjs

The authoring script regenerates the PPTX and six PNG previews. Where native
PDF export is unavailable, run the included fallback (requires reportlab):
  python source/create-preview-pdf.py

Quality checks
All six authoring renders were visually inspected. The final PPTX passes
package, geometry, font-family and first-party re-import checks. Native
PowerPoint desktop rendering was not available for verification.
