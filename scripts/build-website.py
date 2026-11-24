#!/usr/bin/env python3
"""Dependency-free static page build. Source images/fonts are prepared separately."""
import argparse, json, shutil
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'website-src'
p=argparse.ArgumentParser()
p.add_argument('--out',type=Path,default=ROOT/'build/website')
args=p.parse_args()
out=args.out.resolve()
if out in (ROOT, SRC, ROOT/'sites',ROOT/'sites/app',ROOT/'sites/website'):
    p.error('Build to a staging folder, then deploy the verified build.')
out.mkdir(parents=True,exist_ok=True)
cfg=json.loads((SRC/'config.json').read_text())
if cfg['contactMode']!='demo' or cfg['contactDestination'] is not None:
    raise SystemExit('Only demo enquiry mode is implemented. Configure and verify a backend before enabling live mode.')
if cfg['appStatus'] not in ['placeholder','demo']:
    raise SystemExit('Only verified placeholder or demo app states are supported.')
app_label='App-Demo öffnen' if cfg['appStatus']=='demo' else 'App-Platzhalter ansehen'
app_copy=('Die separate Bewohner-App ist als interaktive Demo mit fiktiven Haushalten verfügbar. Reservierungen, Fahrzeuge und Abrechnungen bleiben gespeichert. Der feste Beispieltarif vereinfacht das geplante dynamische Tarifmodell. Die Darstellung hier bleibt eine illustrative Vorschau.' if cfg['appStatus']=='demo' else 'Die Bewohner-App ist eine separate Produktoberfläche. Aktuell liegt dort nur eine Platzhalterseite vor; die Darstellung hier ist eine illustrative Vorschau.')
if cfg['language']!='de-CH':
    raise SystemExit('Only complete German content exists in this release.')
for file in ['site.css','site.mjs','calculator.mjs','calculator.css','contact.mjs','contact.css',
             'finance-model.mjs','finance-ui.mjs','finance-page.mjs','finance.css',
             'presentation-data.json','presentation.mjs','presentation.css']:
    shutil.copy2(SRC/file,out/file)
# Mirror viewport layouts as container queries: content also reflows under CSS
# zoom or embedded/narrow containers, instead of relying only on viewport width.
for cssfile in ['site.css','calculator.css','contact.css']:
    css=(out/cssfile).read_text()
    blocks=[]
    import re
    for match in re.finditer(r'@media\(max-width:[0-9]+px\)\{',css):
        start=match.start(); end=match.end(); depth=1
        while depth and end<len(css):
            depth += (css[end]=='{') - (css[end]=='}'); end+=1
        blocks.append(css[start:end].replace('@media','@container',1))
    (out/cssfile).write_text(css+'\n'+('body{container-type:inline-size}\n' if cssfile=='site.css' else '')+'\n'.join(blocks))
shutil.copytree(SRC/'assets',out/'assets',dirs_exist_ok=True)
shutil.copytree(SRC/'downloads',out/'downloads',dirs_exist_ok=True)
shutil.copy2(SRC/'assets/symbol.svg',out/'favicon.svg')
for size,name in [(180,'apple-touch-icon.png'),(192,'icon-192.png'),(512,'icon-512.png')]:
    shutil.copy2(SRC/'assets'/name,out/name)
(out/'site.webmanifest').write_text(json.dumps({'name':'VoltoShare – Projektkonzept','short_name':'VoltoShare','lang':'de-CH','start_url':'/','display':'standalone','background_color':'#F8F5F0','theme_color':'#F8F5F0','icons':[{'src':f'/icon-{n}.png','sizes':f'{n}x{n}','type':'image/png'} for n in [192,512]]}))
header='''<a class="skip-link" href="#main">Zum Inhalt springen</a><div class="status-strip"><div class="wrap"><span>'''+escape(cfg['projectStatus'])+'''</span><span>Gemeinsam genutzte Ladeinfrastruktur</span></div></div><header class="site-header"><div class="header-inner wrap"><a class="brand" href="/" aria-label="VoltoShare – Startseite"><img src="/assets/logo-navigation.svg" alt="VoltoShare" width="200" height="35"></a><button class="menu-toggle" type="button" aria-controls="site-nav" aria-expanded="false">Menü <span aria-hidden="true">☰</span></button><nav class="site-nav" id="site-nav" aria-label="Hauptnavigation"><a href="/#loesung">Konzept</a><a href="/geschaeftsmodell/">Geschäftsmodell</a><a href="/finanzen/">Finanzen</a><a href="/#praesentation">Präsentation</a><a class="button" href="'''+escape(cfg['appUrl'])+'''">'''+app_label+''' <span aria-hidden="true">↗</span></a></nav></div></header>'''
footer='''<footer class="site-footer"><div class="wrap"><div class="footer-top"><div class="footer-brand"><img src="/assets/logo-white.svg" alt="VoltoShare – Gemeinsam genutzte Ladeinfrastruktur" width="320" height="72"><p>Gemeinsam genutzte Ladeinfrastruktur<br>für Mietwohngebäude.</p></div><nav class="footer-nav" aria-label="Weitere Seiten"><div><strong>Das Konzept</strong><a href="/#loesung">Die Lösung</a><a href="/geschaeftsmodell/">Geschäftsmodell</a><a href="/finanzen/">Finanzen</a><a href="/praesentation/">Präsentation</a></div><div><strong>Projekt &amp; Hinweise</strong><a href="'''+escape(cfg['appUrl'])+'''">'''+app_label+''' ↗</a><a href="/impressum/">Projekthinweise / Impressum</a><a href="/datenschutz/">Datenschutz</a></div></nav></div><div class="footer-bottom"><span>VoltoShare · Projektkonzept · Ökonomie der Elektromobilität</span><span>Arbeitsentwurf · Markt, Produkt und Finanzszenarien</span></div></div></footer>'''
for page in cfg['pages']:
    content=(SRC/'pages'/f"{page['file']}.html").read_text()
    content=content.replace('{{APP_LABEL}}',app_label).replace('{{APP_STATUS_COPY}}',app_copy)
    content=content.replace('{{APP_URL}}',escape(cfg['appUrl'])).replace('{{WINDOWS}}','<i></i>'*20).replace('{{BAYS}}',''.join(f'<div class="bay"><img src="/assets/icons/icon-charger.svg" width="24" height="24" alt=""><span>{i:02}</span></div>' for i in range(1,6)))
    canonical=cfg['siteUrl']+'/'+(page['slug']+'/' if page['slug'] else '')
    title=escape(page['title']+' | VoltoShare')
    extra=''
    if page['file'] in ['home','presentation']:extra='<link rel="stylesheet" href="/finance.css"><link rel="stylesheet" href="/presentation.css"><script type="module" src="/presentation.mjs"></script>'
    if page['file']=='finance':extra='<link rel="stylesheet" href="/finance.css"><script type="module" src="/finance-page.mjs"></script>'
    if page['file']=='economics':extra='<link rel="stylesheet" href="/calculator.css"><script type="module" src="/calculator.mjs"></script>'
    if page['file'] in ['contact','privacy','imprint']:extra='<link rel="stylesheet" href="/contact.css"><script type="module" src="/contact.mjs"></script>'
    current_header=header
    if page['slug']:
        current_header=header.replace(f'href="/{page["slug"]}/"',f'href="/{page["slug"]}/" aria-current="page"')
    html=f'''<!doctype html><html lang="{cfg['language']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="#F8F5F0"><meta name="color-scheme" content="light"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="default"><meta name="robots" content="noindex, nofollow"><title>{title}</title><meta name="description" content="{escape(page['description'])}"><link rel="canonical" href="{canonical}"><meta property="og:title" content="{title}"><meta property="og:description" content="{escape(page['description'])}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{cfg['siteUrl']}/assets/social.png"><meta property="og:locale" content="de_CH"><link rel="icon" type="image/svg+xml" href="/favicon.svg"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="preload" href="/assets/fonts/LiberationSans-Regular.ttf" as="font" type="font/ttf" crossorigin><link rel="stylesheet" href="/assets/tokens.css"><link rel="stylesheet" href="/site.css"><script type="module" src="/site.mjs"></script>{extra}</head><body>{current_header}<main id="main" tabindex="-1">{content}</main>{footer}</body></html>'''
    dest=out/page['slug'];dest.mkdir(parents=True,exist_ok=True);(dest/'index.html').write_text(html)
(out/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
print(f'Built {len(cfg["pages"])} German pages in {out}; project scenarios and presentation, demo enquiries only.')
