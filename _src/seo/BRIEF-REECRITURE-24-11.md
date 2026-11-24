# Réécriture des sections mots-clés : 24/11/2026

Emrick : les textes du bas des LP (sous la carte des villes) ont été écrits pour le score de
qualité Google Ads, avec des mots-clés empilés. Un particulier ne les comprend plus : « ce n'est
pas du français ». On les réécrit en français naturel et clair **en gardant tous les mots-clés**,
pour garder le score de qualité et les annonces « Excellente ».

## Ce que tu touches

- Uniquement `_src/seo/<page>.json`, et dedans uniquement les sections dont `"mode"` n'est PAS
  `"carte"`. La section `"mode": "carte"` (carte des villes) est validée par Emrick : tu ne la
  modifies pas (ni son H2, ni son lead, ni ses items).
- Tu peux réécrire : `h2`, `lead`, `q` (devient le H3), `a`, `tag` (étiquette sur la photo,
  2 à 4 mots). Tu gardes `img`, `ic`, `mode`, `alt`, `foot` tels quels (tu peux changer `ic`
  parmi les icônes de `ICONS` dans `_src/build.py` si l'étiquette change de sens).
- `title` et `desc` : ne pas toucher.
- Tu peux ajouter ou retirer un item dans une section, garder 3 à 6 items par section.
- Ne lance PAS `build.py`, ne fais PAS de commit. Un autre agent travaille sur chacune des
  autres pages : ne touche à aucun autre fichier.

## Le test : un particulier qui lit à voix haute

Chaque phrase doit pouvoir être dite par Tonio à un client, au téléphone, sans qu'il fronce les
sourcils. Phrases complètes, sujet-verbe-complément, articles et prépositions à leur place.

Mauvais (actuel) :
> « Fuite au toit, fuite sur le toit ou fuite toit : c'est l'eau que vous voyez couler. Toiture
> infiltration ou fuite dans la toiture, il y a un point précis que Tonio localise avant de réparer. »

Bon :
> « Quand l'eau coule au plafond, c'est une fuite sur le toit. Une infiltration par la toiture est
> plus lente : une auréole qui grandit, une odeur d'humidité dans les combles. Dans les deux cas,
> Tonio cherche le point précis par où l'eau passe avant de réparer. »

## Garder les mots-clés sans casser la phrase

Le contrôle ignore les accents, les majuscules et **la ponctuation** : il cherche les mots dans
le même ordre. Donc :

1. **D'abord, la forme naturelle contiguë** : « la réparation de toiture » ne compte PAS pour
   « réparation toiture » (« de » s'intercale). Cherche une tournure où les mots se suivent
   naturellement : « un devis de réparation toiture », « Réparation toiture : ce que fait Tonio »
   (titre), « votre toiture qui fuit ».
2. **La ponctuation peut séparer les mots** quand ça se lit bien : « Fuite toiture : réparation
   garantie 2 ans » compte pour « fuite toiture réparation » ; « peintre d'intérieur » compte pour
   « peintre d intérieur » ; « Urgence, toiture qui fuit » compte pour « urgence toiture ».
   Les titres courts (H3, étiquettes) s'y prêtent bien : « Démoussage toiture : le prix ».
3. **Les formes vraiment tordues** (« toiture infiltration », « entreprise 24h toiture »,
   « nettoyage crepis maison ») : une seule fois chacune, citée comme ce que les gens tapent,
   et au maximum UNE citation de ce genre par réponse : « Vous avez cherché « entreprise 24h
   toiture » ? Tonio ne promet pas de venir à toute heure, il promet de décrocher. »
   Jamais d'énumération de variantes (« X, Y ou Z : c'est pareil »).
4. Les mots-clés principaux (liste sortie par le contrôle) : garde au moins le nombre indiqué
   et au moins un dans un H2 ou un H3. Inutile de les répéter plus : le but est la lisibilité.

## Règles de ton (Emrick)

- Vouvoiement, ton d'artisan, phrases courtes. 2 à 4 phrases par réponse (40 à 90 mots).
- Aucun tiret long ni moyen (— –). Pas de « n'hésitez pas », « de qualité », « expertise »,
  « sublimer », « incontournable », pas de formules creuses, pas de triplets forcés, pas de
  phrase-slogan en fin de paragraphe.
- Jamais plus de 2 fois le même nom de ville dans une réponse.
- Le H2 et les H3 restent courts et clairs (une idée, un mot-clé dedans).

## Ce qui est vrai (n'invente RIEN)

Lis le bloc de ta page dans `_src/build.py` (dict de `PAGES` dont `out` commence par le nom de
ta page) et le texte actuel de `_src/seo/<page>.json` : n'utilise que les faits qui y sont
déjà (offre, prix, délais, garanties, produits). Faits sûrs : Tonio Rénov', artisan basé à
Boucau, entreprise créée en 2009, c'est Tonio qui vient (pas de sous-traitance), devis gratuit
fait sur place, le prix du devis est le prix payé, photos avant/après, rappel sous 24 h.
INTERDIT : « RGE », « 500 chantiers », un nombre d'avis, un prix ou une garantie absents de la
page, des fourchettes de prix du marché, des marques non citées.

## Contrôle (à lancer jusqu'à « ABSENTS (0) », principaux tous « OK », « TICS : aucun »)

    python3 _src/seo/controle_reecriture.py <page>

Rends : le nombre de mots-clés absents (doit être 0), la liste des principaux avec leurs
comptes, et 3 exemples avant → après de phrases que tu as le plus débloquées.
