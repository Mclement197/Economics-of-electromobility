#!/usr/bin/env python3
"""Check the authorized first 17 slides against the untouched full source PPTX.

Standard library only. Shape order/position, font styling and decorative logos
may change. Source text, pictures, chart data, notes and hidden flags may not.
The browser transcript is independently extracted from source Office XML.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import posixpath
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


def values(node, path):
    return [e.text or '' for e in node.findall(path, NS)]


def textframe(node):
    """Office text semantics: paragraphs use LF, soft line breaks use VT."""
    result = []
    for paragraph in node.findall('a:p', NS):
        parts = []
        for child in paragraph:
            if child.tag == '{' + NS['a'] + '}br':
                parts.append('\v')
            else:
                parts.extend(values(child, './/a:t'))
        result.append(''.join(parts))
    return '\n'.join(result)


class Package:
    def __init__(self, path):
        self.path = path
        self.zip = ZipFile(path)
        manifest = self.xml('ppt/presentation.xml')
        rels = self.rels('ppt/presentation.xml')
        self.slides = [rels[s.get('{' + NS['r'] + '}id')]
                       for s in manifest.findall('p:sldIdLst/p:sldId', NS)]

    def xml(self, path):
        return ET.fromstring(self.zip.read(path))

    def rels(self, path):
        dirname, basename = posixpath.split(path)
        relfile = posixpath.join(dirname, '_rels', basename + '.rels')
        if relfile not in self.zip.namelist():
            return {}
        return {r.get('Id'): posixpath.normpath(posixpath.join(dirname, r.get('Target')))
                for r in self.xml(relfile) if r.get('TargetMode') != 'External'}

    def read_slide(self, path):
        root = self.xml(path)
        rels = self.rels(path)
        charts = [self.xml(rels[c.get('{' + NS['r'] + '}id')])
                  for c in root.findall('.//c:chart', NS)]
        images = Counter(hashlib.sha256(self.zip.read(rels[blip.get('{' + NS['r'] + '}embed')])).hexdigest()
                         for pic in root.findall('.//p:pic', NS)
                         for blip in pic.findall('.//a:blip', NS)
                         if blip.get('{' + NS['r'] + '}embed'))
        notes = next((self.xml(target) for target in rels.values()
                      if '/notesSlides/' in target and target.endswith('.xml')), None)
        note_body = ''
        if notes is not None:
            for shape in notes.findall('.//p:sp', NS):
                ph = shape.find('p:nvSpPr/p:nvPr/p:ph', NS)
                if ph is not None and ph.get('type') == 'body':
                    tf = shape.find('p:txBody', NS)
                    note_body = textframe(tf) if tf is not None else ''
        texts = []

        def walk(tree):
            for shape in tree:
                if shape.tag == '{' + NS['p'] + '}grpSp':
                    yield from walk(shape)
                else:
                    yield shape

        for shape in walk(root.find('p:cSld/p:spTree', NS)):
            tf = shape.find('p:txBody', NS)
            if tf is not None:
                text = textframe(tf)
                if text.strip():
                    texts.append(text)
            for table in shape.findall('.//a:tbl', NS):
                texts.extend(' · '.join(textframe(cell.find('a:txBody', NS))
                                       for cell in row.findall('a:tc', NS))
                             for row in table.findall('a:tr', NS))
        return {
            'text_runs': Counter(values(root, './/a:t')),
            'paragraphs': Counter(textframe(tf) for tf in root.findall('.//p:txBody', NS) if textframe(tf).strip()),
            'images': images,
            'tables': [values(t, './/a:t') for t in root.findall('.//a:tbl', NS)],
            'chart_cache': [values(c, './/c:v') for c in charts],
            'chart_text': [values(c, './/a:t') for c in charts],
            'charts': [chart_model(c) for c in charts],
            'notes_runs': Counter(values(notes, './/a:t')) if notes is not None else Counter(),
            'notes': note_body,
            'text': texts,
            'hidden': root.get('show') == '0',
        }


def chart_model(chart):
    result = {'title': '', 'categories': [], 'series': []}
    title = chart.find('c:chart/c:title/c:tx/c:rich', NS)
    if title is not None:
        result['title'] = textframe(title)
    for i, series in enumerate(chart.findall('.//c:ser', NS)):
        tx = series.find('c:tx', NS)
        name = ''.join(values(tx, './/c:v')) if tx is not None else ''
        if i == 0:
            cat = series.find('c:cat', NS)
            result['categories'] = values(cat, './/c:pt/c:v') if cat is not None else []
        val = series.find('c:val', NS)
        result['series'].append({'name': name,
                                 'values': [float(v) for v in values(val, './/c:pt/c:v')] if val is not None else []})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path.home() / '.local/state/voltoshare/source-2026-11-24/Voltoshare_Slides_Final.pptx')
    parser.add_argument('--pptx', type=Path, default=ROOT / 'website-src/downloads/VoltoShare-Praesentation.pptx')
    parser.add_argument('--manifest', type=Path, default=ROOT / 'website-src/presentation-data.json')
    parser.add_argument('--skip-browser', action='store_true', help='Development-only: audit the PPTX before browser assets have been regenerated.')
    args = parser.parse_args()
    source, target = Package(args.source), Package(args.pptx)
    failures = []
    checks = 0

    def check(ok, label):
        nonlocal checks
        checks += 1
        if not ok:
            failures.append(label)

    check(len(source.slides) >= 17, 'Source does not contain 17 slides')
    included = source.slides[:17]
    check(len(target.slides) == 17, 'PPTX must end after source slide 17')
    actual_slide_parts = [name for name in target.zip.namelist() if name.startswith('ppt/slides/slide') and name.endswith('.xml')]
    check(len(actual_slide_parts) == 17, 'PPTX retains unwanted appendix slide parts')
    browser = None
    if not args.skip_browser:
        browser = json.loads(args.manifest.read_text())
        check(len(browser['slides']) == 17, 'Browser must end after source slide 17')
        check(browser.get('includedSourceSlides') == list(range(1,18)), 'Browser source scope differs')
        check(browser.get('sourceSha256') == hashlib.sha256(args.source.read_bytes()).hexdigest(), 'Browser source hash differs')
        check(browser.get('revision') == hashlib.sha256(args.pptx.read_bytes()).hexdigest()[:12], 'Browser revision does not match the downloadable PPTX')

    for index, source_path in enumerate(included):
        if index >= len(target.slides):
            break
        original, redesigned = source.read_slide(source_path), target.read_slide(target.slides[index])
        label = f'Slide {index + 1}'
        for key in ['text_runs', 'paragraphs', 'tables', 'chart_cache', 'chart_text', 'notes_runs', 'notes', 'hidden']:
            check(original[key] == redesigned[key], f'{label}: {key} differs')
        check(not (original['images'] - redesigned['images']), f'{label}: source picture blobs were removed/replaced')
        if browser is not None and index < len(browser['slides']):
            published = browser['slides'][index]
            check(published.get('number') == index + 1, f'{label}: browser order differs')
            for key in ['text', 'charts', 'notes', 'hidden']:
                check(published.get(key) == original[key], f'{label}: browser {key} differs')
            image = published.get('image', '')
            asset = ROOT / 'website-src' / image.split('?', 1)[0].lstrip('/')
            check(image.startswith('/assets/slides/') and asset.is_file(), f'{label}: browser artwork missing')
            check(asset.suffix == '.png', f'{label}: browser must use stable raster artwork')
    if browser is not None:
        assets = ROOT / 'website-src/assets/slides'
        check({p.name for p in assets.glob('slide-*.svg')} == {f'slide-{i:02d}.svg' for i in range(1,18)}, 'Browser artwork directory retains obsolete appendix pages')
        check({p.name for p in assets.glob('slide-*.png')} == {f'slide-{i:02d}.png' for i in range(1,18)}, 'Browser raster directory must contain exactly 17 pages')
    if failures:
        print(f'FAIL: {len(failures)} of {checks} fidelity checks failed')
        print('\n'.join(f'  - {f}' for f in failures))
        return 1
    print(f'PASS: {checks} fidelity checks across the first {len(included)} source slides; exact source text, notes, chart values, images and hidden flags preserved' + ('; browser export pending' if args.skip_browser else '; browser transcript and revision match'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
