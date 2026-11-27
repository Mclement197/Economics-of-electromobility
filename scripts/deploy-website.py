#!/usr/bin/env python3
"""Install an already-verified static website; preserve a dated rollback copy."""
import argparse, datetime, json, os, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('build',type=Path)
a=p.parse_args(); source=a.build.resolve(); live=ROOT/'sites/website'
required=['finanzen/index.html','praesentation/index.html','finance-model.mjs','finance-ui.mjs','finance.css','presentation.mjs','presentation.css','presentation-data.json','downloads/VoltoShare-Praesentation.pdf','downloads/VoltoShare-Praesentation.pptx','index.html','geschaeftsmodell/index.html','kontakt/index.html','impressum/index.html','datenschutz/index.html','site.css','site.mjs','assets/logo-navigation.svg','assets/fonts/LiberationSans-Regular.ttf','favicon.svg','site.webmanifest']
required += [f'assets/slides/slide-{i:02d}.{ext}' for i in range(1,18) for ext in ['svg','png']]
for f in required:
    if not (source/f).is_file():p.error(f'Missing build file: {f}')
manifest=json.loads((source/'presentation-data.json').read_text())
if [s.get('number') for s in manifest.get('slides',[])]!=list(range(1,18)):p.error('Presentation must contain only the 17 authorized slides.')
if {f.name for f in (source/'assets/slides').glob('slide-*.svg')}!={f'slide-{i:02d}.svg' for i in range(1,18)}:p.error('Build retains missing or obsolete slide artwork.')
if {f.name for f in (source/'assets/slides').glob('slide-*.png')}!={f'slide-{i:02d}.png' for i in range(1,18)}:p.error('Build must contain exactly 17 stable raster slides.')
if any(not s.get('image','').startswith(f'/assets/slides/slide-{i:02d}.png?v=') for i,s in enumerate(manifest['slides'],1)):p.error('Player must use the stable PNG derivatives.')
if source==live or source in live.parents:p.error('Use a separate, verified build folder.')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
state=Path.home()/'.local/state/voltoshare/releases';state.mkdir(parents=True,exist_ok=True)
backup=state/('website-'+stamp)
# Stage beside live so both renames stay on the same filesystem.
staged=ROOT/'sites'/('.website-next-'+stamp)
shutil.copytree(source,staged)
if live.exists():shutil.copytree(live,backup)
previous=ROOT/'sites'/('.website-previous-'+stamp)
try:
    if live.exists():os.rename(live,previous)
    try:os.rename(staged,live)
    except BaseException:
        if previous.exists():os.rename(previous,live)
        raise
finally:
    # Retain the displaced tree outside the public sites path as an extra fallback.
    if previous.exists():shutil.move(str(previous),str(state/('displaced-'+stamp)))
print(f'Deployed website only: {live}\nRollback copy: {backup}\nNo app, service, DNS or tunnel changes.')
