#!/usr/bin/env python3
"""Install an already-verified static website; preserve a dated rollback copy."""
import argparse, datetime, os, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('build',type=Path)
a=p.parse_args(); source=a.build.resolve(); live=ROOT/'sites/website'
required=['finanzen/index.html','praesentation/index.html','finance-model.mjs','finance-ui.mjs','finance.css','presentation.mjs','presentation.css','presentation-data.json','downloads/VoltoShare-Praesentation.pdf','downloads/VoltoShare-Praesentation.pptx','index.html','geschaeftsmodell/index.html','kontakt/index.html','impressum/index.html','datenschutz/index.html','site.css','site.mjs','assets/logo-navigation.svg','assets/fonts/LiberationSans-Regular.ttf','favicon.svg','site.webmanifest']
required += [f'assets/slides/slide-{i:02d}.svg' for i in range(1,52)]
for f in required:
    if not (source/f).is_file():p.error(f'Missing build file: {f}')
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
