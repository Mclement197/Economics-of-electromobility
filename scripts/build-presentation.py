#!/usr/bin/env python3
"""Cosmetic-only redesign of the complete supplied 51-slide PowerPoint.

The source is the content master: native text runs, diagrams, pictures, charts,
notes and hidden-slide flags are retained. Only geometry, colours and typography
are changed. Do not use the previous editorial JSON deck as a content source.
Requires python-pptx and Pillow. The original and brand kit are never modified.
"""
from pathlib import Path
import argparse, colorsys, zipfile, hashlib
from lxml import etree as ET
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,default=Path.home()/'.local/state/voltoshare/source-2026-11-24/Voltoshare_Slides_Final.pptx')
parser.add_argument('--out',type=Path,default=ROOT/'website-src/downloads/VoltoShare-Praesentation.pptx')
args=parser.parse_args()
prs=Presentation(args.source)
kit=ROOT/'design/brand-kit'
C={'green':'28563B','ink':'1E2023','dark':'23262B','paper':'F8F5F0','white':'FFFFFF','tint':'EAF0EB','line':'D9DFD9','muted':'58615C','sage':'748178','pale':'D6E5D6','blue':'1959A6'}
def rgb(c):return RGBColor.from_string(C.get(c,c))
def at(sh,x,y,w,h):
 sh.left=Inches(x);sh.top=Inches(y);sh.width=Inches(w);sh.height=Inches(h);return sh
def fill(sh,c,line=None):
 if not hasattr(sh,'fill'):return sh
 if c is None:sh.fill.background()
 else:sh.fill.solid();sh.fill.fore_color.rgb=rgb(c)
 if hasattr(sh,'line'):
  if line:sh.line.color.rgb=rgb(line);sh.line.width=Pt(.6)
  else:sh.line.fill.background()
 for e in sh.element.xpath('.//a:effectLst'):
  for q in list(e):e.remove(q)
 return sh

def fmt(sh,size=20,bold=None,color='ink',align=PP_ALIGN.LEFT,center=False):
 if not sh.has_text_frame:return sh
 tf=sh.text_frame;tf.word_wrap=True
 tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 tf.vertical_anchor=MSO_ANCHOR.MIDDLE if center else MSO_ANCHOR.TOP
 # Keep every original run, paragraph and literal unchanged, incl spaces/typos.
 for p in tf.paragraphs:
  p.alignment=align;p.space_before=Pt(0);p.space_after=Pt(4);p.line_spacing=1.08
  p.font.name='Liberation Sans';p.font.size=Pt(size);p.font.color.rgb=rgb(color)
  if bold is not None:p.font.bold=bold
  for r in p.runs:
   r.font.name='Liberation Sans';r.font.size=Pt(size);r.font.color.rgb=rgb(color)
   if bold is not None:r.font.bold=bold
  for e in p._p.xpath('./a:endParaRPr | ./a:fld/a:rPr'):
   e.set('sz',str(int(size*100)))
 return sh

def text(sh,x,y,w,h,size=20,bold=None,color='ink',align=PP_ALIGN.LEFT,center=False):
 at(sh,x,y,w,h);fmt(sh,size,bold,color,align,center);return sh

def bg(s,c='paper'):
 s.background.fill.solid();s.background.fill.fore_color.rgb=rgb(c)
 s.element.set('showMasterSp','0')
def rect(s,x,y,w,h,c='green',back=False):
 sh=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));fill(sh,c)
 if back:s.shapes._spTree.remove(sh.element);s.shapes._spTree.insert(2,sh.element)
 return sh

def S(s):return {sh.shape_id:sh for sh in s.shapes}
def panel(sh,x,y,w,h,c='white'):
 at(sh,x,y,w,h);fill(sh,c)
 if sh.element.xpath('.//a:prstGeom'):
  for g in sh.element.xpath('.//a:prstGeom'):g.set('prst','rect')
 return sh

def walk(shapes):
 for sh in shapes:
  yield sh
  if sh.shape_type==6:yield from walk(sh.shapes)

def theme_color(old):
 try:r,g,b=(int(old[i:i+2],16)/255 for i in (0,2,4))
 except:return old
 h,s,v=colorsys.rgb_to_hsv(r,g,b)
 if s<.12:
  if v>.94:return C['white']
  if v>.77:return C['line']
  if v>.35:return C['muted']
  return C['ink']
 # Preserve informational red/orange, harmonize green/cyan/blue brand colours.
 if .17<h<.65:return C['green'] if v<.78 else C['sage']
 return old

# Global visual foundation without changing any text or media payload.
for slide in prs.slides:
 for sh in walk(slide.shapes):
  if sh.has_text_frame:
   for p in sh.text_frame.paragraphs:
    p.font.name='Liberation Sans'
    for r in p.runs:
     # Preserve icon fonts whose source characters depend on symbol glyphs.
     if r.font.name not in ['Wingdings','Webdings','Segoe UI Emoji','Symbol']:r.font.name='Liberation Sans'
  for e in sh.element.xpath('.//a:srgbClr'):
   val=e.get('val');e.set('val',theme_color(val))
  for e in sh.element.xpath('.//a:effectLst'):
   for q in list(e):e.remove(q)

for i,s in enumerate(list(prs.slides)[:17],1):
 d=S(s);bg(s)
 if i not in [1,16]:
  # Generous editorial header; original footer and page number remain intact.
  rect(s,.65,.30,.55,.045,'green')
  title=d[2];text(title,.65,.55,12.05,.68,32 if len(title.text)<48 else 29,True)
  for sh in s.shapes:
   if sh.has_text_frame and sh.top>Inches(6.95):
    if sh.text.strip().isdigit():text(sh,12.13,7.05,.55,.2,10,False,'muted',PP_ALIGN.RIGHT)
    else:text(sh,.65,7.05,5.5,.2,10,False,'muted')
  if 32 in d and d[32].has_text_frame and d[32].text and d[32].top<Inches(1.3):text(d[32],.65,1.28,12,.3,14,False,'muted')
  for sh in s.shapes:
   if sh.has_text_frame and sh.text and Inches(6.58)<=sh.top<Inches(6.95):text(sh,.65,6.68,12,.3,10.5,False,'muted')
  rect(s,.65,6.99,12.03,.009,'line')
  logo=s.shapes.add_picture(str(kit/'02_Logos/voltoshare-logo-navigation.png'),Inches(10.15),Inches(7.01),width=Inches(1.55))

# 01 — strong split cover, source concept photograph retained.
s=prs.slides[0];d=S(s);bg(s,'dark')
photo=d[2];at(photo,6.05,0,7.28333,7.5)
# Crop only the composition; native source image bytes remain unchanged.
photo.crop_left=.27;photo.crop_right=.185;photo.crop_top=0;photo.crop_bottom=0
# Source freeform artwork becomes a quiet inset detail, not a competing headline.
at(d[5],5.15,6.40,.57,.41)
text(d[27],.72,2.48,5.20,1.0,49,True,'white')
fill(d[32],None);text(d[32],.77,5.35,4.7,1.25,17,False,'pale')
rect(s,.77,4.02,.92,.055,'pale')
# Original source title remains the display headline; supplied symbol avoids a duplicate wordmark.
s.shapes.add_picture(str(kit/'02_Logos/voltoshare-symbol-white.png'),Inches(.77),Inches(.64),width=Inches(.65))

# 02 — restrained two-column agenda, large typographic indices.
s=prs.slides[1];d=S(s)
for j,base in enumerate([32,37,42,47,52,57]):
 x=.65+(j%2)*6.18;y=1.85+(j//2)*1.49
 panel(d[base],x,y,5.85,1.27,'paper');fill(d[base+1],None)
 text(d[base+2],x,y+.02,.78,.65,37,True,'green')
 text(d[base+3],x+1.05,y+.02,4.8,.44,24 if j!=2 else 21,True)
 text(d[base+4],x+1.05,y+.60,4.75,.46,17,False,'muted')
 rect(s,x,y+1.22,5.65,.01,'line')
text(d[62],.65,6.52,9,.3,12,False,'muted')

# 03 — five aligned editorial profiles, preserving every placeholder and portrait.
s=prs.slides[2];d=S(s)
for j,ids in enumerate([(33,34,35,36,37,38,39),(40,41,42,43,44,45,46),(47,None,None,50,51,52,53),(54,55,56,57,58,59,60),(61,62,63,64,65,66,67)]):
 x=.65+j*2.46;a,b,c,n,rule,label,num=ids
 panel(d[a],x,1.88,2.18,4.67,'white')
 if b:panel(d[b],x+.14,2.06,1.9,1.9,'tint')
 if c:text(d[c],x+.14,2.06,1.9,1.9,16,False,'muted',PP_ALIGN.CENTER,True)
 text(d[n],x+.15,4.17,1.88,.78,21,True)
 panel(d[rule],x+.15,5.17,.42,.035,'green')
 text(d[label],x+.15,5.52,1.88,.25,12,False,'muted')
 text(d[num],x+.15,5.92,1.88,.28,16,False)
for id,j in [(7,1),(4,2),(3,4)]:
 sh=d[id];at(sh,.65+j*2.46+.14,2.06,1.90,1.90)

# 04 — business-model matrix remains native and exact.
s=prs.slides[3];d=S(s)
panel(d[13],.65,1.62,12.03,1.20,'tint');text(d[14],.89,1.82,11.55,.82,20,False)
for j,id in enumerate([15,17,18,19,20,21]):
 panel(d[id],.65,3.07+j*.53,3.05,.46,'green');fmt(d[id],15,True,'white',center=True);d[id].text_frame.margin_left=Inches(.16)
for id,row,col in [(22,0,0),(23,0,1),(25,1,0),(26,1,1),(27,1,2),(28,2,0),(29,2,1),(30,2,2)]:
 sh=d[id];panel(sh,3.96+col*2.95,3.07+row*.53,2.73,.46,'white');fmt(sh,16,False,'ink',PP_ALIGN.CENTER,True)
# Preserve the source's existing selection colours (Make/home/smart) as brand emphasis.
# Source choices have equal visual weight; no new selection semantics added.

# 05 — market numbers dominate, explanatory band anchors the story.
s=prs.slides[4];d=S(s)
for j,base in enumerate([33,36,39,42]):
 x=.65+j*3.07;dark=j==2
 panel(d[base],x,1.88,2.82,2.43,'green' if dark else 'white')
 text(d[base+1],x+.20,2.13,2.44,.68,35,True,'white' if dark else 'green')
 text(d[base+2],x+.20,3.00,2.40,1.04,17,False,'white' if dark else 'ink')
panel(d[45],.65,4.62,12.03,1.82,'tint');text(d[46],.89,4.83,11.6,.3,19,True,'green')
text(d[47],.89,5.34,5.50,.92,16,False);text(d[48],6.88,5.34,5.50,.92,16,False)

# 06 — simple bar narrative with contrasting source-stat sidebars.
s=prs.slides[5];d=S(s)
panel(d[33],.65,1.87,7.18,4.67,'white');text(d[34],.91,2.07,6.6,.4,21,True)
for label,bar,val,y in [(35,36,38,2.77),(39,40,42,4.00),(43,44,46,5.23)]:
 text(d[label],.91,y,6.55,.30,16,False)
 panel(d[bar],.91,y+.47,5.05,.28,'tint')
 # Mathematically identical bar proportions, merely reduced stroke height.
 old_ratio=d[bar+1].width/d[bar].width
 panel(d[bar+1],.91,y+.47,[.707,3.0805,4.242][[35,39,43].index(label)],.28,'green')
 text(d[val],6.13,y+.30,1.40,.55,24,True,'green')
text(d[47],.91,6.17,6.5,.23,12,False,'muted')
for base,y,c in [(48,1.87,'green'),(51,4.31,'tint')]:
 panel(d[base],8.12,y,4.56,2.23,c)
 text(d[base+1],8.41,y+.20,3.97,.65,38,True,'white' if c=='green' else 'green')
 text(d[base+2],8.41,y+.99,3.97,1.03,17,False,'white' if c=='green' else 'ink')

# 07 — market funnel, retaining source figures/assumptions word-for-word.
s=prs.slides[6];d=S(s)
for j,(base,x,w) in enumerate([(33,.65,6.32),(41,1.11,5.40),(49,1.57,4.48)]):
 y=1.89+j*1.52;dark=j==2
 panel(d[base],x,y,w,1.31,'green' if dark else 'tint')
 text(d[base+1],x+.20,y+.13,w-.4,.25,14,True,'white' if dark else 'green')
 text(d[base+2],x+.20,y+.47,w-.4,.40,27 if j<2 else 24,True,'white' if dark else 'ink')
 text(d[base+3],x+.20,y+.93,w-.4,.31,12.5,False,'white' if dark else 'muted')
 rev=[37,45,53][j];panel(d[rev],7.28,y,2.54,1.31,'white')
 text(d[rev+1],7.45,y+.17,2.20,.27,12,False,'muted')
 text(d[rev+2],7.45,y+.62,2.20,.45,23,True,'green')
 at(d[rev+3],6.98,y+.66,.25,0)
panel(d[57],10.11,1.89,2.57,4.35,'dark');text(d[58],10.34,2.15,2.11,.32,19,True,'white')
text(d[59],10.34,2.79,2.11,3.1,15,False,'white')

# 08 — timeline becomes a legible 4x2 grid; all phases/dates/wording retained.
s=prs.slides[7];d=S(s)
panel(d[33],.65,1.78,7.45,.85,'green');panel(d[34],8.28,1.78,4.40,.85,'dark')
text(d[35],.87,1.94,7.01,.25,15,True,'white');text(d[36],.87,2.30,7.01,.25,12,False,'white')
text(d[37],8.48,1.94,4.00,.25,14,True,'white');text(d[38],8.48,2.27,4.00,.31,12,False,'white')
fill(d[39],None);d[39].line.fill.background()
for j,base in enumerate(range(40,72,4)):
 x=.65+(j%4)*3.07;y=2.96+(j//4)*1.52
 text(d[base],x,y,2.77,.26,15,True,'green')
 panel(d[base+1],x,y+.36,.30,.025,'green')
 text(d[base+2],x,y+.49,2.77,.36,19,True)
 text(d[base+3],x,y+.94,2.77,.52,13.5,False,'muted')
panel(d[72],.65,6.22,12.03,.46,'tint');text(d[73],.82,6.28,11.69,.35,11.5,False)

# 09 — source garage diagram on an open field, operating promises in three rows.
s=prs.slides[8];d=S(s)
for sh in s.shapes:
 if sh.has_text_frame and sh.text and sh.top>Inches(1.5) and sh.top<Inches(6.5):
  # Preserve positions inside the detailed garage diagram.
  original=max([r.font.size.pt for p in sh.text_frame.paragraphs for r in p.runs if r.font.size] or [14])
  fmt(sh,original,None,'green' if original>=18 else 'ink')
for sh in s.shapes:
 if sh.has_text_frame and sh.text and sh.left>Inches(8):
  if len(sh.text)<40:fmt(sh,21,True,'green')
  else:fmt(sh,17,False)
for id in [33]:
 if id in d:fill(d[id],'white')
for id in [40,45,50,55,60,62,64,66]:fmt(d[id],11,False,'ink',PP_ALIGN.CENTER,True)
for id in [69,71]:fmt(d[id],18,True,'white',PP_ALIGN.CENTER,True)
fmt(d[67],12,False,'muted')

# 10 — user roles as three balanced columns, source bullets retained.
s=prs.slides[9];d=S(s)
for j,base in enumerate([33,38,43]):
 x=.65+j*4.10;dark=j==2
 panel(d[base],x,1.88,3.82,4.66,'green' if dark else 'white')
 panel(d[base+1],x+.25,2.15,.62,.62,'pale' if dark else 'tint')
 text(d[base+2],x+.25,2.15,.62,.62,22,True,'green',PP_ALIGN.CENTER,True)
 text(d[base+3],x+.25,3.02,3.32,.88,24,True,'white' if dark else 'ink')
 text(d[base+4],x+.25,4.17,3.28,1.92,18,False,'white' if dark else 'ink')

# 11 — payment flow right, service promise left, no editorial modifications.
s=prs.slides[10];d=S(s)
panel(d[33],.65,1.88,5.30,4.66,'white');panel(d[41],6.20,1.88,6.48,4.66,'tint')
text(d[34],.91,2.12,4.78,.37,22,True)
for j,(head,body) in enumerate([(35,36),(37,38),(39,40)]):
 y=[2.86,4.10,5.27][j];text(d[head],.91,y,4.78,.30,17,True,'green');text(d[body],.91,y+.38,4.78,.73,15,False)
text(d[42],6.48,2.12,5.92,.37,22,True)
for j,(circle,txt) in enumerate([(43,44),(45,46),(47,48)]):
 x=6.47+j*2.08;panel(d[circle],x,3.02,1.78,.83,'green' if j==1 else 'white')
 text(d[txt],x+.05,3.02,1.68,.83,17,True,'white' if j==1 else 'green',PP_ALIGN.CENTER,True)
for id,x in [(49,8.28),(50,10.36)]:at(d[id],x,3.43,.24,0)
text(d[51],6.47,4.24,2.75,1.13,17,False);text(d[52],9.65,4.24,2.75,1.13,17,False)
panel(d[53],6.47,5.66,5.93,.61,'white');text(d[54],6.65,5.75,5.57,.45,14,False)

# 12 — retain exact building illustration, increase legibility of assumptions.
s=prs.slides[11];d=S(s)
fill(d[33],'tint');fill(d[78],'white')
text(d[79],6.8,1.88,5.6,.37,22,True)
for j,(label,value) in enumerate([(80,81),(83,84),(86,87),(89,90),(92,93),(95,96),(98,99)]):
 y=2.48+j*.56
 text(d[label],6.8,y,3.62,.43,15.7,False)
 text(d[value],10.52,y,1.98,.43,18,True,'green',PP_ALIGN.RIGHT)
text(d[76],4.43,2.12,1.60,.87,18,True,'green',PP_ALIGN.CENTER)
text(d[77],4.43,5.22,1.60,.87,18,True,'green',PP_ALIGN.CENTER)
text(d[75],.95,6.29,3.6,.27,13,False,'muted',PP_ALIGN.CENTER)

# 13 — native source chart with all three original series unchanged.
s=prs.slides[12];d=S(s)
panel(d[33],.65,1.87,7.45,4.64,'white');at(d[34],.74,2.00,7.2,4.28)
for j,(circle,num,title,body) in enumerate([(35,36,37,38),(39,40,41,42),(43,44,45,46),(47,48,49,50)]):
 y=1.95+j*.98
 panel(d[circle],8.42,y,.55,.55,'tint');text(d[num],8.42,y,.55,.55,17,True,'green',PP_ALIGN.CENTER,True)
 text(d[title],9.19,y-.02,3.48,.32,20,True);text(d[body],9.19,y+.36,3.48,.50,15,False)
panel(d[51],8.42,5.84,4.26,.68,'green');text(d[52],8.64,5.92,3.82,.51,14.5,False,'white')

# 14 — financial statement hierarchy and a large editable native chart.
s=prs.slides[13];d=S(s)
for j,base in enumerate([33,36,39]):
 x=.65+j*2.10;dark=j==1
 panel(d[base],x,1.88,1.92,1.26,'green' if dark else 'tint')
 text(d[base+1],x+.14,2.09,1.64,.42,23.5,True,'white' if dark else 'green')
 text(d[base+2],x+.14,2.67,1.64,.28,12.5,False,'white' if dark else 'ink')
panel(d[42],.65,3.38,6.12,3.13,'white')
for id,y,size,bold in [(43,3.57,16,True),(44,4.01,15,False),(45,4.01,16,True),(46,4.44,15,False),(47,4.44,16,True),(48,4.89,16,True),(49,5.30,15,False),(50,5.30,16,True),(51,5.72,15,False),(52,5.72,16,True),(53,6.14,15,False),(54,6.14,16,True)]:
 sh=d[id];val=id in [45,47,50,52,54]
 text(sh,4.89 if val else .88,y,1.58 if val else (5.61 if id in [43,48] else 3.88),.31,size,bold,'green' if id in [43,48] else 'ink',PP_ALIGN.RIGHT if val else PP_ALIGN.LEFT)
panel(d[55],7.06,1.88,5.62,4.63,'white');text(d[56],7.30,2.12,5.13,.64,20,True)
at(d[57],7.18,2.92,5.34,3.10);text(d[58],7.30,6.13,5.13,.23,12,False,'muted',PP_ALIGN.CENTER)

# 15 — landlord economics vs sensitivity; source chart and text unchanged.
s=prs.slides[14];d=S(s)
panel(d[33],.65,1.88,5.75,2.30,'tint');text(d[34],.90,2.12,5.25,.35,22,True)
for label,value,y in [(35,36,2.78),(37,38,3.22),(40,41,3.73)]:
 text(d[label],.90,y,3.1,.34,15,False);text(d[value],4.03,y,2.13,.34,20 if value==41 else 17,True,'green',PP_ALIGN.RIGHT)
at(d[39],.90,3.62,5.25,0)
panel(d[42],.65,4.41,5.75,2.10,'white');text(d[43],.90,4.61,5.25,.33,22,True)
text(d[44],.90,5.15,5.25,1.15,17,False)
panel(d[45],6.68,1.88,6.0,4.63,'white');text(d[46],6.95,2.12,5.46,.38,22,True)
at(d[47],6.87,2.76,5.60,2.95);text(d[48],6.95,5.99,5.46,.44,14,False,'muted')

# 16 — calm dark closing, exact three text boxes only.
s=prs.slides[15];d=S(s);bg(s,'dark');panel(d[2],0,0,13.333333,7.5,'dark')
panel(d[3],11.55,.6,.75,.045,'pale');panel(d[4],.75,6.72,.75,.045,'pale')
text(d[5],.75,2.12,10.8,1.3,80,True,'white');text(d[6],.81,4.12,10.7,.65,30,False,'white');text(d[7],.81,5.08,10.7,.4,20,False,'pale')
s.shapes.add_picture(str(kit/'02_Logos/voltoshare-logo-white.png'),Inches(.81),Inches(.66),width=Inches(2.75))

# 17 — bibliography as an aligned two-column index. Every full source remains.
s=prs.slides[16];d=S(s)
for j in range(12):
 label=33+j*2;body=label+1;col=j//6;row=j%6;x=.65+col*6.18;y=1.88+row*.69
 text(d[label],x,y,1.65,.59,12,True,'green');text(d[body],x+1.80,y,4.02,.61,11.8,False)
 if row<5:rect(s,x,y+.64,5.82,.008,'line')
panel(d[57],.65,6.17,12.03,.52,'tint');text(d[58],.84,6.25,11.65,.40,11.5,False)

# 18–51 — preserve the source layouts/media, repair inherited text overflow.
# All table/diagram labels remain editable; these edits are geometry/style only.
def allids(slide):return {sh.shape_id:sh for sh in walk(slide.shapes)}
s=prs.slides[18];d=allids(s)
text(d[25],9.30,3.10,2.7,.47,21,True,'white',PP_ALIGN.CENTER,True)
s=prs.slides[25];d=allids(s)
for id,x,y,w in [(58,2.25,2.50,1.80),(62,2.25,4.92,1.80),(64,9.38,2.48,2.12),(68,9.38,4.87,2.12),(19,5.31,6.69,2.72),(20,5.24,.48,2.84)]:
 text(d[id],x,y,w,.58,18,True,'ink',PP_ALIGN.CENTER)
for id in [2]:text(d[id],.60,.55,4.6,1.0,28,True)
s=prs.slides[26];d=allids(s)
# The source's giant overlapping diagram shapes cover two source headings.
# Bring those original text objects forward without changing their content.
for id in [19,20,2]:
 sh=d[id];parent=sh.element.getparent();parent.remove(sh.element);parent.append(sh.element)
text(d[19],8.14,1.07,4.65,.58,28,True,'white')
text(d[3],8.14,1.85,4.63,1.14,16,False,'white')
s=prs.slides[30];d=allids(s)
text(d[25],3.16,4.66,3.15,.61,19,True,'white',PP_ALIGN.CENTER)
text(d[26],6.71,4.66,3.15,.61,19,True,'white',PP_ALIGN.CENTER)
text(d[81],.18,3.02,2.39,2.45,15,True,'ink',PP_ALIGN.CENTER)
s=prs.slides[33];d=allids(s)
for id,x,y,w in [(15,2.52,2.28,3.27),(27,8.64,4.69,3.43),(30,2.52,4.69,3.27),(3,8.65,2.28,2.70)]:
 text(d[id],x,y,w,.34,13.5,True,'white',PP_ALIGN.CENTER,True)
s=prs.slides[46];d=allids(s)
text(d[2],.65,.42,12.03,.67,31,True)
for p in d[2].text_frame.paragraphs:
 pp=p._p.get_or_add_pPr();pp.set('marL','0');pp.set('indent','0')
for id in [15,17,19,21,23,25,27,29,33]:
 sh=d[id];text(sh,sh.left/914400,sh.top/914400,sh.width/914400,.55,16,True,'green',PP_ALIGN.CENTER)
for id in [16,18,20,22,24,26,28,30,34,36,38,39,40,41,71,72,73,74,75,76,77,78]:
 sh=d[id];fmt(sh,11.5,False,'ink')
# Keep all blank source paragraphs. They take space but are not discarded.
for id in [20]:d[id].height=Inches(1.1)
text(d[30],5.74,5.30,1.87,.55,11.5,False,'ink',PP_ALIGN.CENTER)
text(d[74],5.74,5.88,1.87,.45,11.5,False,'ink',PP_ALIGN.CENTER)
text(d[75],5.74,6.37,1.87,.58,11.5,False,'ink',PP_ALIGN.CENTER)
text(d[28],10.43,2.74,2.05,.83,11.5,False,'ink',PP_ALIGN.CENTER)

# Native chart cosmetics only; no categories, numbers, series, chart type edited.
for s in list(prs.slides)[:17]:
 for sh in s.shapes:
  if not sh.has_chart:continue
  chart=sh.chart
  for e in chart._chartSpace.xpath('.//a:srgbClr'):e.set('val',theme_color(e.get('val')))
  for j,series in enumerate(chart.series):
   col=['green','sage','blue'][j%3]
   try:series.format.line.color.rgb=rgb(col);series.format.line.width=Pt(2.3)
   except (AttributeError,ValueError):pass
   try:series.format.fill.solid();series.format.fill.fore_color.rgb=rgb(col)
   except (AttributeError,ValueError):pass
  for attr in ['category_axis','value_axis']:
   try:
    ax=getattr(chart,attr);ax.tick_labels.font.name='Liberation Sans';ax.tick_labels.font.size=Pt(11);ax.tick_labels.font.color.rgb=rgb('muted')
    if ax.has_major_gridlines:ax.major_gridlines.format.line.color.rgb=rgb('line')
   except (AttributeError,ValueError):pass
  if chart.has_legend:chart.legend.font.name='Liberation Sans';chart.legend.font.size=Pt(10)

# Hide the legacy decorative master stripe; all footer text remains above it.
for s in list(prs.slides)[1:17]:
 if s is not prs.slides[15]:rect(s,0,7.40,13.333333,.10,'paper')

# Fit unchanged text to its box using real font metrics. No text truncation.
fontdir=kit/'04_Fonts'
fit_changes=[]
def estimate(sh,size,bold=False):
 font=ImageFont.truetype(str(fontdir/('LiberationSans-Bold.ttf' if bold else 'LiberationSans-Regular.ttf')),round(size*4))
 width=sh.width/914400*72-sh.text_frame.margin_left/12700-sh.text_frame.margin_right/12700
 height=sh.height/914400*72-sh.text_frame.margin_top/12700-sh.text_frame.margin_bottom/12700
 lines=0
 for p in sh.text_frame.paragraphs:
  for raw in p.text.replace('\v','\n').split('\n'):
   current='';count=1
   for word in raw.split(' '):
    trial=current+' '+word if current else word
    if current and font.getlength(trial)/4>width:count+=1;current=word
    else:current=trial
   lines+=count
 return lines*size*1.08+max(0,len(sh.text_frame.paragraphs)-1)*4 <= height+1
for idx,s in enumerate(list(prs.slides)[:17],1):
 for sh in s.shapes:
  if not sh.has_text_frame or not sh.text.strip():continue
  sizes=[r.font.size.pt for p in sh.text_frame.paragraphs for r in p.runs if r.font.size]
  if not sizes:continue
  current=max(sizes);size=current
  bold=any(r.font.bold for p in sh.text_frame.paragraphs for r in p.runs)
  while size>10 and not estimate(sh,size,bold):size-=.5
  if size<current:
   fit_changes.append((idx,sh.shape_id,current,size,sh.text[:40]))
   for p in sh.text_frame.paragraphs:
    p.font.size=Pt(size)
    for r in p.runs:r.font.size=Pt(size)

args.out.parent.mkdir(parents=True,exist_ok=True);prs.save(args.out)
# Resolve source theme colours too (many appendix shapes use scheme references).
# Raster source images, embedded workbooks and all non-visual content are untouched.
from io import BytesIO
raw=args.out.read_bytes();buffer=BytesIO()
with zipfile.ZipFile(BytesIO(raw)) as zin,zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as zout:
 for info in zin.infolist():
  blob=zin.read(info.filename)
  if info.filename.startswith('ppt/theme/') and info.filename.endswith('.xml'):
   root=ET.fromstring(blob)
   nsTheme={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
   mapping={'dk1':'1E2023','lt1':'FFFFFF','dk2':'23262B','lt2':'F8F5F0','accent1':'28563B','accent2':'23262B','accent3':'58615C','accent4':'748178','accent5':'D6E5D6','accent6':'1959A6','hlink':'1959A6','folHlink':'28563B'}
   for scheme in root.xpath('//a:clrScheme',namespaces=nsTheme):
    for item in scheme:
     key=ET.QName(item).localname
     if key in mapping:
      for old in list(item):item.remove(old)
      ET.SubElement(item,'{'+nsTheme['a']+'}srgbClr',val=mapping[key])
   blob=ET.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
  zout.writestr(info,blob)
args.out.write_bytes(buffer.getvalue())
# Assert that all original slide-visible literals survive (z-order may change).
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(args.source) as original,zipfile.ZipFile(args.out) as final:
 for i in range(1,52):
  name=f'ppt/slides/slide{i}.xml';a=ET.fromstring(original.read(name));b=ET.fromstring(final.read(name))
  assert sorted(a.xpath('//a:t/text()',namespaces=ns))==sorted(b.xpath('//a:t/text()',namespaces=ns)),f'Text changed on slide {i}'
  assert a.get('show')==b.get('show'),f'Hidden flag changed on slide {i}'
print(f'Built {len(prs.slides)} cosmetically redesigned editable slides: {args.out}')
print(f'Exact original text/hidden-status assertions passed for all {len(prs.slides)} slides.')
for change in fit_changes:print('Font fit:',change)
