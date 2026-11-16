from pathlib import Path
from xml.sax.saxutils import escape
import math, json
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader

KIT=Path(__file__).resolve().parents[2]
OUT=KIT/'01_Guidelines/VoltoShare_Design_Guidelines.pdf'
W,H=1280,720
M=60
C={'ink':'#1E2023','graphite':'#23262B','green':'#28563B','warm':'#F8F5F0','white':'#FFFFFF','tint':'#EAF0EB','muted':'#58615C','border':'#D9DFD9','strong':'#748178','blue':'#1959A6','bluebg':'#EAF2FE','amber':'#8A5200','amberbg':'#FFF3D6','red':'#B42318','redbg':'#FDECE9','neutral':'#56645E','neutralbg':'#EEF1EE'}
for name,f in [('LS','LiberationSans-Regular.ttf'),('LSB','LiberationSans-Bold.ttf'),('LSI','LiberationSans-Italic.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(KIT/'04_Fonts'/f)))
pdfmetrics.registerFontFamily('LS',normal='LS',bold='LSB',italic='LSI',boldItalic='LSB')
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('VoltoShare | Brand & digital design guidelines')
c.setAuthor('VoltoShare project team')
c.setSubject('Identity, website, resident app and presentation design system')
PAGE=0
CHECKS=[]
def col(x):return HexColor(C.get(x,x))
def rect(x,y,w,h,fill='white',stroke=None,r=0,sw=1):
    c.setFillColor(col(fill));c.setStrokeColor(col(stroke or fill));c.setLineWidth(sw)
    if r:c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=bool(stroke))
    else:c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))
def line(x,y,xx,yy,color='border',sw=1,dash=None):
    c.saveState();c.setStrokeColor(col(color));c.setLineWidth(sw)
    if dash:c.setDash(*dash)
    c.line(x,H-y,xx,H-yy);c.restoreState()
def text(s,x,y,size=18,color='ink',bold=False,align='left'):
    c.setFont('LSB' if bold else 'LS',size);c.setFillColor(col(color))
    if align=='center':c.drawCentredString(x,H-y-size*.83,str(s))
    elif align=='right':c.drawRightString(x,H-y-size*.83,str(s))
    else:c.drawString(x,H-y-size*.83,str(s))
    CHECKS.append({'page':PAGE,'text':str(s),'box':[x,y,x+pdfmetrics.stringWidth(str(s),'LSB' if bold else 'LS',size),y+size]})
def para(s,x,y,w,size=18,color='muted',bold=False,leading=None):
    p=Paragraph(s,ParagraphStyle('p',fontName='LSB' if bold else 'LS',fontSize=size,leading=leading or size*1.35,textColor=col(color)))
    _,hh=p.wrap(w,1000);p.drawOn(c,x,H-y-hh)
    CHECKS.append({'page':PAGE,'text':s,'box':[x,y,x+w,y+hh]})
    return hh
def label(s,x,y,color='green',size=11):
    c.saveState();t=c.beginText(x,H-y-size*.83);t.setFont('LSB',size);t.setFillColor(col(color));t.setCharSpace(1.5);t.textOut(s.upper());c.drawText(t);c.restoreState()
def image(p,x,y,w,h,fit='contain',pos=.5):
    ir=ImageReader(str(p));iw,ih=ir.getSize();k=min(w/iw,h/ih) if fit=='contain' else max(w/iw,h/ih)
    ww,hh=iw*k,ih*k
    xx=x+(w-ww)*pos;yy=y+(h-hh)*.5
    c.saveState();clip=c.beginPath();clip.rect(x,H-y-h,w,h);c.clipPath(clip,stroke=0,fill=0)
    c.drawImage(ir,xx,H-yy-hh,ww,hh,mask='auto');c.restoreState()
def logo(x,y,w=205,white=False,full=False):
    stem='voltoshare-logo-white' if white else ('voltoshare-logo-primary' if full else 'voltoshare-logo-navigation')
    h=w*(676/3000 if full or white else 516/3000)
    image(KIT/'02_Logos'/(stem+'.png'),x,y,w,h);return h
def symbol(x,y,w=55,white=False):image(KIT/'02_Logos'/('voltoshare-symbol-white.png' if white else 'voltoshare-symbol-green.png'),x,y,w,w)
def icon(name,x,y,size=26):image(KIT/'03_Images/icons'/('icon-'+name+'.png'),x,y,size,size)
def pill(s,x,y,fg='green',bg='tint',size=12,h=28):
    tw=pdfmetrics.stringWidth(s,'LSB',size)+24;rect(x,y,tw,h,bg,r=14);text(s,x+12,y+(h-size)/2-1,size,fg,True);return tw
def btn(s,x,y,w,h=42,primary=True,size=14):
    rect(x,y,w,h,'green' if primary else 'white',None if primary else 'strong',r=7)
    text(s,x+w/2,y+(h-size)/2-1,size,'white' if primary else 'ink',True,'center')
def arrow(x,y,xx,yy,color='green',sw=1.7):
    line(x,y,xx,yy,color,sw);a=math.atan2(yy-y,xx-x);l=7
    line(xx,yy,xx-l*math.cos(a-.45),yy-l*math.sin(a-.45),color,sw);line(xx,yy,xx-l*math.cos(a+.45),yy-l*math.sin(a+.45),color,sw)
def footer(source='',dark=False):
    co='white' if dark else 'muted'
    line(M,H-48,W-M,H-48,'strong' if dark else 'border',.7)
    text('VOLTOSHARE  /  BRAND & DIGITAL GUIDELINES',M,H-33,10,co)
    if source:text(source,430,H-33,9,co)
    text(f'{PAGE:02}',W-M,H-35,13,co,True,'right')
def page(section,title,sub='',bg='warm',source='Design system v2.0  |  16 November 2026'):
    global PAGE
    if PAGE:c.showPage()
    PAGE+=1
    rect(0,0,W,H,bg)
    logo(M,28,155)
    label(section,W-M,35,'muted') if False else text(section.upper(),W-M,34,10,'muted',True,'right')
    text(title,M,91,42,'ink',True)
    if sub:para(sub,M,146,1110,18,'muted')
    footer(source)
def ruleitem(n,title,body,x,y,w=325):
    label(n,x,y);text(title,x,y+27,23,'ink',True);para(body,x,y+65,w,17)
def smallstat(x,y,w,labeltext,value,sub='',tint=False):
    rect(x,y,w,101,'tint' if tint else 'white','border',r=10)
    text(labeltext,x+16,y+15,12,'muted');text(value,x+16,y+37,28,'green' if tint else 'ink',True)
    if sub:text(sub,x+16,y+77,10.5,'muted')
def field(labeltext,value,x,y,w,h=42):
    text(labeltext,x,y,11,'muted');rect(x,y+20,w,h,'white','strong',r=7);text(value,x+12,y+33,13)
def browser(x,y,w,h,title='voltoshare / design reference'):
    rect(x,y,w,h,'white','border',r=12)
    rect(x+1,y+1,w-2,30,'neutralbg',r=10)
    for i in range(3):
        c.setFillColor(col('strong'));c.circle(x+16+13*i,H-y-15,3,fill=1,stroke=0)
    text(title,x+w/2,y+9,10,'muted',False,'center')
def phone(x,y,w,h,title):
    rect(x,y,w,h,'graphite',r=25);rect(x+5,y+5,w-10,h-10,'warm',r=21)
    rect(x+w*.35,y+11,w*.3,5,'graphite',r=3)
    text('14:30',x+18,y+24,10,'ink',True);text('DEMO',x+w-18,y+24,8,'muted',True,'right')
    text(title,x+18,y+52,24,'ink',True)
def mnav(x,y,w,active='Home'):
    rect(x+6,y,w-12,49,'white',r=14);line(x+15,y,x+w-15,y)
    for i,n in enumerate(['Home','Chargers','Bookings','More']):
        xx=x+(i+.5)*w/4
        c.setFillColor(col('green' if n==active else 'strong'));c.circle(xx,H-y-14,2.4,fill=1,stroke=0)
        text(n,xx,y+26,8.2,'green' if n==active else 'muted',n==active,'center')
def parking(x,y,w,h,selected='C01',labels=True):
    rect(x,y,w,h,'white','border',r=12)
    cw=(w-30-9*6)/10;ch=(h-75)/2
    status={3:('C01','Available','green','tint'),4:('C02','Charging','blue','bluebg'),5:('C03','Available','green','tint'),13:('C04','Reserved','amber','amberbg'),14:('C05','Offline','neutral','neutralbg')}
    for b in range(1,21):
        row=0 if b<=10 else 1;cc=(b-1)%10;bx=x+15+cc*(cw+6);by=y+14+row*(ch+45)
        if b in status:
            cid,st,fg,bg=status[b];rect(bx,by,cw,ch,bg,fg,r=5,sw=2 if cid==selected else 1)
            text(cid,bx+cw/2,by+10,10 if cw>55 else 8,fg,True,'center')
            if cw>55:text(st,bx+cw/2,by+35,8.5,fg,False,'center')
            else:text('+' if st=='Available' else ('C' if st=='Charging' else ('R' if st=='Reserved' else 'OFF')),bx+cw/2,by+32,11,fg,True,'center')
        else:rect(bx,by,cw,ch,'warm','border',r=5)
        text(f'P{b:02}',bx+cw/2,by+ch-19,9,'muted',False,'center')
    yy=y+14+ch+23;arrow(x+18,yy,x+w-18,yy,'strong',1)
    rect(x+w*.36,yy-9,w*.28,20,'white');text('DRIVE AISLE',x+w*.5,yy-6,9,'muted',True,'center')

# 01. Cover
PAGE=1
rect(0,0,W,H,'graphite')
image(KIT/'03_Images/voltoshare-charger-garage.jpg',564,0,716,H,'cover',.67)
logo(60,55,380,True,True)
label('Identity / Website / Presentation',62,232,'white',11)
text('Shared charging.',60,278,49,'white',True)
text('One clear identity.',60,338,49,'white',True)
para('Brand and digital<br/>design guidelines',62,430,430,27,'white')
line(62,550,475,550,'strong',1)
text('VoltoShare',62,572,17,'white',True)
text('Ökonomie der Elektromobilität',62,602,15,'white')
text('VERSION 2.0  /  16 NOVEMBER 2026',62,663,11,'white')
rect(978,660,247,25,'graphite',r=4);text('SUPPLIED CONCEPT VISUAL',991,667,9,'white')

# 02. Direction
page('01 / Brand direction','A building service, made effortless.','A restrained identity for a shared infrastructure service: clear, dependable and easy to use.',source='Foundation: supplied proposal, p. 1  |  Visual direction: supplied references')
image(KIT/'03_Images/voltoshare-charger-garage.jpg',60,218,550,245,'cover',.65)
rect(634,218,260,245,'green',r=0);symbol(707,279,116,True)
image(KIT/'03_Images/voltoshare-nfc-card.jpg',918,218,302,245,'cover',.5)
ruleitem('01 / Clarity','Show the service.','Lead with shared charging at home. Explain the two payment streams in plain language.',60,493,340)
ruleitem('02 / Consistency','Repeat the essentials.','Use the same logo, typography, colours and spacing across the website and slides.',462,493,340)
ruleitem('03 / Credibility','Make evidence visible.','Label proposal examples and demo values. Keep open commercial decisions explicit.',864,493,340)

# 03. Logo family
page('02 / Identity','The supplied mark is the anchor.','Use the master assets in the kit. Keep the symbol, wordmark and German tagline in their defined proportions.')
rect(60,219,566,205,'white',r=12);logo(94,275,495,False,True);label('Primary / light backgrounds',83,391,'muted',10)
rect(650,219,570,205,'graphite',r=12);logo(686,275,495,True,True);label('Reversed / dark backgrounds',674,391,'white',10)
rect(60,448,566,161,'white',r=12);logo(91,487,330);label('Navigation / tagline omitted',83,576,'muted',10)
for xx,fill,white in [(650,'tint',False),(845,'green',True),(1040,'graphite',True)]:
    rect(xx,448,180,161,fill,r=12);symbol(xx+54,477,72,white)
    text('Symbol',xx+90,578,12,'white' if white else 'green',False,'center')

# 04. Clear space and export
page('03 / Logo use','Give the identity room to breathe.','A stable silhouette, generous clear space and the right export are more important than decorative effects.')
rect(60,220,760,360,'white',r=12)
logo(159,332,560,False,True)
line(131,302,748,302,'strong',1,[4,4]);line(131,476,748,476,'strong',1,[4,4]);line(131,302,131,476,'strong',1,[4,4]);line(748,302,748,476,'strong',1,[4,4])
line(159,270,159,490,'border',.8,[2,4]);line(719,270,719,490,'border',.8,[2,4])
arrow(131,287,159,287);text('x',139,267,15,'green',True)
text('Minimum clear space: x = 25% of symbol height',440,526,15,'green',True,'center')
text('Choose the right file',862,221,25,'ink',True)
for yy,head,body in [(270,'Full lockup','Use at 320 px or wider in digital layouts. Keep the tagline readable.'),(370,'Navigation logo','Use at 200 px or wider. The separate file omits the tagline intentionally.'),(470,'Symbol','Use at 24 px or larger for compact UI. Use 32 px for clearer recognition.')]:
    text(head,862,yy,18,'green',True);para(body,862,yy+30,340,16)
para('<b>Preserve:</b> aspect ratio, letterforms and clear space. <b>Avoid:</b> stretching, shadows, outlines, extra colours or placing the mark over a busy photo.',60,602,1160,16)

# 05. Colour
page('04 / Colour','Forest green. Charcoal. Space.','Neutral surfaces carry the content. Forest green identifies the brand and the primary action.')
swatches=[('Forest','#28563B','Primary action / brand','green','white'),('Ink','#1E2023','Headlines / body','ink','white'),('Graphite','#23262B','Dark surfaces / covers','graphite','white'),('Warm white','#F8F5F0','Page canvas','warm','ink'),('White','#FFFFFF','Content surfaces','white','ink'),('Soft green','#EAF0EB','Supporting emphasis','tint','ink')]
for i,(nm,hx,use,fill,fg) in enumerate(swatches):
    xx=60+(i%3)*272;yy=218+(i//3)*186
    rect(xx,yy,250,125,fill,'border' if fill in ['warm','white','tint'] else None,r=9)
    text(nm,xx+18,yy+22,24,fg,True);text(hx,xx+18,yy+77,15,fg)
    text(use,xx,yy+142,13,'muted')
text('Contrast for projection',904,222,24,'ink',True)
para('White on forest<br/><b>8.45 : 1</b>',904,273,290,21,'green')
para('Forest on graphite is only <b>1.80 : 1</b>. Use the all-white logo and white text on dark covers.',904,353,290,17)
line(904,446,1220,446)
para('Use blue, amber and red only for operational states. Pair every state with a written label.',904,469,290,17)
pill('Charging',904,560,'blue','bluebg');pill('Reserved',1022,560,'amber','amberbg')
text('Contrast ratios calculated from the specified sRGB colours. WCAG references appear on page 18.',60,621,12,'muted')

# 06. Typography
page('05 / Typography','Familiar letterforms. A clear hierarchy.','Preserve the logo as artwork. Use one companion family for editable website, document and slide text.')
rect(60,218,436,364,'white',r=12)
text('Aa',87,236,150,'green',True)
text('Liberation Sans',90,414,35,'ink',True)
text('Regular  /  Bold',91,464,20,'muted')
text('0123456789   CHF 35.84',91,513,24,'ink')
text('Web hierarchy',546,222,23,'ink',True)
roles=[('Display','48–64 px','Shared charging.'),('Section heading','32–40 px','How the model works'),('Body','16–18 px','Clear, concise explanatory text.'),('UI label','14–16 px','Reserve a charger'),('Supporting text','12–14 px','Last updated 14:30')]
for i,(role,spec,sample) in enumerate(roles):
    yy=270+i*58
    text(role,546,yy,15,'green',True);text(spec,746,yy,15,'muted');text(sample,920,yy,17 if i>1 else 20,'ink',i<2)
    line(546,yy+39,1220,yy+39)
para('<b>Font match:</b> the supplied images do not identify the original font. Liberation Sans is the bundled Arial-compatible companion; the logo lettering remains derived from the supplied artwork. Regular, bold and italic font files are included with their licence.',60,604,1160,15)

# 07. Layout system
page('06 / Layout & components','Structure does the visual work.','Use a 4 px spacing unit, a restrained radius system and a clear difference between actions, content and status.')
label('Spacing scale',60,220)
for i,n in enumerate([4,8,12,16,24,32,48,64]):
    xx=60+i*94;rect(xx,253,62,n,'green',r=2);text(str(n),xx,332,16,'green',True)
text('Desktop',60,395,23,'ink',True);para('12-column layout<br/>Content width up to 1200 px<br/>24–32 px gutters',60,436,300,17)
text('Mobile',398,395,23,'ink',True);para('Single-column reading order<br/>16–20 px side padding<br/>44 px touch targets preferred',398,436,315,17)
rect(806,218,414,380,'white','border',r=12)
text('Controls',831,243,24,'ink',True)
btn('Reserve a charger',831,291,234,44);btn('View details',831,351,174,44,False)
field('Vehicle','City EV',831,420,364)
pill('Available',831,513);pill('Charging',950,513,'blue','bluebg');pill('Offline',1073,513,'neutral','neutralbg')
para('Control radius: <b>8 px</b> · Card radius: <b>12 px</b> · Feature radius: <b>20 px</b>. Use visible focus, persistent field labels and explicit error messages.',60,606,1160,15)

# 08. Imagery
page('07 / Imagery','Show the place and the product.','Use the supplied garage and access-card visuals to make the service tangible. Keep text outside the busiest parts of the image.',source='Images: supplied concept artwork  |  No customer installation is implied')
image(KIT/'03_Images/voltoshare-charger-garage.jpg',60,219,740,344,'cover',.68)
image(KIT/'03_Images/voltoshare-nfc-card.jpg',824,219,396,222,'cover',.5)
text('Infrastructure in context',60,581,23,'ink',True)
para('Hero, cover and service sections. Preserve the charger and its cable when cropping.',60,615,740,15)
text('Access, made visible',824,466,23,'ink',True)
para('Use the NFC-card image for access and resident journeys. Label it as a concept visual where evidence matters.',824,504,380,17)
para('Avoid extra filters, fake installation claims and decorative stock imagery.',824,594,396,13,'muted')

# 09. Website
page('08 / Public website','One screen should explain the offer.','A strong headline, a practical service image and an immediate path to the business model or resident demonstration.')
browser(60,215,842,397,'voltoshare / public website reference')
logo(82,263,156)
text('How it works    Business model    FAQ',491,271,10,'muted')
btn('Resident demo',763,257,116,32,size=10)
text('Shared charging',88,332,37,'ink',True);text('for your building.',88,378,37,'ink',True)
para('One shared infrastructure service.<br/>A clear model for owners and residents.',89,437,340,15)
btn('Explore the model',89,505,164,39,size=12)
image(KIT/'03_Images/voltoshare-charger-garage.jpg',470,313,408,242,'cover',.68)
text('Financed & installed',89,578,12,'green',True);text('Operated & maintained',350,578,12,'green',True);text('Booked through the app',632,578,12,'green',True)
ruleitem('01','Lead with the use case.','Shared home charging is the primary message. The financial model comes next.',945,224,268)
ruleitem('02','Keep the routes obvious.','How it works, business model, FAQ and resident demo. Use plain labels.',945,365,268)
ruleitem('03','Use evidence carefully.','No invented savings, customer logos or environmental impact figures.',945,506,268)

# 10. Business model
page('09 / Business model','Make both payment streams visible.','The building subscription and the household electricity payment have different payers and different units.',source='Source: supplied proposal, p. 1, sections 1–5  |  Layout is a design recommendation')
rect(60,234,325,186,'white','border',r=12);icon('building',83,255,38)
text('Property owner / manager',83,309,23,'ink',True)
para('Monthly subscription<br/><b>per billable apartment</b>',83,352,280,18)
rect(477,234,326,186,'green',r=12);symbol(501,255,43,True);text('VoltoShare',501,313,30,'white',True);text('Finances, installs and operates',501,367,17,'white')
rect(895,234,325,186,'white','border',r=12);icon('household',918,255,38)
text('Resident / household',918,309,23,'ink',True);para('Metered electricity<br/><b>dynamic tariff + markup</b>',918,352,275,18)
arrow(390,329,466,329);arrow(889,329,814,329)
for xx,val,lab in [(60,'20','apartments'),(270,'5','shared chargers'),(480,'20','subscriptions')]:
    text(val,xx,467,54,'green',True);text(lab,xx,534,18,'ink')
para('Proposal example at <b>full occupancy</b>.<br/>Not a universal sizing rule or a deployed site.',60,578,590,16)
rect(762,460,458,177,'tint',r=12)
label('Keep the assumptions visible',788,484)
para('Vacancy billing is unresolved. Subscription prices and installation costs still need validation. Electricity revenue is not the same as electricity margin.',788,521,405,17)

# 11. Tenant desktop
page('10 / Resident application','Availability first. Costs always visible.','The dashboard should answer: can I charge, what have I booked, and what do I owe?',source='All property, household, tariff and account records on pages 11–15 are fictional demo data')
browser(60,211,1160,430,'Lindenhof / resident dashboard / illustrative data')
rect(61,242,180,398,'white')
logo(79,268,143)
for i,n in enumerate(['Overview','Chargers','Bookings','Activity','Vehicles','Household','Invoices']):
    yy=321+i*39
    if i==0:rect(73,yy-8,154,32,'tint',r=6)
    text(n,88,yy,13,'green' if i==0 else 'muted',i==0)
rect(242,242,977,398,'warm')
text('Your building, connected.',266,264,26,'ink',True);text('Lindenhof · Apartment A-12 · Alex',267,302,12,'muted')
pill('Demo · 16 Nov, 14:30',1031,266,size=10,h=24)
smallstat(266,338,213,'Available now','2 / 5','Bay occupancy unverified',True)
smallstat(492,338,213,'Completed sessions','8','November 2026')
smallstat(718,338,213,'Charging cost','CHF 35.84','112.0 kWh · unbilled')
smallstat(944,338,251,'Outstanding invoices','CHF 28.40','October · overdue')
rect(266,458,445,157,'white','border',r=10);label('Your next booking',285,477,size=10);text('Today, 18:00–20:00',285,507,24,'ink',True);text('C03 · Bay P05 · City EV',285,543,14,'muted');btn('Manage booking',285,571,150,29,False,11)
rect(731,458,464,157,'white','border',r=10);text('Find a charger',751,480,21,'ink',True);pill('C01 · available',751,521,size=11);pill('C03 · available',924,521,size=11);text('View the map or use the equivalent charger list.',751,565,12,'muted');btn('Open chargers',1036,575,140,27,size=10)

# 12. Mobile
page('11 / Mobile experience','Three clear moments, one visual language.','Keep the essentials within reach: overview, availability and a reservation review before confirmation.')
for xx,title in [(60,'Overview'),(395,'Chargers'),(730,'Review booking')]:phone(xx,214,276,409,title)
smallstat(78,310,240,'Available now','2 / 5','Bay occupancy unverified',True)
rect(78,423,240,105,'white','border',r=10);text('Your next booking',91,437,11,'muted');text('Today, 18:00–20:00',91,462,18,'ink',True);text('C03 · P05 · City EV',91,494,12,'muted')
text('November cost',79,542,11,'muted');text('CHF 35.84',318,539,18,'ink',True,'right');mnav(60,569,276)
for i,(cid,st,fg,bg) in enumerate([('C01 · P03','Available','green','tint'),('C02 · P04','Charging','blue','bluebg'),('C03 · P05','Available','green','tint'),('C04 · P13','Reserved','amber','amberbg'),('C05 · P14','Offline','neutral','neutralbg')]):
    yy=309+i*45;rect(413,yy,240,39,'white','border',r=6);text(cid,424,yy+12,12,'ink',True);pill(st,551 if st!='Available' else 546,yy+7,fg,bg,9,24)
mnav(395,569,276,'Chargers')
text('C01 · Bay P03',748,312,21,'green',True);text('Tuesday, 17 November',748,351,14,'ink');text('18:00–20:00',748,378,22,'ink',True);text('City EV',748,417,15,'muted')
line(748,449,988,449);text('Indicative rate',748,467,12,'muted');text('CHF 0.32/kWh',748,491,21,'ink',True);text('Dynamic rate, not price-locked.',748,523,10,'muted');btn('Confirm demo booking',748,557,240,44,size=13)
para('Designed for<br/>small screens',1028,226,192,21,'ink',True,26)
para('Use a list as the primary charger view on mobile. Keep the map available as an alternative.',1028,307,192,16)
para('Before confirming, show the charger, bay, date, interval, vehicle and indicative price.',1028,421,192,16)
para('The review shown here is an unsubmitted draft. It is not counted in the baseline totals.',1028,548,192,13)

# 13. Parking
page('12 / Parking & status','A charger state is not a parking sensor.','Map charger IDs to physical bay numbers. Keep an equivalent list and distinguish occupancy from electrical availability.')
parking(60,228,810,307)
label('Entry',61,549,size=10);label('Pedestrian exit',707,549,size=10)
pill('Available',60,590);pill('Charging',187,590,'blue','bluebg');pill('Reserved',314,590,'amber','amberbg');pill('Offline',445,590,'neutral','neutralbg')
text('At the demo clock',914,229,25,'ink',True)
para('<b>C01 / P03</b> available now.<br/><b>C03 / P05</b> available now, booked at 18:00.<br/><b>C02 / P04</b> charging.<br/><b>C04 / P13</b> reserved until 16:00.<br/><b>C05 / P14</b> offline.',914,281,300,18,leading=31)
rect(914,482,306,129,'tint',r=10);para('<b>Bay occupancy unverified</b><br/>No parked-car status is inferred from the charger state. Other households stay anonymous.',934,503,266,15)

# 14. Costs and invoices
page('13 / Costs & invoices','Show what was used, billed and paid.','Keep charging activity and unpaid invoices separate. Every amount needs a period, a unit and a state.')
smallstat(60,221,346,'November activity','CHF 35.84','8 completed sessions · 112.0 kWh',True)
smallstat(430,221,346,'November bookings','10','8 completed · 1 upcoming · 1 cancelled')
smallstat(800,221,420,'Outstanding invoices','CHF 28.40','October invoice · overdue')
rect(60,350,716,252,'white','border',r=12)
text('Invoice overview',83,375,24,'ink',True)
for xx,s in [(83,'Period'),(318,'Amount'),(483,'Status')]:text(s,xx,426,12,'muted',True)
for yy,per,amt,st,fg,bg in [(461,'September 2026','CHF 31.20','Paid','green','tint'),(511,'October 2026','CHF 28.40','Overdue','red','redbg'),(561,'November usage','CHF 35.84','Unbilled','neutral','neutralbg')]:
    line(83,yy-13,751,yy-13);text(per,83,yy,16);text(amt,318,yy,16,'ink',True);pill(st,483,yy-5,fg,bg,11,27)
rect(800,350,420,252,'graphite',r=12)
label('Illustrative rate only',825,375,'white')
text('CHF 0.28',825,420,29,'white',True);text('energy / kWh',1013,431,14,'white')
text('+ CHF 0.04',825,470,29,'white',True);text('markup / kWh',1013,481,14,'white')
line(825,516,1195,516,'strong');text('CHF 0.32 / kWh',825,541,33,'white',True)
text('Demo only. Dynamic rate. Taxes and extra fees set to zero for illustration. A reservation does not lock a tariff.',60,624,13,'muted')

# 15. Evidence & financial design
page('14 / Numbers & evidence','Make the economics easy to question.','Use labels and explicit assumptions so the audience can follow the model and challenge it constructively.')
rect(60,220,730,371,'white','border',r=12)
text('Subscription revenue',87,246,24,'ink',True)
text('Billable apartments × monthly subscription',87,289,26,'green',True)
line(87,338,764,338)
text('Energy margin contribution',87,369,24,'ink',True)
text('Metered kWh × provider markup per kWh',87,412,26,'green',True)
para('Neither line is profit. Evaluate installation, hardware, platform, maintenance, support and other costs separately.',87,483,640,18)
ruleitem('01','Label scenarios.','State the occupancy rule, tariff assumptions and time period beside the result.',837,223,365)
ruleitem('02','Use honest charts.','Use direct labels, clear units and consistent scales. Use zero baselines for bar charts.',837,363,365)
ruleitem('03','Keep sources close.','Put evidence in the slide footer and details in speaker notes. Mark unvalidated inputs.',837,503,365)
text('No financial return, investment recommendation or guaranteed saving is implied by these illustrative model expressions.',60,624,12,'muted')

# 16. Presentation
page('15 / Presentation system','One argument per slide.','The editable six-slide starter carries the same identity into the graded presentation. Add the team’s research and evidence.')
for i in range(6):
    xx=60+(i%3)*394;yy=215+(i//3)*196
    image(KIT/'06_Presentation/previews'/f'slide-{i+1:02}.png',xx,yy,372,158,'contain')
    names=['The service','The shared configuration','Who pays for what','The resident journey','The economic assumptions','Open questions']
    text(f'{i+1:02}  {names[i]}',xx,yy+165,13,'muted')
para('<b>16:9 format</b> · Content titles 32–44 pt · Body 18–24 pt · Display titles may be larger · Table labels and source notes may be smaller · Install the bundled fonts before editing.',60,622,1160,14)

# 17. Handoff
page('16 / Asset handoff','A practical kit for the whole project.','The ZIP contains the implementation Markdown and reusable assets. Keep the folder structure intact when handing it to OpenClaw.')
rows=[('01_Guidelines','This polished PDF','Human review and brand decisions'),('02_Logos','7 SVG + 7 transparent PNG variants','Website, slides and documents'),('03_Images','Concept imagery + 8 SVG / PNG icons','Hero visuals and interface graphics'),('04_Fonts','Liberation Sans + licence','Consistent editable typography'),('05_Website','Markdown, HTML demo, CSS and JSON','AI brief, reference behaviour and design tokens'),('06_Presentation','PPTX, PDF preview, 6 PNG slides, source','Editable presentation starter'),('07_References','Original supplied artwork and proposal','Traceability and source comparison')]
for i,(folder,contents,use) in enumerate(rows):
    yy=222+i*51
    if i%2==0:rect(60,yy-8,1160,46,'white',r=5)
    text(folder,77,yy,16,'green',True);text(contents,302,yy,16,'ink');text(use,811,yy,15,'muted')
rect(60,602,1160,39,'green',r=7);text('AI entry point: 05_Website/OPENCLAW_IMPLEMENTATION_GUIDE.md',80,614,16,'white',True)

# 18. Source boundary
page('17 / Sources & decisions','A coherent design, with honest boundaries.','Use these guidelines as the visual standard. Treat the commercial proposal and validated project research as the evidence base.')
text('What this guide is based on',60,223,25,'ink',True)
para('<b>Provided proposal.</b> VoltoShare_Expose_DE(1).pdf, page 1, dated 15 October 2026. Service, payer split, 20/5/20 example, operations and open vacancy decision.',60,271,550,17)
para('<b>Provided artwork.</b> Eight logo, icon and product/garage images. Product photographs are supplied concept visuals. The new SVGs are cleaned vector reconstructions of the raster artwork, not original source vectors.',60,378,550,17)
para('<b>Original design work.</b> Layouts, interface recommendations, line icons, presentation templates and fictional demo records.',60,510,550,17)
text('What remains to be confirmed',676,223,25,'ink',True)
para('Subscription amount; installation costs; vacancy billing; tariff source; taxes and fees; billing cycle; cancellation and no-show rules; final household permissions; hardware and payment integrations.',676,271,540,17)
text('Technical references',676,385,25,'ink',True)
para('Liberation Fonts: Arial-compatible metrics and SIL Open Font License. Exact original editable font is not identifiable from the supplied images.',676,429,540,16)
text('github.com/liberationfonts/liberation-fonts',676,489,14,'green')
c.linkURL('https://github.com/liberationfonts/liberation-fonts',(676,H-507,1110,H-486),relative=0)
para('W3C WCAG 2.2: target AA for the implemented website. Accessibility requires testing the actual interface.',676,524,540,16)
text('w3.org/TR/WCAG22/',676,581,14,'green')
c.linkURL('https://www.w3.org/TR/WCAG22/',(676,H-601,1000,H-579),relative=0)
text('Prepared for VoltoShare · Ökonomie der Elektromobilität · Design version 2.0',60,622,13,'muted')

c.save()
# Layout audit is optional; the final PDF is written to 01_Guidelines.
print(str(OUT));print('Pages:',PAGE)
