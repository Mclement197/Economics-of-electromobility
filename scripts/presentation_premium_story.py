"""Second editorial design direction: source-exact story slides 9–17.

This module deliberately changes the composition rather than merely recolouring
existing cards. It is applied after the source-preserving modern pass.
"""
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from presentation_modern_main import at, fill, text, panel, rect, bg, ids, rgb, front


def tight(shape):
    for p in shape.text_frame.paragraphs:
        p.space_after = Pt(0)
        p.line_spacing = 1.0
    return shape


def t(shape,x,y,w,h,size=18,bold=False,color='ink',align=PP_ALIGN.LEFT,center=False):
    return tight(text(shape,x,y,w,h,size,bold,color,align,center))


def hide_decor(shape):
    fill(shape,None)


def _white_paper(slide):
    bg(slide,'white')
    for shape in slide.shapes:
        try:
            if str(shape.fill.fore_color.rgb)=='F8F5F0':
                shape.fill.fore_color.rgb=rgb('white')
        except (AttributeError,TypeError):
            pass


def _transform(shapes,old,new):
    ox,oy,ow,oh=old;nx,ny,nw,nh=new
    for shape in shapes:
        x,y,w,h=[v/Inches(1) for v in [shape.left,shape.top,shape.width,shape.height]]
        at(shape,nx+(x-ox)*nw/ow,ny+(y-oy)*nh/oh,w*nw/ow,h*nh/oh)


def apply(prs,kit):
    for no in range(9,18):
        s=prs.slides[no-1];d=ids(s)
        if no!=16:
            _white_paper(s)
            t(d[2],.65,.55,12.03,.82,36 if len(d[2].text)<46 else 32,True)
            t(d[32],.67,1.48,11.98,.30,15,False,'muted')
            t(d[30],.65,7.05,5.5,.20,9.5,False,'muted')
            t(d[31],12.13,7.02,.55,.27,12,True,'green',PP_ALIGN.RIGHT)

    # 09: architectural dark schematic, contrasted with an open feature index.
    s=prs.slides[8];d=ids(s)
    panel(d[33],.65,2.02,6.82,4.55,'dark')
    _transform([d[n] for n in range(34,73) if n in d],(.85,2.22,6.6,4.0),(.92,2.27,6.30,3.99))
    t(d[34],.93,2.28,6.18,.50,16.5,True,'white')
    for n in [40,45,50,55,60,62,64,66]:
        # The bay itself remains pale; this is its original, editable label.
        for p in d[n].text_frame.paragraphs:
            p.font.color.rgb=rgb('ink')
            for r in p.runs:r.font.color.rgb=rgb('ink')
    for n in [37,42,47,52,57]:fill(d[n],'pale')
    for n in [38,43,48,53,58]:fill(d[n],'green')
    for n in [39,44,49,54,59]:d[n].line.color.rgb=rgb('pale')
    t(d[67],.94,5.34,6.22,.30,12.5,False,'pale')
    fill(d[68],'green');fill(d[70],'green')
    t(d[69],.97,5.84,2.92,.43,18,True,'white',PP_ALIGN.CENTER,True)
    t(d[71],4.16,5.84,2.92,.43,18,True,'white',PP_ALIGN.CENTER,True)
    for back,bar,head,body,y in [(73,74,75,76,2.09),(77,78,79,80,3.68),(81,82,83,84,5.27)]:
        hide_decor(d[back]);hide_decor(d[bar])
        t(d[head],7.99,y,4.65,.63,22,True,'green')
        t(d[body],7.99,y+.70,4.62,.83,17,False)
        if y<5:rect(s,7.99,y+1.45,4.65,.01,'line')

    # 10: three flush architectural lanes. Numbers anchor the base instead of
    # repeating a row of cards with the same typographic hierarchy.
    s=prs.slides[9];d=ids(s)
    for sh in s.shapes:
        if abs(sh.top/Inches(1)-3.98)<.02 and sh.height<Inches(.03):hide_decor(sh)
    for j,base in enumerate([33,38,43]):
        x=.65+j*4.01;color=['green','white','dark'][j];fg='ink' if j==1 else 'white'
        panel(d[base],x,2.03,4.01,4.57,color);hide_decor(d[base+1])
        t(d[base+3],x+.30,2.39,3.42,1.10,27,True,fg)
        t(d[base+4],x+.30,3.70,3.42,1.87,18,False,fg)
        for p in d[base+4].text_frame.paragraphs:p.space_after=Pt(12)
        t(d[base+2],x+2.82,5.62,.82,.76,48,True,'green' if j==1 else 'pale',PP_ALIGN.RIGHT)
    rect(s,4.66,2.03,.012,4.57,'line')

    # 11: a value-proposition column beside a large two-sided payment diagram.
    s=prs.slides[10];d=ids(s)
    hide_decor(d[33]);t(d[34],.65,2.06,4.14,.48,24,True)
    for head,body,y in [(35,36,2.84),(37,38,4.62),(39,40,5.75)]:
        t(d[head],.65,y,4.13,.34,17,True,'green')
        t(d[body],.65,y+.40,4.13,1.15 if head==35 else .58,16,False)
    panel(d[41],5.17,2.02,7.51,4.60,'tint')
    t(d[42],5.51,2.30,6.83,.48,25,True)
    for box,txt,x,w,c in [(43,44,5.51,1.94,'white'),(45,46,8.02,2.03,'green'),(47,48,10.60,1.72,'white')]:
        panel(d[box],x,3.14,w,.80,c)
        t(d[txt],x+.05,3.14,w-.10,.80,17,True,'white' if c=='green' else 'green',PP_ALIGN.CENTER,True)
    at(d[49],7.57,3.54,.33,0);at(d[50],10.17,3.54,.31,0)
    d[49].line.color.rgb=rgb('green');d[50].line.color.rgb=rgb('green')
    for no,x,w in [(51,5.52,3.04),(52,9.13,3.17)]:
        t(d[no],x,4.40,w,1.35,17,False)
        first=d[no].text_frame.paragraphs[0]
        first.font.size=Pt(25);first.font.bold=True;first.font.color.rgb=rgb('green');first.space_after=Pt(10)
        for run in first.runs:run.font.size=Pt(25);run.font.bold=True;run.font.color.rgb=rgb('green')
    hide_decor(d[53]);t(d[54],5.52,6.08,6.79,.38,12.7,False,'muted')

    # 12: the building illustration becomes a compact architectural elevation;
    # two original statistics get typographic emphasis, the ledger stays open.
    s=prs.slides[11];d=ids(s)
    _transform([d[n] for n in range(33,76)],(.65,2.0,5.45,4.42),(.65,2.03,4.65,4.56))
    panel(d[33],.65,2.03,4.65,4.56,'tint')
    # Reserve a true annotation lane: labels must not sit on the building edge.
    for no in range(34,75):
        sh=d[no];sh.left=Inches(.90+(sh.left/Inches(1)-.90)*.78);sh.width=round(sh.width*.78)
    # Retain the original complete number/label paragraphs in separate callouts.
    for no,y in [(76,2.48),(77,5.18)]:
        rect(s,3.47,y,1.68,.95,'white')
        t(d[no],3.60,y+.17,1.43,.65,16,True,'green',PP_ALIGN.LEFT);front(d[no])
    t(d[75],.90,6.27,2.48,.28,11.8,False,'muted',PP_ALIGN.CENTER)
    hide_decor(d[78]);t(d[79],5.84,2.05,6.84,.45,25,True)
    for j,(label,value) in enumerate([(80,81),(83,84),(86,87),(89,90),(92,93),(95,96),(98,99)]):
        y=2.80+j*.53
        t(d[label],5.84,y,4.73,.40,15.4,False)
        t(d[value],10.67,y,2.01,.40,21,True,'green',PP_ALIGN.RIGHT)
        if j<6:at(d[label+2],5.84,y+.45,6.84,0);d[label+2].line.color.rgb=rgb('line')

    # 13: wide chart and an explicit horizontal four-step journey underneath.
    s=prs.slides[12];d=ids(s)
    hide_decor(d[33]);at(d[34],.65,2.02,12.03,2.83)
    panel(d[51],.65,4.98,12.03,.47,'green')
    t(d[52],.87,5.075,11.59,.25,16,False,'white',PP_ALIGN.CENTER)
    for j,(box,num,title,body) in enumerate([(35,36,37,38),(39,40,41,42),(43,44,45,46),(47,48,49,50)]):
        x=.65+j*3.05;hide_decor(d[box])
        t(d[num],x,5.69,.47,.36,18,True,'green')
        t(d[title],x+.61,5.69,2.26,.36,19,True)
        t(d[body],x+.61,6.14,2.26,.44,12.8,False,'muted')
        if j<3:rect(s,x+2.91,5.70,.008,.80,'line')

    # 14: asymmetrical financial statement. A forest metric rail gives a clear
    # reading order; the chart has a broad uninterrupted axis and the annual
    # statement sits below it as an editorial ledger, not a stack of cards.
    s=prs.slides[13];d=ids(s)
    panel(d[33],.65,2.03,3.20,4.53,'green')
    hide_decor(d[36]);hide_decor(d[39])
    for value,label,y in [(34,35,2.37),(37,38,3.80),(40,41,5.22)]:
        t(d[value],.92,y,2.69,.58,30,True,'white')
        t(d[label],.94,y+.67,2.65,.32,15,False,'pale')
    hide_decor(d[42]);hide_decor(d[55])
    t(d[56],4.22,2.04,8.46,.44,24,True)
    at(d[57],4.16,2.61,8.57,1.85)
    t(d[58],4.22,4.44,8.46,.22,11.5,False,'muted',PP_ALIGN.CENTER)
    t(d[43],4.22,4.85,4.12,.32,17,True,'green')
    for label,value,y in [(44,45,5.36),(46,47,5.99)]:
        t(d[label],4.22,y,2.98,.43,14,False)
        t(d[value],7.30,y,1.10,.43,13.2,True,'ink',PP_ALIGN.RIGHT)
    t(d[48],8.78,4.85,3.90,.32,17,True,'green')
    for label,value,y in [(49,50,5.30),(51,52,5.75),(53,54,6.20)]:
        t(d[label],8.78,y,2.68,.43,13,False)
        t(d[value],11.57,y,1.11,.43,13,True,'ink',PP_ALIGN.RIGHT)
    rect(s,8.58,4.86,.01,1.73,'line')

    # 15: landlord result as a large dark hero; the sensitivity chart takes the
    # wider column, with the source resident trade-offs kept readable beneath.
    s=prs.slides[14];d=ids(s)
    panel(d[33],.65,2.03,4.22,2.65,'dark')
    t(d[34],.94,2.31,3.65,.38,21,True,'white')
    t(d[35],.94,2.95,2.20,.48,13.5,False,'pale');t(d[36],3.12,2.95,1.48,.48,14,True,'white',PP_ALIGN.RIGHT)
    t(d[37],.94,3.51,2.20,.37,13.5,False,'pale');t(d[38],3.12,3.51,1.48,.37,14,True,'white',PP_ALIGN.RIGHT)
    at(d[39],.94,3.99,3.65,0);d[39].line.color.rgb=rgb('sage')
    t(d[41],.94,4.15,3.65,.45,30,True,'white')
    # Small original net caption sits in the white area immediately beneath.
    t(d[40],.65,4.85,4.22,.30,13.5,False,'muted')
    hide_decor(d[42]);t(d[43],.65,5.65,2.12,.40,22,True)
    t(d[44],3.12,5.65,9.56,.95,16.5,False)
    for p in d[44].text_frame.paragraphs:p.space_after=Pt(4)
    hide_decor(d[45]);t(d[46],5.42,2.06,7.26,.52,25,True)
    at(d[47],5.31,2.90,7.39,2.17)
    t(d[48],5.48,5.15,7.15,.35,13.5,False,'muted')

    # 16: a deliberately quiet closing slide, with large original letterforms
    # and the supplied white mark; no additional slogans or decoration.
    s=prs.slides[15];d=ids(s);bg(s,'green');fill(d[2],'green')
    t(d[5],.65,2.04,7.10,1.62,108,True,'white')
    t(d[6],.72,4.20,10.95,.73,32,False,'white')
    t(d[7],.74,5.41,10.95,.38,18,False,'pale')
    panel(d[3],.73,1.56,1.06,.018,'sage');hide_decor(d[4])
    for sh in s.shapes:
        if sh.shape_type==13:at(sh,.72,.61,2.75,sh.height/Inches(1))

    # 17: exact-source bibliography in an indexed two-column editorial grid.
    s=prs.slides[16];d=ids(s)
    for j in range(12):
        label=33+j*2;body=label+1;col=j//6;row=j%6;x=.65+col*6.19;y=2.06+row*.70
        t(d[label],x,y,1.67,.51,12.0,True,'green')
        t(d[body],x+1.84,y,3.99,.59,11.6,False)
    hide_decor(d[57]);t(d[58],.65,6.43,12.03,.30,10.5,False,'muted')
    # White masks are not needed: source rules are simply aligned to new rows.
    for sh in s.shapes:
        if (not sh.has_text_frame or not sh.text.strip()) and sh.height<Inches(.02) and Inches(2)<sh.top<Inches(6.4):
            hide_decor(sh)

    # Chart data/workbooks are unchanged; only native visual styling is touched.
    for no in [13,14,15]:
        for sh in prs.slides[no-1].shapes:
            if not sh.has_chart:continue
            ch=sh.chart
            for attr in ['category_axis','value_axis']:
                try:
                    ax=getattr(ch,attr);ax.tick_labels.font.name='Liberation Sans';ax.tick_labels.font.size=Pt(11.5);ax.tick_labels.font.color.rgb=rgb('muted')
                    if ax.has_major_gridlines:ax.major_gridlines.format.line.color.rgb=rgb('line');ax.major_gridlines.format.line.width=Pt(.5)
                except (AttributeError,ValueError):pass
            if ch.has_legend:ch.legend.font.name='Liberation Sans';ch.legend.font.size=Pt(10.5)
    return prs
