# Landings Google Ads — Tonio Rénov' (modèle réutilisable par métier)

4 pages, un seul design :

| Groupe d'annonces | URL |
|---|---|
| Démoussage toiture | `/` (nettoyage-toiture.toniorenov.fr) |
| Entretien & traitement | `/entretien` |
| Fuite / urgence | `/urgence` |
| Ravalement façade | `/ravalement` |

## Modifier le design ou le contenu
Tout vient de `_src/` — ne pas éditer les `index.html` à la main (ils sont générés) :

- `_src/style.css` → le design (couleurs, polices, boutons, animations)
- `_src/app.js` → barre au scroll, révélations, suivi GTM (`click_call`, `leads_entrer`), formulaire à choix
- `_src/build.py` → le contenu de chaque page (titres, avis, FAQ, questions du formulaire)

```bash
python3 _src/build.py   # régénère les 4 pages
```

## Nouveau métier
Ajouter un bloc dans `PAGES` (`build.py`), relancer la commande, pousser.
Tracking GTM `GTM-5VBQJ4RZ` : événements `click_call` (clic téléphone) et `leads_entrer` (formulaire terminé).
