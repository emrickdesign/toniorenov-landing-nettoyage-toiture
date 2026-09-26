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

## Numéro affiché
Les pages affichent le **numéro de suivi Twilio `04 15 87 02 42`** (défini dans `SITE` de `build.py`), pas le 06 de Tonio : les appels sont transférés à Tonio, enregistrés, et visibles dans son espace client Potentieel.

## Formulaire
Les demandes sont insérées dans la table `form_submissions` de Supabase avec le `client_id` de Tonio (voir `LEAD` dans `app.js`) : elles apparaissent dans sa fiche admin, puis dans son espace client une fois qualifiées.

## Photos
Photos d'illustration libres de droits (Unsplash) dans `/img` — voir `_src/CREDITS.md`. À remplacer par de vraies photos avant/après du client dès qu'elles existent (même nom de fichier).
