#!/usr/bin/env python3
"""Build native editable PowerPoint from the shared website slide content.

Requires python-pptx>=1.0.2 and Pillow. Keeps supplied brand starter unchanged.
PDF is exported separately from the website's print layout.
"""
import argparse, json
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.chart.data import CategoryChartData
from PIL import ImageFont

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--data',type=Path,default=ROOT/'website-src/presentation-data.json')
parser.add_argument('--out',type=Path,default=ROOT/'website-src/downloads/VoltoShare-Praesentation.pptx')
args=parser.parse_args()
data=json.loads(args.data.read_text())
kit=ROOT/'design/brand-kit'
prs=Presentation(kit/'06_Presentation/VoltoShare_Presentation_Starter.pptx')
# Reuse the supplied starter's masters/layouts, replace only its sample slide list.
for sid in list(prs.slides._sldIdLst):
    prs.part.drop_rel(sid.rId)
    prs.slides._sldIdLst.remove(sid)
prs.slide_width=Inches(13.333333)
prs.slide_height=Inches(7.5)
FONT='Liberation Sans'
C={'green':'28563B','ink':'1E2023','dark':'23262B','canvas':'F8F5F0','white':'FFFFFF','tint':'EAF0EB','border':'D9DFD9','muted':'58615C','blue':'1959A6','red':'B42318'}
def rgb(key):return RGBColor.from_string(C.get(key,key))
def box(s,x,y,w,h,color='white',line=None,radius=False):
    z=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    z.fill.solid();z.fill.fore_color.rgb=rgb(color)
    if line:z.line.color.rgb=rgb(line);z.line.width=Pt(.7)
    else:z.line.fill.background()
    if radius:z.adjustments[0]=.08
    return z

def text(s,content,x,y,w,h,size=22,bold=False,color='ink',align=None):
    z=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=z.text_frame
    tf.clear();tf.word_wrap=True
    tf.margin_left=tf.margin_right=0;tf.margin_top=tf.margin_bottom=0
    for i,line in enumerate(str(content).split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.text=line;p.font.name=FONT;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color)
        p.space_after=Pt(5);p.line_spacing=1.08
        if align is not None:p.alignment=align
    return z

def card(s,item,x,y,w,h,size=20,dark=False):
    box(s,x,y,w,h,'green' if dark else 'white',None if dark else 'border',True)
    title=item['title'];body=item.get('body') or '\n'.join('• '+t for t in item.get('items',[]))
    f=ImageFont.truetype(str(kit/'04_Fonts/LiberationSans-Bold.ttf'),size=size*4)
    titleh=.65 if f.getlength(title)/4 > (w-.46)*72 else .38
    text(s,title,x+.23,y+.23,w-.46,titleh,size,True,'white' if dark else 'green')
    text(s,body,x+.23,y+.28+titleh,w-.46,h-titleh-.50,size-1,False,'white' if dark else 'ink')

def stats(s,items,y=1.8,h=1.35):
    gap=.22;w=(12.13-gap*(len(items)-1))/len(items)
    for i,it in enumerate(items):
        x=.6+i*(w+gap);box(s,x,y,w,h,'tint',None,True)
        text(s,it['value'],x+.22,y+.18,w-.44,.5,31 if len(it['value'])<12 else 28,True,'green')
        text(s,it['label'],x+.22,y+.79,w-.44,h-.84,15)

def table(s,rows,x,y,w,h,header=False,colwidths=None):
    ncols=max(len(r) for r in rows)
    shape=s.shapes.add_table(len(rows),ncols,Inches(x),Inches(y),Inches(w),Inches(h));t=shape.table
    if colwidths:
        for c,frac in zip(t.columns,colwidths):c.width=Inches(w*frac)
    for i,row in enumerate(rows):
        for j in range(ncols):
            cell=t.cell(i,j);cell.text=str(row[j]) if j<len(row) else ''
            cell.fill.solid();cell.fill.fore_color.rgb=rgb('green' if header and i==0 else ('tint' if i%2==0 else 'white'))
            cell.margin_top=Inches(.09);cell.margin_bottom=Inches(.06);cell.margin_left=Inches(.14);cell.margin_right=Inches(.14)
            cell.vertical_anchor=MSO_ANCHOR.MIDDLE
            for p in cell.text_frame.paragraphs:
                p.font.name=FONT;p.font.size=Pt(16 if ncols>2 else 17)
                p.font.bold=(j==0 or header and i==0);p.font.color.rgb=rgb('white' if header and i==0 else 'ink')
    return shape

def chart(s,c,x,y,w,h):
    cd=CategoryChartData();cd.categories=c['categories']
    for series in c['series']:cd.add_series(series['name'],series['values'])
    ch=s.shapes.add_chart(XL_CHART_TYPE.LINE,Inches(x),Inches(y),Inches(w),Inches(h),cd).chart
    ch.has_legend=len(c['series'])>1
    if ch.has_legend:
        ch.legend.position=XL_LEGEND_POSITION.BOTTOM;ch.legend.include_in_layout=False
        ch.legend.font.name=FONT;ch.legend.font.size=Pt(11)
    ch.has_title=False
    for ax in [ch.value_axis,ch.category_axis]:
        ax.tick_labels.font.name=FONT;ax.tick_labels.font.size=Pt(11);ax.tick_labels.font.color.rgb=rgb('muted')
    ch.value_axis.has_major_gridlines=True
    ch.value_axis.tick_labels.number_format='#,##0'
    for i,series in enumerate(ch.series):
        series.format.line.color.rgb=rgb(['green','blue','muted'][i%3]);series.format.line.width=Pt(2.4)
    return ch

for index,d in enumerate(data['slides'],1):
    s=prs.slides.add_slide(prs.slide_layouts[5]);dark=d['kind'] in ['title','closing']
    s.background.fill.solid();s.background.fill.fore_color.rgb=rgb('dark' if dark else 'canvas')
    # Full surface prevents hidden source-template decorations from leaking through.
    box(s,0,0,13.333333,7.5,'dark' if dark else 'canvas')
    box(s,.6,.48,.42,.05,'white' if dark else 'green')
    text(s,d['kicker'].upper(),1.14,.4,9,.25,11,True,'white' if dark else 'muted')
    logo=kit/'02_Logos'/('voltoshare-logo-white.png' if dark else 'voltoshare-logo-navigation.png')
    s.shapes.add_picture(str(logo),Inches(10.73),Inches(.35),width=Inches(2.0))
    if d['kind']=='title':
        text(s,d['title'],.6,1.65,10.9,1.8,53,True,'white')
        text(s,d['subtitle'],.65,3.8,9.85,1,26,False,'white')
        text(s,'TEAM VOLTOSHARE',.65,5.45,10,.3,12,True,'white')
        text(s,' · '.join(d['sections'][0]['items']),.65,5.96,11.8,.65,19,False,'white')
    elif d['kind']=='closing':
        text(s,d['title'],.6,1.45,11.6,1,42,True,'white')
        text(s,d['subtitle'],.6,2.6,11.6,.6,25,False,'white')
        for j,it in enumerate(d['sections']):card(s,it,.6+j*4.1,4.0,3.93,1.95,21,True)
    else:
        title_size=31 if len(d['title'])>50 else 35
        text(s,d['title'],.6,.97,12.13,.6,title_size,True)
        kind=d['kind'];sections=d.get('sections',[])
        if kind=='agenda':
            for j,it in enumerate(sections):card(s,it,.6+(j%2)*6.18,1.9+(j//2)*1.49,5.95,1.28,22)
        elif kind=='team':
            for j,it in enumerate(sections):
                y=1.9+j*.88;box(s,.6,y,.60,.6,'green',None,True)
                text(s,str(j+1).zfill(2),.69,y+.12,.42,.35,18,True,'white')
                text(s,it['title'],1.48,y+.07,10.8,.48,26,True)
        elif kind in ['market','metrics','marketSizing','hardware','case']:
            stats(s,d['stats'])
            y=3.46
            if kind=='case':table(s,d['rows'],.6,y,12.13,2.76,colwidths=[.65,.35])
            elif len(sections)==1:card(s,sections[0],.6,y,12.13,2.8,22)
            else:
                gap=.22;w=(12.13-gap*(len(sections)-1))/len(sections)
                for j,it in enumerate(sections):card(s,it,.6+j*(w+gap),y,w,2.8,21)
        elif kind=='roadmap':
            for j,it in enumerate(sections):card(s,it,.6+(j%4)*3.08,1.9+(j//4)*2.25,2.88,2.03,18)
        elif kind in ['model','platform']:
            if d.get('subtitle'):
                text(s,d['subtitle'],.6,1.78,12.13,.97,21);y=3.04;h=3.2
            else:y=1.93;h=4.25
            for j,it in enumerate(sections):card(s,it,.6+j*4.12,y,3.89,h,22)
        elif kind=='flows':
            for j,it in enumerate(sections):card(s,it,.6+j*4.12,1.87,3.89,1.95,20)
            table(s,d['rows'],.6,4.1,12.13,2.23,colwidths=[.2,.8])
        elif kind=='charging':
            for j,it in enumerate(sections):card(s,it,.6+j*3.08,1.84,2.88,1.58,18)
            for j,it in enumerate(d['stats']):
                text(s,it['value'],.6,3.65+j*.87,3.0,.52,28,True,'green');text(s,it['label'],.6,4.12+j*.87,3.0,.35,13)
            text(s,'Illustrative Lastkurven · kW nach Stunde',3.82,3.48,8.9,.3,14,True)
            chart(s,d['chart'],3.7,3.78,9.1,2.65)
        elif kind=='finance' and d.get('financePreset')=='zurich':
            stats(s,d['stats'],1.86,1.38)
            text(s,'Erträge und Kosten pro Jahr',.6,3.34,6.25,.25,12,True)
            table(s,[[a,b.replace(' / Jahr','')] for a,b in d['rows']],.6,3.70,6.25,2.57,colwidths=[.72,.28])
            text(s,'Kumulierter Cashflow · CHF',7.06,3.49,5.6,.3,14,True)
            chart(s,d['chart'],6.95,3.9,5.82,2.5)
        elif kind=='benefits':
            for j,it in enumerate(sections):card(s,it,.6+j*6.18,1.88,5.95,2.4,20)
            table(s,d['rows'],.6,4.57,12.13,1.73,True,colwidths=[.33,.4,.27])
        elif kind=='sources':
            for j,it in enumerate(d['sources']):
                x=.6+(j%2)*6.18;y=1.86+(j//2)*.84
                txt=text(s,it['label'],x,y,5.9,.66,16,True)
                if it.get('url'):
                    for p in txt.text_frame.paragraphs:
                        for r in p.runs:r.hyperlink.address=it['url']
            text(s,sections[0]['title'],.6,5.43,12.13,.3,17,True,'green')
            text(s,sections[0]['body'],.6,5.85,12.13,.65,16)
        elif kind=='finance':
            stats(s,d['stats'],1.86,1.38)
            for j,it in enumerate(sections):card(s,it,.6+j*4.12,3.55,3.89,2.78,19)
        else:
            for j,it in enumerate(sections):card(s,it,.6,1.9+j*1.3,12.13,1.13,21)
    # A true source/assumption footer, rather than unsupported customer claims.
    source_label=' · '.join(x['label'] for x in d.get('sources',[])) if d['kind']!='sources' else 'Quellen aus der gelieferten Präsentation · Details und Abgrenzungen in den Notizen'
    if not source_label:
        source_label='Teamannahmen · Modell ohne Steuern und Finanzierung' if d['kind'] in ['finance','benefits','case','marketSizing'] else 'Projektentwurf · Quelle: gelieferte VoltoShare-Präsentation'
    if len(source_label)>170:source_label=source_label[:167]+'…'
    text(s,source_label,.6,6.92,11.3,.27,9.5,False,'white' if dark else 'muted')
    text(s,f'{index:02d} / {len(data["slides"]):02d}',11.92,6.9,.8,.3,11,False,'white' if dark else 'muted',PP_ALIGN.RIGHT)
    note='\n\n'.join(d.get('notes',[]))+'\n\n'+data['exportNote']
    if d.get('sources'):note+='\n\nQuellen:\n'+'\n'.join(x['label']+(' — '+x['url'] if x.get('url') else '') for x in d['sources'])
    s.notes_slide.notes_text_frame.text=note

prs.core_properties.title=data['title']
prs.core_properties.subject='VoltoShare – Projektentwurf und illustrative Finanzmodelle'
prs.core_properties.author='Team VoltoShare'
prs.core_properties.keywords='VoltoShare, Elektromobilität, Shared Charging, Modellrechnung'
args.out.parent.mkdir(parents=True,exist_ok=True);prs.save(args.out)
print(f'Built {len(prs.slides)} editable slides: {args.out}')
