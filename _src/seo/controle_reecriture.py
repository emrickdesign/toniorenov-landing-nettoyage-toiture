#!/usr/bin/env python3
"""Contrôle de la réécriture du 24/11/2026 : python3 _src/seo/controle_reecriture.py <page>
Compte chaque mot-clé (accents, majuscules et ponctuation ignorés, mots exacts dans le même ordre) dans :
le texte visible de la page SANS aucune section mots-clés + title/desc + TOUTES les sections de _src/seo/<page>.json.
Compare au relevé d'avant (_src/seo/avant-reecriture-24-11.json). Signale aussi les tics interdits."""
import json, re, html, sys, os, unicodedata
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(D))
def norm(s):
    s = unicodedata.normalize('NFKD', s.lower()); s = ''.join(c for c in s if not unicodedata.combining(c))
    return ' ' + re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', s)).strip() + ' '
pg = sys.argv[1]
k = json.load(open(f'{D}/{pg}.keywords.json'))
avant = json.load(open(f'{D}/avant-reecriture-24-11.json'))[pg]
raw = open(f'{R}/{pg}/index.html', encoding='utf-8').read()
body = raw.split('<body>', 1)[1]
body = re.sub(r'(?s)<section class="sec sec-(?:light|dark|nuit) kw[^"]*".*?</section>', '', body)
body = re.sub(r'(?s)<(script|style)\b.*?</\1>', '', body)
body = re.sub(r'aria-label="[^"]*"', '', body)
j = json.load(open(f'{D}/{pg}.json'))
txt = [j.get('title', ''), j.get('desc', '')]
for s in j['sections']:
    txt += [s['h2'], s['lead']]
    for i in s['items']: txt += [i['q'], i['a'], i.get('tag', '')]
neuf = ' '.join(txt)
page = norm(html.unescape(re.sub(r'<[^>]+>', ' ', body + ' ' + neuf)))
print(f'== {pg} : {len(k["mots_cles"])} mots-clés')
manque = [m for m in k['mots_cles'] if page.count(norm(m)) == 0]
print(f'ABSENTS ({len(manque)}) :', ' | '.join(manque) or 'aucun')
titres = norm(' '.join([s['h2'] for s in j['sections']] + [i['q'] for s in j['sections'] for i in s['items']]))
for m in k.get('principaux', []):
    n, t = page.count(norm(m)), titres.count(norm(m))
    flag = 'OK ' if (n >= min(avant[m][0], 4) and t >= 1) else '-- '
    print(f'  {flag}principal « {m} » : {n} fois sur la page (avant {avant[m][0]}), {t} dans un H2/H3')
tics = []
for s in txt:
    for bad in ['—', '–', "n'hésitez", 'de qualité', 'expertise', 'sublimer', 'au cœur de', 'en somme', 'incontournable']:
        if bad in s.lower(): tics.append((bad, s[:70]))
print('TICS :', tics or 'aucun')
mots = len(norm(re.sub(r'<[^>]+>', ' ', ' '.join(txt[2:]))).split())
print(f'{mots} mots dans les sections')
