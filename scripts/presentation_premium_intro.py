"""Architectural editorial redesign of source slides 1–8, retaining native content."""
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from presentation_modern_main import at,fill,fmt,text,panel,rect,front,bg,ids,rgb


def _quiet(slide):
    """Clear only old cosmetic panels/rules before composing a fresh layout."""
    bg(slide,'white')
    for sh in slide.shapes:
        if sh.shape_type in (1,9) and (not sh.has_text_frame or not sh.text.strip()):
            fill(sh,None)
    for sh in slide.shapes:
        if sh.has_text_frame and sh.top/Inches(1)>6.95:
            fmt(sh,10,False,'muted')
    rect(slide,.65,.27,.64,.035,'green')
    rect(slide,0,7.40,13.3333,.10,'white')


def _rule(s,x,y,w,c='line'):
    return rect(s,x,y,w,.012,c)


def _avatar(s,x,y,size):
    # Neutral native placeholder, not a generated/guessed person or photograph.
    circle=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x),Inches(y),Inches(size),Inches(size))
    fill(circle,'tint')
    head=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x+size*.34),Inches(y+size*.20),Inches(size*.32),Inches(size*.32))
    fill(head,'sage')
    shoulders=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x+size*.20),Inches(y+size*.57),Inches(size*.60),Inches(size*.30))
    fill(shoulders,'sage')


def apply(prs,kit):
    for n,s in enumerate(list(prs.slides)[:8],1):
        if n==1:continue
        _quiet(s);d=ids(s)
        text(d[2],.65,.59,12.0,.70,36,True)
        if 32 in d and d[32].has_text_frame and d[32].text.strip() and n!=2:
            text(d[32],.68,1.43,11.95,.28,14.5,False,'muted')
        _rule(s,.65,6.96,12.03)

    # 01: a panoramic architectural hero, with a strong full-width brand plinth.
    s=prs.slides[0];d=ids(s);bg(s,'white')
    for sh in s.shapes:
        if sh.shape_type==1 and sh.has_text_frame and not sh.text:fill(sh,None)
    at(d[2],0,0,13.3333,5.35);d[2].crop_left=d[2].crop_right=0;d[2].crop_top=.12;d[2].crop_bottom=.16
    base=rect(s,0,5.35,13.3333,2.15,'green')
    text(d[27],.68,5.75,6.68,1.20,68,True,'white');front(d[27])
    text(d[32],8.15,5.90,4.48,.97,17,False,'white');front(d[32])
    # Keep the native source symbol visible; supplied white symbol anchors the photo.
    badge=rect(s,.65,.58,1.10,1.10,'green');front(d[34]);at(d[34],.83,.76,.74,.71)
    at(d[5],6.90,6.16,.56,.40)
    for sh in d[5].shapes:fill(sh,'green')
    front(d[5])

    # 02: editorial navigation rail + a concise, vertically paced contents list.
    s=prs.slides[1];d=ids(s);rail=rect(s,0,0,4.10,7.5,'green',True)
    text(d[2],.65,1.02,3.00,.78,46,True,'white')
    text(d[62],.68,5.99,2.80,.62,15,False,'pale')
    text(d[30],.65,7.05,3.0,.20,10,False,'pale')
    rect(s,0,7.40,4.10,.10,'green')
    for j,baseid in enumerate([32,37,42,47,52,57]):
        y=.76+j*.99
        text(d[baseid+2],4.64,y,.75,.46,27,False,'green')
        text(d[baseid+3],5.67,y,6.92,.42,25,True)
        text(d[baseid+4],5.68,y+.49,6.89,.29,16,False,'muted')
        if j<5:_rule(s,4.64,y+.83,8.00)

    # 03: equal portrait medallions, open typography and quiet identity details.
    s=prs.slides[2];d=ids(s)
    for j,entry in enumerate([(33,34,35,36,37,38,39),(40,41,42,43,44,45,46),(47,None,None,50,51,52,53),(54,55,56,57,58,59,60),(61,62,63,64,65,66,67)]):
        x=.68+j*2.46;a,b,c,name,rule,label,num=entry
        if j in [0,3]:_avatar(s,x+.02,2.18,2.10)
        if c:text(d[c],x,4.43,2.16,.20,9,False,'muted',PP_ALIGN.CENTER)
        text(d[name],x,4.88,2.16,1.02,21,True,'ink',PP_ALIGN.CENTER)
        text(d[label],x,6.00,2.16,.21,11,False,'muted',PP_ALIGN.CENTER)
        text(d[num],x,6.30,2.16,.27,14,False,'green',PP_ALIGN.CENTER)
    for sid,j in [(7,1),(4,2),(3,4)]:
        sh=d[sid];at(sh,.70+j*2.46,2.18,2.10,2.10)
        geom=sh._element.spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}prstGeom')
        if geom is not None:geom.set('prst','ellipse')
        front(sh)

    # 04: proposition as the editorial lead, taxonomy as a precise right-hand ledger.
    s=prs.slides[3];d=ids(s)
    panel(d[13],.65,1.82,4.80,4.88,'green')
    text(d[14],.96,2.15,4.18,4.18,23,False,'white')
    for j,sid in enumerate([15,17,18]):
        y=2.08+j*1.12
        fill(d[sid],None);text(d[sid],5.79,y,2.09,.60,15.5,True,'green')
        _rule(s,5.79,y+.82,6.89)
    for sid,row,col in [(22,0,0),(23,0,1),(25,1,0),(26,1,1),(27,1,2),(28,2,0),(29,2,1),(30,2,2)]:
        fill(d[sid],None);text(d[sid],8.12+col*1.53,2.10+row*1.12,1.45,.60,14,False,'ink',PP_ALIGN.CENTER)
    # Source categories without option text are retained as a compact quiet band.
    rect(s,5.79,5.55,6.89,1.10,'tint')
    for j,sid in enumerate([19,20,21]):
        text(d[sid],5.95+j*2.27,5.80,2.03,.64,14.5,True,'green',PP_ALIGN.CENTER);front(d[sid])

    # 05: a single market insight gets a dramatic, editorial dark spread.
    s=prs.slides[4];d=ids(s);bg(s,'green');rect(s,0,4.88,13.3333,2.62,'white',True)
    text(d[2],.65,.59,12.0,.70,36,True,'white');text(d[32],.68,1.43,11.95,.28,14.5,False,'pale')
    text(d[40],.65,1.99,4.71,1.39,100,True,'white')
    text(d[41],.72,3.53,4.48,1.13,22,False,'white')
    for j,baseid in enumerate([33,36,42]):
        y=2.03+j*.95
        text(d[baseid+1],6.02,y,3.03,.55,33,True,'white')
        text(d[baseid+2],9.35,y+.04,3.22,.75,16,False,'white')
        if j<2:_rule(s,6.02,y+.82,6.62,'sage')
    text(d[46],.68,5.05,11.98,.34,19,True,'green')
    text(d[47],.68,5.44,5.64,1.15,14.5,False)
    text(d[48],6.92,5.44,5.65,1.15,14.5,False)
    for sh in s.shapes:
        if sh.has_text_frame and sh.top/Inches(1)>6.65:fmt(sh,10,False,'muted')

    # 06: uncluttered chart rows balanced by a large demand-side callout.
    s=prs.slides[5];d=ids(s)
    text(d[34],.65,1.83,7.10,.42,25,True)
    for j,(label,track,bar,value) in enumerate([(35,36,37,38),(39,40,41,42),(43,44,45,46)]):
        y=2.60+j*1.18
        text(d[label],.65,y,4.55,.60,18,False)
        panel(d[track],.65,y+.70,6.53,.10,'tint');panel(d[bar],.65,y+.70,[.9142,3.9833,5.4852][j],.10,'green')
        text(d[value],5.60,y+.02,1.59,.52,27,True,'green',PP_ALIGN.RIGHT)
    text(d[47],.65,6.28,7.10,.27,12,False,'muted')
    _rule(s,7.68,1.89,.01)
    text(d[49],8.18,1.78,4.47,1.22,86,True,'green')
    text(d[50],8.20,3.13,4.42,1.40,22,False)
    _rule(s,8.19,4.86,4.46)
    text(d[52],8.19,5.14,4.46,.60,39,True)
    text(d[53],8.20,5.91,4.42,.69,15,False,'muted')

    # 07: three editorial market columns replace the nested funnel/card scaffold.
    s=prs.slides[6];d=ids(s)
    for j,baseid in enumerate([33,41,49]):
        x=.65+j*3.13
        if j==2:panel(d[baseid],x-.18,2.01,3.07,4.42,'green')
        color='white' if j==2 else 'ink';accent='white' if j==2 else 'green';muted='pale' if j==2 else 'muted'
        text(d[baseid+1],x,2.23,2.75,.42,17,True,accent)
        text(d[baseid+2],x,2.96,2.82,1.04,26,True,color)
        text(d[baseid+3],x,4.22,2.73,.90,14.5,False,muted)
        rev=[37,45,53][j]
        text(d[rev+1],x,5.28,2.73,.30,13,False,muted)
        text(d[rev+2],x,5.77,2.73,.53,23,True,accent)
        if j<2:_rule(s,x,2.00,2.75,'green')
    _rule(s,10.12,2.0,.01)
    text(d[58],10.20,2.23,2.47,.42,18,True,'green')
    text(d[59],10.20,3.02,2.47,3.30,16,False,'muted')

    # 08: chronology now follows the actual five-stage / three-stage phase split.
    s=prs.slides[7];d=ids(s)
    panel(d[33],.65,1.91,12.03,.43,'green');panel(d[34],.65,4.58,12.03,.43,'dark')
    text(d[35],.84,2.01,6.66,.25,14,True,'white');text(d[36],7.54,2.01,4.92,.25,12,False,'white')
    text(d[37],.84,4.68,5.73,.25,14,True,'white');text(d[38],6.93,4.68,5.53,.25,13,False,'white')
    for j,baseid in enumerate(range(40,72,4)):
        if j<5:x=.65+j*2.45;y=2.63;w=2.20
        else:x=.65+(j-5)*4.10;y=5.18;w=3.83
        text(d[baseid],x,y,w,.24,14,True,'green')
        text(d[baseid+2],x,y+.38,w,.36,19,True)
        text(d[baseid+3],x,y+.91,w,.81 if j<5 else .43,13,False,'muted')
        _rule(s,x,y-.10,w,'line')
    text(d[73],.65,6.57,12.02,.36,10.5,False,'muted')
    return prs
