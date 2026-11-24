#!/usr/bin/env python3
"""Render the editable deck once for identical PDF and browser slides.
Requires python-pptx, a full LibreOffice Impress, and pdftocairo.
Original content (not editorial summaries) provides accessible reading text.
"""
import argparse, hashlib, json, os, shutil, subprocess, tempfile
from pathlib import Path
from pptx import Presentation
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,default=Path.home()/'.local/state/voltoshare/source-2026-11-24/Voltoshare_Slides_Final.pptx')
p.add_argument('--office',default=os.environ.get('LIBREOFFICE','libreoffice'))
p.add_argument('--pdf',type=Path,help='Use an already-rendered PDF including hidden pages')
a=p.parse_args()
pptx=ROOT/'website-src/downloads/VoltoShare-Praesentation.pptx'
pdf=pptx.with_suffix('.pdf')
if a.pdf:
 import shutil
 shutil.copy2(a.pdf,pdf)
else:
 with tempfile.TemporaryDirectory(prefix='volto-export-') as tmp:
  subprocess.run([a.office,'-env:UserInstallation='+Path(tmp,'profile').as_uri(),'--headless','--convert-to','pdf:impress_pdf_Export:{"ExportHiddenSlides":{"type":"boolean","value":"true"}}','--outdir',tmp,str(pptx)],check=True,timeout=180)
  rendered=Path(tmp)/pdf.name
  if not rendered.exists():raise SystemExit('Impress did not produce a fresh PDF')
  shutil.copy2(rendered,pdf)
info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
if 'Pages:           51' not in info:raise SystemExit('Expected exactly 51 PDF pages, including hidden slides')
revision=hashlib.sha256(pptx.read_bytes()).hexdigest()[:12]
assets=ROOT/'website-src/assets/slides';assets.mkdir(exist_ok=True)
prs=Presentation(a.source)
def walk(shapes):
 for s in shapes:
  if s.shape_type==6:yield from walk(s.shapes)
  else:yield s
slides=[]
for i,s in enumerate(prs.slides,1):
 texts=[];charts=[]
 for shape in walk(s.shapes):
  if shape.has_text_frame and shape.text.strip():texts.append(shape.text)
  if shape.has_table:
   for row in shape.table.rows:texts.append(' · '.join(c.text for c in row.cells))
  if shape.has_chart:
   chart=shape.chart
   charts.append({'title':chart.chart_title.text_frame.text if chart.has_title and chart.chart_title.has_text_frame else '', 'categories':[str(c.label) for c in chart.plots[0].categories], 'series':[{'name':x.name,'values':list(x.values)} for x in chart.series]})
 title=s.shapes.title.text if s.shapes.title and s.shapes.title.text.strip() else next((t for t in texts if t.strip() and t not in ['VoltoShare','Gruppe 1 - FlexRide'] and not t.strip().isdigit()),f'Originalfolie {i}')
 if i==1:title='VoltoShare'
 if i in [44,51]:title=f'Originalfolie {i}'
 image=assets/f'slide-{i:02d}.svg'
 subprocess.run(['pdftocairo','-svg','-f',str(i),'-l',str(i),str(pdf),str(image)],check=True,timeout=60)
 slides.append({'number':i,'title':title,'hidden':s._element.get('show')=='0','image':f'/assets/slides/{image.name}?v={revision}','text':texts,'charts':charts,'notes':s.notes_slide.notes_text_frame.text if s.has_notes_slide else ''})
(ROOT/'website-src/presentation-data.json').write_text(json.dumps({'title':'VoltoShare','revision':revision,'sourceSha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'slides':slides},ensure_ascii=False,indent=2)+'\n')
print(f'Exported {len(slides)} source-exact slides, PDF, vector browser artwork, and accessible transcript ({revision})')
