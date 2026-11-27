"""Content-preserving editorial polish for original appendix slides 18–51.

This module only changes styling/geometry, never literals, images or notes.
Noto Emoji is used only for original emoji runs in slide 22 (OFL rendering font).
"""
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

C={'paper':'F8F5F0','white':'FFFFFF','ink':'1E2023','green':'28563B','dark':'23262B','muted':'58615C','line':'D9DFD9','tint':'EAF0EB','pale':'D6E5D6','sage':'748178'}
def rgb(c):return RGBColor.from_string(C.get(c,c))
def walk(shapes):
 for sh in shapes:
  yield sh
  if sh.shape_type==6:yield from walk(sh.shapes)
def ids(s):return {sh.shape_id:sh for sh in walk(s.shapes)}
def at(sh,x,y,w,h):
 sh.left,sh.top,sh.width,sh.height=[Inches(z) for z in (x,y,w,h)];return sh
def fill(sh,c=None,line=None):
 if not hasattr(sh,'fill'):return sh
 if c:sh.fill.solid();sh.fill.fore_color.rgb=rgb(c)
 else:sh.fill.background()
 if hasattr(sh,'line'):
  if line:sh.line.color.rgb=rgb(line);sh.line.width=Pt(.6)
  else:sh.line.fill.background()
 return sh
def fmt(sh,size=18,bold=None,c='ink',align=PP_ALIGN.LEFT):
 if not sh.has_text_frame:return sh
 tf=sh.text_frame;tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0;tf.vertical_anchor=MSO_ANCHOR.TOP
 for p in tf.paragraphs:
  p.font.name='Liberation Sans';p.font.size=Pt(size);p.font.color.rgb=rgb(c);p.alignment=align;p.space_before=Pt(0);p.space_after=Pt(5);p.line_spacing=1.06
  if bold is not None:p.font.bold=bold
  for r in p.runs:
   if r.font.name not in ['Wingdings','Webdings','Segoe UI Emoji','Symbol']:r.font.name='Liberation Sans'
   r.font.size=Pt(size);r.font.color.rgb=rgb(c)
   if bold is not None:r.font.bold=bold
  for e in p._p.xpath('./a:endParaRPr | ./a:fld/a:rPr'):e.set('sz',str(int(size*100)))
 return sh
def text(sh,x,y,w,h,size=18,bold=None,c='ink',align=PP_ALIGN.LEFT):return fmt(at(sh,x,y,w,h),size,bold,c,align)
def rect(s,x,y,w,h,c='white',back=True):
 sh=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));fill(sh,c)
 if back:s.shapes._spTree.remove(sh.element);s.shapes._spTree.insert(2,sh.element)
 return sh
def panel(sh,x,y,w,h,c='white'):
 at(sh,x,y,w,h);fill(sh,c)
 for g in sh.element.xpath('.//a:prstGeom'):g.set('prst','rect')
 return sh
def detach(s,sh):
 sh.element.getparent().remove(sh.element);s.shapes._spTree.append(sh.element);return sh

def apply(prs,kit):
 # Consistent framing without adding a single new visible word or page number.
 for no,s in enumerate(prs.slides,1):
  if no<18 or no in [27,44,51]:continue
  dark=no in [45,46]
  s.background.fill.solid();s.background.fill.fore_color.rgb=rgb('dark' if dark else 'paper');s.element.set('showMasterSp','0')
  for sh in list(s.shapes):
   if sh.has_text_frame and sh.text.strip():
    if sh.top>Inches(6.95):
     # Preserve original footer words and page-number fields.
     if sh.left>Inches(9):text(sh,11.9,7.08,.77,.24,10,False,'pale' if dark else 'muted',PP_ALIGN.RIGHT)
     else:text(sh,.64,7.08,5.8,.24,10,False,'pale' if dark else 'muted')
    elif sh.is_placeholder and sh.top<Inches(.8) and sh.width>Inches(8):
     text(sh,.64,.48,12.05,.70,30 if len(sh.text)>58 else 34,True,'white' if dark else 'ink')
    elif sh.has_text_frame and sh.top>Inches(.8) and sh.top<Inches(1.1) and sh.width>Inches(8):
     text(sh,.66,1.25,11.9,.32,14,False,'pale' if dark else 'green')
   # Quiet the old corner tabs/stripes; these have no text or media.
   elif sh.shape_type==1 and not sh.element.xpath('.//a:blip') and sh.top<Inches(.4) and sh.height<Inches(1):fill(sh,None)
  rect(s,.64,.27,.54,.035,'pale' if dark else 'green')
  rect(s,.64,6.97,12.03,.009,'sage' if dark else 'line')

 # 18: airy four-column overview; source icons retain their native geometry.
 s=prs.slides[17];d=ids(s)
 for j,(panel_id,head,body) in enumerate([(7,24,33),(19,26,34),(22,17,35),(20,28,None)]):
  x=.67+j*3.05
  panel(d[panel_id],x,1.80,2.82,4.90,'white')
  text(d[head],x+.22,2.90,2.38,1.04,21,True,'green')
  if body:text(d[body],x+.16,4.20,2.55,1.56,15.8,False,'ink')
  rect(s,x+.22,4.02,.54,.025,'green',False)
 text(d[29],6.99,5.48,2.30,.70,15,False,'muted')
 for sh in s.shapes:
  if sh.shape_type==6:
   for child in walk(sh.shapes):
    if child.shape_type==5:fill(child,'green')

 # 19: remove ribbon styling but keep the original three concepts and icons.
 s=prs.slides[18];d=ids(s)
 for j,(head,body,pic) in enumerate([(23,37,72),(24,39,73),(25,41,74)]):
  x=.66+j*4.10
  rect(s,x,1.87,3.80,4.80,'white')
  for sh in list(s.shapes):
   if sh.shape_type==6:
    for child in walk(sh.shapes):
     if child.shape_type==5:fill(child,None)
  at(d[pic],x+.24,2.12,.76,.76)
  fill(d[head],None);text(d[head],x+.24,3.11,3.32,.57,24,True,'green')
  text(d[body],x+.25,4.00,3.28,2.35,17,False,'ink')

 # 21: an original title-only case separator becomes an intentional chapter page.
 s=prs.slides[20];d=ids(s);s.background.fill.fore_color.rgb=rgb('green')
 text(d[2],.83,2.65,11.65,1.20,62,True,'white')
 for sh in s.shapes:
  if sh.has_text_frame and sh.top>Inches(6.9):fmt(sh,10,False,'pale')
 rect(s,.86,2.20,1.10,.05,'pale',False)

 # 22: coherent three-method columns, original emoji rendered with Noto Emoji.
 s=prs.slides[21];d=ids(s)
 for j,(p,h,b,em) in enumerate([(7,24,33,4),(19,26,34,8),(22,17,35,21)]):
  x=.66+j*4.10;panel(d[p],x,1.88,3.80,4.78,'white')
  text(d[em],x+.24,2.16,.74,.70,29,False,'green')
  for par in d[em].text_frame.paragraphs:
   par.font.name='Noto Emoji'
   for run in par.runs:run.font.name='Noto Emoji'
  text(d[h],x+.24,3.14,3.32,.88,24,True,'green')
  text(d[b],x+.24,4.42,3.32,1.35,19,False,'ink')
 text(d[29],8.94,5.83,3.10,.61,15,False,'muted')

 # 23–24: free a useful title width while retaining all raster chart/device artwork.
 for no in [23,24]:
  s=prs.slides[no-1];d=ids(s)
  text(d[2],.64,.49,3.15,1.05,29,True)
  text(d[15],.72,2.30,2.90,2.80,20,False,'ink')
  fill(d[14],None)

 # 25: numerical comparison labels, no clipped square-metre units.
 s=prs.slides[24];d=ids(s)
 for no,x in [(25,6.55),(26,9.55)]:text(d[no],x,2.93,2.85,.63,22,True,'white',PP_ALIGN.CENTER)
 for no,x in [(4,6.55),(11,9.55)]:text(d[no],x,4.02,2.85,.98,24,True,'white',PP_ALIGN.CENTER)

 # 27: three original district comparisons as parallel flat panels rather than overlapping arcs.
 s=prs.slides[26];d=ids(s);s.background.fill.solid();s.background.fill.fore_color.rgb=rgb('paper');s.element.set('showMasterSp','0')
 for no in [485,486,488,493,494,495]:fill(d[no],None)
 for j,(h,b) in enumerate([(20,498),(19,3),(2,4)]):
  x=.66+j*4.10;rect(s,x,1.89,3.80,4.65,'green' if j==0 else 'white')
  text(d[h],x+.26,2.25,3.28,1.17,28,True,'white' if j==0 else 'green')
  text(d[b],x+.26,3.81,3.28,2.25,19,False,'white' if j==0 else 'ink')
 at(d[16],11.72,.58,.83,.83);fill(d[16],'green')
 text(d[487],11.9,7.08,.77,.24,10,False,'muted',PP_ALIGN.RIGHT)
 rect(s,.66,.68,8.1,.035,'green');rect(s,.64,6.97,12.03,.009,'line')

 # Sparse section slides now communicate an intentional chapter transition.
 for no,panel_id,head,body in [(28,7,24,33),(33,19,26,27),(38,31,17,32)]:
  s=prs.slides[no-1];d=ids(s)
  panel(d[panel_id],.66,1.88,12.02,4.82,'green')
  text(d[head],1.02,2.40,10.80,1.23,44,True,'white')
  text(d[body],1.04,4.52,10.75,1.26,27,False,'white')
  # Original freeform icon groups remain but use the white foreground on green.
  for sh in s.shapes:
   if sh.shape_type==6:
    at(sh,10.85,2.25,1.0,1.0)
    for child in walk(sh.shapes):
     if child.shape_type==5:fill(child,'white')

 # The ring's existing top label must not collide with the larger page header.
 s=prs.slides[28];d=ids(s);text(d[2],.64,.48,4.75,.95,28,True)

 # 30: well-spaced three-way competitor comparison; all original photographs retained.
 s=prs.slides[29];d=ids(s)
 for j,(h,b,pic) in enumerate([(4,18,3076),(6,15,3074),(8,9,17)]):
  x=.66+j*4.10;rect(s,x,1.88,3.80,4.82,'white')
  text(d[h],x+.22,3.95,3.36,.90,21,True,'green',PP_ALIGN.CENTER)
  text(d[b],x+.22,5.03,3.36,1.30,17,False,'ink',PP_ALIGN.CENTER)
  # Preserve source image ratio, align to a common visual centre.
  sh=d[pic];ratio=sh.width/sh.height;hh=1.45;ww=hh*ratio
  if ww>3.18:ww=3.18;hh=ww/ratio
  at(sh,x+(3.80-ww)/2,2.17+(1.45-hh)/2,ww,hh)
 for no in [27,28,29]:fill(d[no],'green')
 text(d[10],.64,.48,12.05,.70,34,True,'ink');text(d[11],.66,1.25,11.9,.32,14,False,'green')

 # 31: keep the source audience illustration, restore readable peripheral labels.
 s=prs.slides[30];d=ids(s)
 text(d[81],.64,2.85,2.18,2.75,17,True,'ink',PP_ALIGN.LEFT)
 text(d[83],10.59,2.85,2.10,2.75,17,True,'ink',PP_ALIGN.LEFT)

 # 34: a quiet 2x2 value-proposition matrix replaces the winding decorative path.
 s=prs.slides[33];d=ids(s)
 for sh in list(s.shapes):
  if sh.shape_type==6:
   for child in walk(sh.shapes):
    fill(child,None)
    if hasattr(child,'line'):child.line.fill.background()
 for j,(head,body,dot) in enumerate([(15,32,14),(3,34,17),(30,21,29),(27,37,26)]):
  x=.66+(j%2)*6.15;y=1.91+(j//2)*2.38
  rect(s,x,y,5.86,2.14,'white')
  panel(d[dot],x+.25,y+.27,.11,.38,'green')
  fill(d[head],None);text(d[head],x+.52,y+.24,5.0,.52,21,True,'green')
  text(d[body],x+.27,y+.94,5.27,1.20,16.5,False,'ink')
  # The source contains blank paragraphs between bullets: retain them but reduce their leading.
  if body==37:
   for p in d[body].text_frame.paragraphs:
    p.space_after=Pt(0);p.line_spacing=.90
    if not p.text:p.font.size=Pt(3)

 # 35: original six-step journey in a readable 3x2 native-object grid.
 s=prs.slides[34];d=ids(s)
 steps=[(63,65,64,78),(58,59,60,76),(51,52,53,74),(46,47,48,72),(41,42,43,70),(33,36,38,68)]
 for j,(arrow,head,body,pic) in enumerate(steps):
  x=.66+j%3*4.10;y=1.87+j//3*2.42
  for no in [arrow,head,body]:detach(s,d[no])
  fill(d[arrow],'pale');at(d[arrow],x,y,3.80,.58)
  at(d[pic],x+.20,y+.78,.62,.62)
  text(d[head],x+.99,y+.77,2.57,.82,18,True,'green')
  text(d[body],x+.20,y+1.59,3.40,.78,13.2,False,'ink')
  if j==0:rect(s,x+.14,y+.72,.74,.74,'green')
  for p in d[body].text_frame.paragraphs:
   p.space_after=Pt(0);p.line_spacing=.98
   if not p.text:p.font.size=Pt(3)

 # 36: retain source image; give the one original argument more comfortable leading.
 s=prs.slides[35];d=ids(s)
 text(d[3],7.72,.72,4.93,.70,34,True)
 text(d[6],7.72,2.30,4.94,3.81,30,True)

 # 37: two crisp accounting panels, faithful source content with readable leading.
 s=prs.slides[36];d=ids(s)
 panel(d[11],.66,1.89,5.85,4.79,'white');panel(d[10],6.82,1.89,5.85,4.79,'tint')
 text(d[29],.97,2.27,5.23,.60,28,True,'green');text(d[33],7.13,2.27,5.23,.60,28,True,'green')
 text(d[30],.98,3.13,5.17,3.12,20,False,'ink');text(d[5],7.14,3.13,5.17,3.12,18,False,'ink')
 for no in [44,45]:fill(d[no],None)
 for sh in walk(s.shapes):
  if sh.shape_type==5:fill(sh,'green')
 # Retain and align every original icon within its corresponding column.
 at(d[52],4.70,2.25,.54,.54);at(d[60],5.51,2.25,.54,.54);at(d[53],11.69,2.25,.54,.54)

 # The original brochure frame begins at1.42in; keep its subtitle clear of the rule.
 s=prs.slides[42];d=ids(s);text(d[5],.66,1.12,5.00,.24,12.5,False,'green')

 # 45/46: exact source dark closing text, with measured title and better image alignment.
 for no in [45,46]:
  s=prs.slides[no-1];d=ids(s)
  text(d[2],.72,.65,11.75,.70,30,True,'white')
  text(d[8],8.12 if no==45 else 7.29,3.01,4.30 if no==45 else 5.12,1.15,58,True,'white')

 # 47: underlying native text is dense; thin column rules support scanning without squeezing it.
 s=prs.slides[46];d=ids(s)
 for x in [3.14,5.50,7.87,10.28]:rect(s,x,1.79,.009,4.90,'line')
 # Reserve a clear footer strip; the original lower cards extended below it.
 panel(d[12],3.31,4.55,2.012,2.20,'white')
 at(d[47],3.99,4.20,.65,.65);at(d[57],4.12,4.33,.39,.39)
 text(d[19],3.377,4.95,1.875,.34,16,True,'green',PP_ALIGN.CENTER)
 text(d[20],3.413,5.38,1.875,1.34,12.4,False,'ink')
 for p in d[20].text_frame.paragraphs:p.space_after=Pt(0)
 panel(d[8],7.994,4.55,2.012,2.20,'white')
 at(d[48],8.68,4.20,.65,.65);at(d[79],8.81,4.37,.39,.30)
 text(d[25],8.064,4.95,1.875,.34,16,True,'green',PP_ALIGN.CENTER)
 text(d[26],8.064,5.40,1.875,.57,12.4,False,'ink')
 text(d[76],8.064,6.07,1.875,.65,12.4,False,'ink')
 text(d[29],5.729,4.79,1.875,.38,16,True,'green',PP_ALIGN.CENTER)
 for no,y,h in [(30,5.20,.60),(74,5.86,.43),(75,6.34,.57)]:
  text(d[no],5.74,y,1.87,h,12,False,'ink',PP_ALIGN.CENTER)
  for p in d[no].text_frame.paragraphs:p.space_after=Pt(0)
 # A final z-order pass keeps source footer text above all cosmetic backgrounds.
 for no in [3,4]:detach(s,d[no])

 # 48: retain every multiline segment literally, increase breathing room and remove yellow blocks.
 s=prs.slides[47];d=ids(s)
 for j,no in enumerate([46,48,47,49]):
  x=.66+(j%2)*3.91;y=1.86+(j//2)*2.42
  fill(d[no],'white');text(d[no],x,y,3.65,2.20,15.0,False,'ink')
  d[no].text_frame.margin_left=d[no].text_frame.margin_right=Inches(.16);d[no].text_frame.margin_top=Inches(.17)
  for k,p in enumerate(d[no].text_frame.paragraphs):
   p.space_after=Pt(0);p.line_spacing=1.00
   if k==0:
    p.font.bold=True;p.font.color.rgb=rgb('green')
    for r in p.runs:r.font.bold=True;r.font.color.rgb=rgb('green')
   if not p.text:p.font.size=Pt(2)
 at(d[50],8.56,3.25,.39,.85);fill(d[50],'green')
 for j,no in enumerate([52,53,54,55]):
  fill(d[no],'tint');text(d[no],9.22,1.86+j*1.21,3.46,1.11,14.1,False,'ink')
  d[no].text_frame.margin_left=d[no].text_frame.margin_right=Inches(.15);d[no].text_frame.margin_top=Inches(.10)
  for p in d[no].text_frame.paragraphs:p.space_after=Pt(0);p.line_spacing=1.00

 # 49: theory cards retain source photos/icon fills; source body becomes readable.
 s=prs.slides[48];d=ids(s)
 for j,(p,h,b,pic) in enumerate([(18,6,37,20),(35,9,10,28),(51,12,13,31),(67,15,16,40)]):
  x=.66+j*3.05;panel(d[p],x,1.88,2.82,4.82,'white')
  at(d[pic],x+.64,2.10,1.54,1.54)
  text(d[h],x+.19,3.91,2.44,.70,19,True,'green',PP_ALIGN.CENTER)
  text(d[b],x+.22,4.83,2.38,1.62,13.0,False,'ink')
  for p in d[b].text_frame.paragraphs:p.space_after=Pt(4)

 # 50: retain original proportions and content while fixing clipped channel labels.
 s=prs.slides[49];d=ids(s)
 for no in [1409,1415,1421,1430]:
  sh=d[no];sh.width=Inches(2.05);sh.height=Inches(.45);fmt(sh,18,True,'white',PP_ALIGN.CENTER)
 for no in [1410,1416,1422,1427]:fmt(d[no],20,True,'white',PP_ALIGN.CENTER)
 text(d[1411],.80,2.83,2.00,.68,14.0,False,'ink',PP_ALIGN.CENTER)
 d[1420].line.fill.background() # Remove the inherited red outline, not the column.
 # Full-slide backing masks inherited decorative master stripes/SGS logos only.
 # Native source pictures, labels and footer placeholders remain above it.
 for no,s in enumerate(prs.slides,1):
  if no>=18 and no not in [44,51]:rect(s,0,0,13.333333,7.5,'green' if no==21 else ('dark' if no in [45,46] else 'paper'))
 return prs
