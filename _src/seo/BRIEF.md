# Sections « score de qualité » d'une landing page Google Ads

Étape faite APRÈS que les mots-clés du groupe d'annonces sont posés. Le haut de la page
(hero, avis, photos, zone, formulaire du bas, FAQ) ne bouge pas. On ajoute, sous la FAQ,
3 à 5 sections en dépliants qui reprennent les mots-clés du groupe.

## Ce que Google regarde (expérience sur la page de destination)

1. **Pertinence** : la page parle du mot-clé tapé et de l'intention derrière (prix, urgence,
   ville, type de travaux). Le mot-clé exact doit se lire sur la page, au mieux dans un titre.
2. **Contenu utile et original** : des réponses vraies et concrètes, pas une liste de
   mots-clés. Pas de paragraphes copiés d'une ville à l'autre en changeant juste le nom.
3. **Transparence et confiance** : qui intervient, où, comment le prix se fixe, ce qui est
   garanti. Aucune promesse inventée.
4. **Navigation facile, mobile d'abord, page rapide** : déjà traité par le haut de la page,
   les dépliants gardent la page courte.

Le niveau de qualité se calcule sur les recherches EXACTES du mot-clé : les gros mots-clés
sans ville (« nettoyage toiture », « ravalement façade »…) comptent le plus.

## Règles d'écriture

- Chaque section : un **H2** qui contient un mot-clé principal exact, une phrase d'intro
  (lead, 1 à 2 phrases, `<strong>` autorisé sur le mot-clé), puis 3 à 6 dépliants.
- Chaque dépliant : une **question ou un intitulé (H3)** qui contient un mot-clé exact, et une
  réponse de 2 à 4 phrases (40 à 90 mots) qui en glisse 1 ou 2 autres naturellement.
- **Tous les mots-clés du fichier `<page>.keywords.json` apparaissent au moins une fois**,
  écrits mot pour mot dans le même ordre (les accents et les majuscules peuvent varier, les
  mots ne doivent pas changer : « nettoyage toiture » ≠ « nettoyage de toiture »).
- **Les mots-clés principaux** (liste donnée dans ta mission) : au moins 4 fois chacun dans
  tes sections, dont 1 fois dans un H2 ou un H3.
- Les mots-clés « + ville » : une section « [mot-clé principal] à Bayonne, Anglet, Biarritz,
  Boucau… » avec un dépliant par ville. Chaque réponse dit quelque chose de différent et de
  vrai (Boucau = la base de Tonio ; les autres : distance, type de maisons de façon générale
  et prudente, mêmes conditions). Une ville absente de la zone d'intervention de la page :
  ne l'écris pas, signale-la dans ton rapport.
- Formes maladroites (« entreprise entretient façade », « nettoyage crepis maison »,
  « peintre d intérieur ») : place-les dans une phrase où elles passent (titre court,
  citation de ce que les gens tapent : « Vous cherchez un “peintre d intérieur autour de
  moi” ? »). Jamais de liste de mots-clés brute.
- Vouvoiement, phrases simples, ton d'artisan. Pas de tiret long (—). Pas de formules
  creuses (« n'hésitez pas », « de qualité », « expertise »).
- Longueur totale : 600 à 1 100 mots pour toutes les sections.

## Ce qui est vrai (n'invente RIEN d'autre)

Lis le bloc de ta page dans `_src/build.py` (ou le HTML de la page pour peinture) : offre,
FAQ, preuves, zone. Faits communs sûrs : Tonio Rénov', artisan basé à Boucau, entreprise
créée en 2009, c'est Tonio qui vient (pas de sous-traitance), devis gratuit fait sur place,
le prix du devis est le prix payé, photos avant/après, 5/5 sur 7 avis Google, rappel sous
24 h quand la page le dit. Toiture : produits DALEP 2100, basse pression, biocide sans chlore.

INTERDIT : « RGE », « 500 chantiers », un autre nombre d'avis, des fourchettes de prix du
marché, un prix qui n'est pas sur la page, une garantie ou un délai d'intervention qui n'est
pas sur la page, des matériaux ou des marques non cités. Pour un mot-clé « prix », réponds
avec l'offre de la page si elle existe et explique ce qui fait varier le prix ; sinon
« prix ferme donné après visite ».

## Format de sortie : `_src/seo/<page>.json`

```json
{
  "title": "balise <title> : mot-clé principal exact en tête, villes, · Tonio Rénov' (≤ 70 car.)",
  "desc": "meta description 140-160 car. avec le mot-clé principal exact et l'offre",
  "sections": [
    {"h2": "…", "lead": "…", "items": [{"q": "…", "a": "…"}]}
  ]
}
```

HTML autorisé dans `lead` et `a` : `<strong>` seulement. Échappe les guillemets JSON.
Vérifie la couverture avec : `python3 _src/seo/verifier.py <page>`.
