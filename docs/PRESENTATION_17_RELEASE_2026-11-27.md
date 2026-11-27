# Focused 17-slide redesign — 27 November 2026

## Superseding request

Mathis rejected the earlier 51-slide redesign and explicitly requested cutting the presentation after slide 17 and redesigning the first 17. This supersedes the previous all-51 publishing requirement. The original received 51-slide file remains private and untouched; only original slides 1–17 now belong in the published PowerPoint, PDF, browser navigation and accessible transcript. Original hidden flags on 8 and 13 remain in PowerPoint; browser and PDF show all 17.

## Design and content boundaries

- Preserve exactly the original first-17 wording, notes, source pictures, charts, values and order. The supplied files remain the content master, including existing inconsistencies and placeholders.
- Replace the prior compositions with a coordinated white/forest/graphite editorial system, not an editorial rewrite. Keep original editable PowerPoint objects.
- Introductory designs: `scripts/presentation_premium_intro.py` (1–8).
- Product and financial story: `scripts/presentation_premium_story.py` (9–17).
- The integrated browser Live-Szenario still follows original slide 14; financial formulas, controls and tenant application are outside this cosmetic change.
- PDF and vector browser artwork derive from the same native Impress render. Native Microsoft PowerPoint rendering is not claimed.
- LinkedIn photos remain pending the requested uploads; no guessed replacement portraits.

## Verification and release

- Independent source-scope checks: 156 checks against exactly original slides 1–17, including a guard that no excluded slide parts remain in the PPTX. The old 51-slide artifact is rejected by the updated audit.
- Full derivative audit: 263 checks, covering exact content, original source hash, selected source-slide mapping, native images/chart data/notes/hidden flags and matching browser revision. Obsolete SVGs are rejected.
- Browser staging: 190 presentation/finance checks and 74 focused live-finance checks passed, including End navigation to slide 17, only two original hidden-slide labels and a 404 for excluded slide 18 artwork.
- Visual review covered all 17 native pages; final changed pages are rechecked after wrapping/contrast fixes. Mixed-size heading/body boxes bypass the old uniform-font autofitter so intentional hierarchies are not flattened.
- Fonts, original source file and the brand kit are unchanged. Native source chart data stays editable; the existing negative-bar rendering style fix is retained.

Final release evidence follows below.

## Published 17-slide build

- Published revision `ac1e3110b3e7`; native PDF has exactly 17 pages.
- Final source/browser audit: 263 checks passed. Public browser suite: 190 checks passed, including all17 rendered assets, retained live scenarios, fullscreen, accessible text and excludedslide18 returning404.
- Public manifest/PPTX/PDF and correctedslide12 SVG matchlocalSHA256; excludedslide51 also returns404.
- Website-only rollback: `~/.local/state/voltoshare/releases/website-20261127T092956942578Z`. No tenantapp, account, service, DNS or tunnel changes.
- An interrupted native export left a stale output lock; the final export was regenerated in a fresh directory and the resulting PDF/image inspected. Do not treat the earlier missing export as delivered.
- Final labels on12fit without mid-word wrapping. Every slide was inspected in the native draft and affectedslides were rechecked afterfixes.

- `presentation-data.json`: `018832fa4602a70dd942a7fee7834bdecb58daa9408f2f536294cb7ea994884e`
- `downloads/VoltoShare-Praesentation.pptx`: `ac1e3110b3e7431795a2bb5ac9e408932fe3dc2bec075b519f681f8dd8ffbf2f`
- `downloads/VoltoShare-Praesentation.pdf`: `6858650bd61a44f90f780901a70872ff96cbbdb407efbc4cd22e8de1a4c14fd5`
- `assets/slides/slide-12.svg`: `aa2d81a3055017ec4d1364fb0a7229751e68a1904a2d9f31b017ad9447bc59c8`
