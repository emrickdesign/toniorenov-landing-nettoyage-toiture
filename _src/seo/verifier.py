#!/usr/bin/env python3
"""Couverture des mots-clés du groupe : python3 _src/seo/verifier.py <page>
Compte chaque mot-clé (accents/majuscules ignorés, mots exacts) dans le texte visible de la
page SANS ses anciennes sections mots-clés + les sections de _src/seo/<page>.json."""
import json, re, html, sys, os, unicodedata
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(D))
def norm(s):
    s = unicodedata.normalize('NFKD', s.lower()); s = ''.join(c for c in s if not unicodedata.combining(c))
    return ' ' + re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', s)).strip() + ' '
pg = sys.argv[1]
k = json.load(open(f'{D}/{pg}.keywords.json'))
raw = open(f'{R}/{pg}/index.html', encoding='utf-8').read()
raw = re.sub(r'(?s)<section class="sec sec-light kw[^"]*".*?</section>', '', raw)
raw = re.sub(r'(?s)<(script|style)\b.*?</\1>', '', raw)
page = norm(html.unescape(re.sub(r'<[^>]+>', ' ', raw)))
j = json.load(open(f'{D}/{pg}.json')) if os.path.exists(f'{D}/{pg}.json') else {'sections': []}
titres = ' '.join([s['h2'] for s in j['sections']] + [i['q'] for s in j['sections'] for i in s['items']])
neuf = ' '.join([s['h2'] + ' ' + s['lead'] for s in j['sections']] + [i['q'] + ' ' + i['a'] for s in j['sections'] for i in s['items']])
neuf_n, tit_n = norm(re.sub(r'<[^>]+>', ' ', neuf)), norm(titres)
mots = len(neuf_n.split())
manque = [m for m in k['mots_cles'] if (page + neuf_n).count(norm(m)) == 0]
print(f'{pg} : {len(j["sections"])} sections, {mots} mots ajoutés, title {len(j.get("title",""))} car., desc {len(j.get("desc",""))} car.')
print(f'Mots-clés absents ({len(manque)}) :', ' | '.join(manque) or 'aucun')
for m in k.get('principaux', []):
    n, t = neuf_n.count(norm(m)), tit_n.count(norm(m))
    ok = 'OK ' if n >= 4 and t >= 1 else '-- '
    print(f'  {ok}{m} : {n} fois dans les sections, {t} dans un H2/H3, title {"oui" if norm(m) in norm(j.get("title","")) else "non"}')
