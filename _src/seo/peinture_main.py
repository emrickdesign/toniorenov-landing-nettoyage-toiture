#!/usr/bin/env python3
"""peinture-interieure est éditée À LA MAIN : ce script y greffe les sections de
_src/seo/peinture-interieure.json (remplace les sections .kw), le title, la description et le CSS
des dépliants, sans régénérer la page."""
import os, re, sys, html as H
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(D))
import build
f = os.path.join(os.path.dirname(D), '..', 'peinture-interieure', 'index.html')
s = open(f, encoding='utf-8').read()
p = {'out': 'peinture-interieure/index.html'}
d = build.seo_json(p)
sec = build.typo_fr(build.kw_sections(p))
blocs = list(re.finditer(r'(?s)<section class="sec sec-light kw[^"]*".*?</section>\n?', s))
assert blocs, 'sections kw introuvables'
s = s[:blocs[0].start()] + sec + s[blocs[-1].end():]
t, ds = H.escape(d['title'], quote=True), H.escape(d['desc'], quote=True)
s = re.sub(r'<title>[^<]*</title>', lambda m: '<title>' + H.escape(d['title'], quote=False) + '</title>', s, 1)
s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + ds, s, 1)
s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + t, s, 1)
s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + ds, s, 1)
css = open(os.path.join(os.path.dirname(D), 'style.css'), encoding='utf-8').read()
bloc_css = css[css.index('/* Sections score de qualité en dépliants'):]
if '.kw-acc{' not in s:
    i = s.index('</style>'); s = s[:i] + '\n' + bloc_css + s[i:]
open(f, 'w', encoding='utf-8').write(s)
print('peinture-interieure : %d sections greffées' % len(d['sections']))
