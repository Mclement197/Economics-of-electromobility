"""Editorial 2026-11-27 styling pass. Original objects remain editable and exact."""
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

PALETTE={'green':'28563B','ink':'1E2023','dark':'23262B','paper':'F8F5F0','white':'FFFFFF','tint':'EAF0EB','line':'D9DFD9','muted':'58615C','sage':'748178','pale':'D6E5D6','blue':'1959A6'}
def rgb(c): return RGBColor.from_string(PALETTE.get(c,c))
def at(sh,x,y,w,h):
 sh.left=Inches(x);sh.top=Inches(y);sh.width=Inches(w);sh.height=Inches(h);return sh
def fill(sh,c,line=None):
 if hasattr(sh,'fill'):
  if c is None:sh.fill.background()
  else:sh.fill.solid();sh.fill.fore_color.rgb=rgb(c)
 if hasattr(sh,'line'):
  if line:sh.line.color.rgb=rgb(line);sh.line.width=Pt(.75)
  else:sh.line.fill.background()
 return sh
def fmt(sh,size=20,bold=False,color='ink',align=PP_ALIGN.LEFT,center=False):
 if not sh.has_text_frame:return sh
 tf=sh.text_frame;tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0;tf.vertical_anchor=MSO_ANCHOR.MIDDLE if center else MSO_ANCHOR.TOP
 for p in tf.paragraphs:
  p.alignment=align;p.space_before=Pt(0);p.space_after=Pt(4);p.line_spacing=1.08
  p.font.name='Liberation Sans';p.font.size=Pt(size);p.font.color.rgb=rgb(color);p.font.bold=bold
  for r in p.runs:r.font.name='Liberation Sans';r.font.size=Pt(size);r.font.color.rgb=rgb(color);r.font.bold=bold
  for e in p._p.xpath('./a:endParaRPr | ./a:fld/a:rPr'):e.set('sz',str(round(size*100)))
 return sh
def text(sh,x,y,w,h,size=20,bold=False,color='ink',align=PP_ALIGN.LEFT,center=False):return fmt(at(sh,x,y,w,h),size,bold,color,align,center)
def panel(sh,x,y,w,h,c='paper'):
 at(sh,x,y,w,h);fill(sh,c)
 for e in sh.element.xpath('.//a:prstGeom'):e.set('prst','rect')
 return sh
def rect(slide,x,y,w,h,c='green',back=False):
 sh=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));fill(sh,c)
 if back:
  tree=slide.shapes._spTree;tree.remove(sh.element);tree.insert(2,sh.element)
 return sh
def front(sh):
 parent=sh.element.getparent();parent.remove(sh.element);parent.append(sh.element)
def bg(s,c='paper'):
 s.background.fill.solid();s.background.fill.fore_color.rgb=rgb(c)
def ids(s):return {x.shape_id:x for x in s.shapes}

def apply(prs,kit):
 # Quiet editorial folio. All original titles/footer strings are kept as native text.
 for n,s in enumerate(list(prs.slides)[:17],1):
  d=ids(s)
  if n not in [1,16]:
   text(d[2],.70,.60,11.95,.72,34 if len(d[2].text)<43 else 30,True)
   if 32 in d and d[32].has_text_frame and d[32].text.strip():text(d[32],.73,1.40,11.90,.28,13,False,'muted')
   # Existing added top dash becomes a quieter vertical brand keyline.
   for sh in s.shapes:
    if not sh.has_text_frame or not sh.text:
     if abs(sh.left/Inches(1)-.65)<.02 and abs(sh.top/Inches(1)-.30)<.02:
      at(sh,.70,.28,.70,.025)

 # 01 — architectural photograph, deep-green editorial cover.
 s=prs.slides[0];d=ids(s);bg(s,'green')
 at(d[2],5.68,0,7.6533,7.5);d[2].crop_left=.22;d[2].crop_right=.17
 text(d[27],.72,2.22,5.12,1.05,62,True,'white')
 text(d[32],.76,5.63,4.35,1.05,17,False,'pale')
 fill(d[5],'green')
 # Decorative symbol and rule retain the existing supplied white brand artwork.
 for sh in s.shapes:
  if sh.shape_id not in d:continue
  if sh.shape_type==13 and sh.shape_id!=2:at(sh,.76,.64,.62,.62)
 rect(s,.76,4.16,3.92,.012,'sage')

 # 02 — rhythmic agenda, no cards; large indices and open whitespace.
 s=prs.slides[1];d=ids(s);text(d[2],.70,.58,11.9,.8,44,True)
 for j,base in enumerate([32,37,42,47,52,57]):
  x=.72+(j%2)*6.16;y=1.99+(j//2)*1.44
  panel(d[base],x,y,5.75,1.22,'paper');fill(d[base+1],None)
  text(d[base+2],x,y,.86,.70,43,True,'green')
  text(d[base+3],x+1.10,y+.03,4.62,.56,23 if j==2 else 26,True)
  text(d[base+4],x+1.10,y+.70,4.60,.42,16,False,'muted')
 text(d[62],.73,6.58,10,.25,11,False,'muted')

 # 03 — consistent portrait row, open biographies and fine rules.
 s=prs.slides[2];d=ids(s)
 for j,entry in enumerate([(33,34,35,36,37,38,39),(40,41,42,43,44,45,46),(47,None,None,50,51,52,53),(54,55,56,57,58,59,60),(61,62,63,64,65,66,67)]):
  x=.70+j*2.46;a,b,c,name,rule,label,num=entry
  panel(d[a],x,1.98,2.18,4.60,'paper')
  if b:panel(d[b],x,2.05,2.18,2.18,'tint')
  if c:text(d[c],x,4.34,2.18,.15,8,False,'muted')
  text(d[name],x,4.62,2.15,.78,21,True)
  panel(d[rule],x,5.63,2.15,.012,'line')
  text(d[label],x,5.88,2.12,.22,11,False,'muted')
  text(d[num],x,6.20,2.12,.25,15,False,'muted')
 for sid,j in [(7,1),(4,2),(3,4)]:at(d[sid],.70+j*2.46,2.05,2.18,2.18)

 # 04 — proposition as a spacious lead, native model taxonomy aligned beneath.
 s=prs.slides[3];d=ids(s)
 panel(d[13],.70,1.88,11.94,1.42,'tint')
 text(d[14],.95,2.09,11.4,.98,21,False)
 for j,sid in enumerate([15,17,18,19,20,21]):
  y=3.65+j*.48;panel(d[sid],.70,y,3.14,.40,'paper');fmt(d[sid],14,True,'green',center=True)
 for sid,row,col in [(22,0,0),(23,0,1),(25,1,0),(26,1,1),(27,1,2),(28,2,0),(29,2,1),(30,2,2)]:
  panel(d[sid],4.1+col*2.9,3.65+row*.48,2.68,.40,'white');fmt(d[sid],15,False,'ink',PP_ALIGN.CENTER,True)
 for j in range(6):rect(s,.70,4.10+j*.48,11.94,.008,'line')

 # 05 — one dominant insight, three supporting rows and an open rationale band.
 s=prs.slides[4];d=ids(s)
 panel(d[39],.70,1.99,4.10,2.82,'green')
 text(d[40],.98,2.20,3.52,1.03,70,True,'white')
 text(d[41],1.01,3.47,3.44,1.03,20,False,'white')
 for j,base in enumerate([33,36,42]):
  y=2.04+j*.96;panel(d[base],5.15,y,7.49,.84,'paper')
  text(d[base+1],5.15,y,3.12,.65,34,True,'green')
  text(d[base+2],8.45,y+.03,4.08,.77,17,False)
  if j<2:rect(s,5.15,y+.85,7.48,.012,'line')
 panel(d[45],.70,5.00,11.94,1.55,'tint');text(d[46],.94,5.16,11.42,.29,17,True,'green')
 text(d[47],.94,5.58,5.51,.92,13,False);text(d[48],6.89,5.58,5.49,.92,13,False)

 # 06 — clearer comparative bars and a typographic demand statement.
 s=prs.slides[5];d=ids(s)
 panel(d[33],.70,2.00,7.25,4.46,'paper');text(d[34],.70,2.02,7.13,.39,23,True)
 for j,(label,track,bar,value) in enumerate([(35,36,37,38),(39,40,41,42),(43,44,45,46)]):
  y=2.79+j*1.12;text(d[label],.70,y,5.37,.50,16,False)
  panel(d[track],.70,y+.61,5.32,.12,'line');panel(d[bar],.70,y+.61,[.745,3.2452,4.4688][j],.12,'green')
  text(d[value],6.20,y+.16,1.70,.59,28,True,'green',PP_ALIGN.RIGHT)
 text(d[47],.70,6.24,7.12,.26,11,False,'muted')
 panel(d[48],8.30,1.98,4.34,2.75,'green')
 text(d[49],8.59,2.21,3.76,.90,59,True,'white');text(d[50],8.59,3.31,3.76,1.08,18,False,'white')
 panel(d[51],8.30,4.95,4.34,1.51,'paper')
 text(d[52],8.30,4.99,4.31,.56,35,True,'green');text(d[53],8.30,5.71,4.31,.69,15,False)

 # 07 — clear linked market stages, matching revenue and an explicit assumptions rail.
 s=prs.slides[6];d=ids(s)
 for j,base in enumerate([33,41,49]):
  y=2.00+j*1.44;w=6.30-j*.52;dark=j==2
  panel(d[base],.70,y,w,1.23,'green' if dark else 'tint')
  text(d[base+1],.92,y+.12,w-.44,.23,13,True,'white' if dark else 'green')
  text(d[base+2],.92,y+.47,w-.44,.42,27 if j==0 else 25,True,'white' if dark else 'ink')
  text(d[base+3],.92,y+.95,w-.44,.24,10.5,False,'white' if dark else 'muted')
  rev=[37,45,53][j];panel(d[rev],7.30,y,2.54,1.23,'paper')
  text(d[rev+1],7.30,y+.16,2.54,.24,11,False,'muted');text(d[rev+2],7.30,y+.60,2.54,.42,24,True,'green')
  at(d[rev+3],7.02,y+.62,.23,0)
 panel(d[57],10.14,2.00,2.50,4.11,'paper');text(d[58],10.14,2.14,2.50,.31,18,True,'green')
 text(d[59],10.14,2.85,2.50,3.05,15,False,'muted')
 rect(s,9.97,2.00,.009,4.11,'line')

 # 08 — phase bands and spacious, crisp timeline cards using only original text.
 s=prs.slides[7];d=ids(s)
 panel(d[33],.70,1.99,7.45,.76,'green');panel(d[34],8.34,1.99,4.30,.76,'dark')
 text(d[35],.91,2.10,7.02,.24,14.5,True,'white');text(d[36],.91,2.43,7.02,.20,11,False,'white')
 text(d[37],8.54,2.10,3.90,.26,13,True,'white');text(d[38],8.54,2.42,3.90,.22,11,False,'white')
 for j,base in enumerate(range(40,72,4)):
  x=.70+(j%4)*3.07;y=2.96+(j//4)*1.70
  text(d[base],x,y,2.77,.22,13,True,'green');panel(d[base+1],x,y+.31,2.76,.012,'line')
  text(d[base+2],x,y+.43,2.77,.36,20,True);text(d[base+3],x,y+.88,2.77,.72,11.5,False,'muted')
 panel(d[72],.70,6.34,11.94,.34,'paper');text(d[73],.70,6.34,11.94,.34,10.5,False,'muted')

 # 09 — preserve and scale the source garage diagram under the editorial header.
 s=prs.slides[8];d=ids(s)
 for sid in range(33,73):
  if sid not in d:continue
  sh=d[sid];sh.top=Inches(2.0+(sh.top/Inches(1)-1.55)*.88);sh.height=round(sh.height*.88)
 fill(d[33],'paper')
 d[72].line.color.rgb=rgb('muted');d[72].line.width=Pt(1.5)
 for back,bar,head,body,y in [(73,74,75,76,2.0),(77,78,79,80,3.5),(81,82,83,84,5.0)]:
  panel(d[back],8.1,y,4.54,1.43,'paper');panel(d[bar],8.1,y,.05,1.43,'green')
  text(d[head],8.57,y+.03,3.78,.62,20,True,'green')
  text(d[body],8.57,y+.68,3.78,.75,15.5,False)

 # 10 — open numbered columns; not three heavy cards.
 s=prs.slides[9];d=ids(s)
 for j,base in enumerate([33,38,43]):
  x=.70+j*4.10;panel(d[base],x,1.99,3.74,4.47,'paper');fill(d[base+1],None)
  text(d[base+2],x,1.99,1.06,.81,48,True,'green')
  text(d[base+3],x,3.05,3.56,.88,27,True)
  text(d[base+4],x,4.27,3.52,1.95,19,False)
  rect(s,x,3.98,3.53,.012,'line')

 # 11 — service promises left, two clearly separated payer lanes right.
 s=prs.slides[10];d=ids(s)
 panel(d[33],.70,1.99,5.18,4.48,'paper');text(d[34],.70,2.00,5.16,.41,23,True)
 for j,(head,body) in enumerate([(35,36),(37,38),(39,40)]):
  y=[2.77,4.13,5.36][j];text(d[head],.70,y,5.08,.30,16,True,'green');text(d[body],.70,y+.39,4.99,.80,15.5,False)
 panel(d[41],6.21,1.99,6.43,4.48,'tint');text(d[42],6.50,2.22,5.84,.39,23,True)
 for j,(box,txt) in enumerate([(43,44),(45,46),(47,48)]):
  x=6.50+j*2.00;panel(d[box],x,3.04,1.78,.77,'green' if j==1 else 'white');text(d[txt],x+.05,3.04,1.68,.77,17,True,'white' if j==1 else 'green',PP_ALIGN.CENTER,True)
 for sid,x in [(49,8.31),(50,10.31)]:at(d[sid],x,3.43,.17,0)
 text(d[51],6.50,4.24,2.68,1.12,17,False);text(d[52],9.57,4.24,2.68,1.12,17,False)
 panel(d[53],6.50,5.78,5.84,.48,'white');text(d[54],6.66,5.86,5.52,.32,12.5,False)

 # 12 — clean assumption ledger beside the unchanged building illustration.
 s=prs.slides[11];d=ids(s)
 for sid in range(33,78):
  if sid not in d:continue
  sh=d[sid];sh.top=Inches(2.0+(sh.top/Inches(1)-1.55)*.88);sh.height=round(sh.height*.88)
 fill(d[33],'tint');panel(d[78],6.4,2.0,6.24,4.40,'paper')
 text(d[79],6.80,2.02,5.6,.42,25,True)
 for j,(label,value) in enumerate([(80,81),(83,84),(86,87),(89,90),(92,93),(95,96),(98,99)]):
  y=2.71+j*.52;text(d[label],6.80,y,3.88,.38,14.5,False);text(d[value],10.77,y,1.87,.38,20,True,'green',PP_ALIGN.RIGHT)
  if j<6:at(d[label+2],6.80,y+.43,5.84,0);d[label+2].line.color.rgb=rgb('line')
 text(d[76],4.40,2.50,1.68,.90,18,True,'green',PP_ALIGN.CENTER);text(d[77],4.40,5.45,1.68,.90,18,True,'green',PP_ALIGN.CENTER)

 # 13 — graph is the hero; lean process sidebar, strong source-result band.
 s=prs.slides[12];d=ids(s)
 panel(d[33],.70,2.00,7.62,4.42,'white');at(d[34],.79,2.11,7.43,4.13)
 for j,(box,num,title,body) in enumerate([(35,36,37,38),(39,40,41,42),(43,44,45,46),(47,48,49,50)]):
  y=2.04+j*.88+(.12 if j==3 else 0);fill(d[box],None);text(d[num],8.64,y,.53,.45,23,True,'green');text(d[title],9.37,y,3.25,.31,21,True);text(d[body],9.37,y+.39,3.25,.47,14.5,False)
 panel(d[51],8.64,5.82,4.00,.60,'green');text(d[52],8.83,5.89,3.61,.46,13.5,False,'white')

 # 14 — finance hero band, restrained statement and enlarged native cash chart.
 s=prs.slides[13];d=ids(s)
 for j,base in enumerate([33,36,39]):
  x=.70+j*4.08;panel(d[base],x,1.99,3.79,1.24,'green' if j==1 else 'tint')
  text(d[base+1],x+.22,2.17,3.35,.58,36,True,'white' if j==1 else 'green')
  text(d[base+2],x+.22,2.85,3.35,.24,14,False,'white' if j==1 else 'ink')
 panel(d[42],.70,3.59,5.30,2.94,'paper')
 for sid,y,size,bold in [(43,3.58,16,True),(44,4.00,14,False),(45,4.00,15,True),(46,4.40,14,False),(47,4.40,15,True),(48,4.91,16,True),(49,5.31,14,False),(50,5.31,15,True),(51,5.71,14,False),(52,5.71,15,True),(53,6.11,14,False),(54,6.11,15,True)]:
  val=sid in [45,47,50,52,54];text(d[sid],4.55 if val else .70,y,1.45 if val else (5.3 if sid in [43,48] else 3.72),.32,size,bold,'green' if sid in [43,48] else 'ink',PP_ALIGN.RIGHT if val else PP_ALIGN.LEFT)
 panel(d[55],6.40,3.53,6.24,3.00,'white');text(d[56],6.60,3.67,5.84,.42,21,True)
 at(d[57],6.51,4.10,6.03,2.16);text(d[58],6.61,6.30,5.83,.18,11,False,'muted',PP_ALIGN.CENTER)

 # 15 — landlord net result emphasized, sensitivity chart opens up.
 s=prs.slides[14];d=ids(s)
 panel(d[33],.70,1.99,5.45,2.47,'tint');text(d[34],.96,2.21,4.91,.36,23,True)
 for label,value,y in [(35,36,2.90),(37,38,3.33)]:text(d[label],.96,y,2.93,.28,14,False);text(d[value],4.00,y,1.87,.28,16,True,'green',PP_ALIGN.RIGHT)
 at(d[39],.96,3.75,4.93,0);text(d[40],.96,3.98,2.42,.30,13,False);text(d[41],3.20,3.89,2.67,.50,27,True,'green',PP_ALIGN.RIGHT)
 panel(d[42],.70,4.74,5.45,1.79,'paper');text(d[43],.70,4.78,5.30,.35,23,True);text(d[44],.70,5.28,5.32,1.22,14,False)
 panel(d[45],6.53,1.99,6.11,4.54,'white');text(d[46],6.77,2.24,5.64,.60,23,True);at(d[47],6.71,2.99,5.75,2.85);text(d[48],6.77,6.00,5.64,.38,13.5,False,'muted')

 # 16 — typographic closing with confident scale and generous whitespace.
 s=prs.slides[15];d=ids(s);bg(s,'green');fill(d[2],'green')
 text(d[5],.78,2.05,10.9,1.50,104,True,'white');text(d[6],.84,4.25,10.8,.64,32,False,'white');text(d[7],.84,5.29,10.8,.35,17,False,'pale')
 panel(d[3],11.55,.70,.75,.025,'pale');panel(d[4],.84,6.49,11.66,.012,'sage')

 # 17 — source index, calm rules and original full URLs; dense by necessity.
 s=prs.slides[16];d=ids(s)
 for j in range(12):
  label=33+j*2;body=label+1;col=j//6;row=j%6;x=.70+col*6.18;y=2.01+row*.67
  text(d[label],x,y,1.72,.53,11.5,True,'green');text(d[body],x+1.84,y,4.00,.56,11.3,False)
 panel(d[57],.70,6.35,11.94,.32,'paper');text(d[58],.70,6.36,11.94,.29,10.5,False,'muted')

 # Avoid an Impress rendering defect that mirrors negative bars above zero.
 # This is a series colour-style flag only; cached values and workbooks stay exact.
 for sh in prs.slides[13].shapes:
  if sh.has_chart:
   for element in sh.chart._chartSpace.xpath('.//c:invertIfNegative'):
    element.set('val','0')

 # Native data stays untouched; chart visual hierarchy matches the typography.
 for s in list(prs.slides)[:17]:
  for sh in s.shapes:
   if not sh.has_chart:continue
   ch=sh.chart
   for attr in ['category_axis','value_axis']:
    try:
     ax=getattr(ch,attr);ax.tick_labels.font.name='Liberation Sans';ax.tick_labels.font.size=Pt(11.5);ax.tick_labels.font.color.rgb=rgb('muted')
     if ax.has_major_gridlines:ax.major_gridlines.format.line.color.rgb=rgb('line');ax.major_gridlines.format.line.width=Pt(.5)
    except (ValueError,AttributeError):pass
   if ch.has_legend:ch.legend.font.name='Liberation Sans';ch.legend.font.size=Pt(10)
