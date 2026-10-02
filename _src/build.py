#!/usr/bin/env python3
"""Génère les 4 landings à partir d'UN design (style.css) et du contenu ci-dessous.
Usage : python3 _src/build.py      (depuis la racine du dépôt)
Pour un nouveau métier : ajouter une entrée dans PAGES, relancer, pousser."""
import re, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = open(os.path.join(ROOT, '_src', 'style.css'), encoding='utf-8').read()
JS = open(os.path.join(ROOT, '_src', 'app.js'), encoding='utf-8').read()

SITE = dict(
    # Numéro de suivi Twilio (pas le 06 direct) : les appels sont transférés à Tonio
    # et tracés dans l'espace client Potentieel. Changer ici = changer les 4 pages.
    name="Tonio Rénov'", phone="04 15 87 02 42", tel="+33415870242",
    email="contact@toniorenov.fr", gtm="GTM-5VBQJ4RZ",
    base="https://nettoyage-toiture.toniorenov.fr",
)
ZONES = ["Boucau", "Bayonne", "Anglet", "Biarritz", "Bidart", "Guéthary", "Saint-Jean-de-Luz",
         "Hendaye", "Urrugne", "Arbonne", "Arcangues", "Tarnos", "Ondres",
         "Saint-Martin-de-Seignanx", "Labenne", "Capbreton"]

ICONS = {
 'phone': '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
 'arrow': '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
 'back': '<path d="M19 12H5"/><path d="m12 19-7-7 7-7"/>',
 'check': '<path d="M20 6 9 17l-5-5"/>',
 'plus': '<path d="M12 5v14"/><path d="M5 12h14"/>',
 'shield': '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
 'shield-check': '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
 'award': '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>',
 'clock': '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
 'home': '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
 'pin': '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
 'drop': '<path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"/>',
 'sprout': '<path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>',
 'layers': '<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
 'waves': '<path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>',
 'search': '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
 'zap': '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
 'alert': '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
 'help': '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
 'crack': '<path d="M13 2v6l-4 3 5 3-3 3v5"/>',
 'roller': '<rect width="16" height="6" x="2" y="2" rx="2"/><path d="M10 16v-2a2 2 0 0 1 2-2h8a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect width="4" height="6" x="8" y="16" rx="1"/>',
 'image': '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
 'lr': '<path d="m9 7-5 5 5 5"/><path d="m15 7 5 5-5 5"/>',
 'tools': '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
}

def ic(name, cls=''):
    return f'<svg class="ic {cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'

STAR = '<svg class="ic ic-fill" viewBox="0 0 24 24" aria-hidden="true"><path d="m12 2 3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/></svg>'
def stars(): return '<span class="stars" role="img" aria-label="5 étoiles sur 5">' + STAR * 5 + '</span>'

# Repère de marque (chevrons du logo) — version claire pour fonds sombres
def mark(light=True):
    big, small = ('#ffffff', '#ff6f58') if light else ('#152c48', '#8c1c2c')
    return (f'<svg viewBox="395 438 620 262" aria-hidden="true">'
            f'<polygon fill="{big}" points="704,442 1008,695 934,695 704,505 476,695 400,695 505,607 505,514 562,514 562,558"/>'
            f'<polygon fill="{small}" points="704,532 901,695 869,695 704,562 539,695 507,695"/></svg>')

def split_words(html, start=0):
    i, out = start, []
    for m in re.finditer(r'(<[^>]+>)|([^<\s]+)|(\s+)', html):
        tag, word, sp = m.groups()
        if tag: out.append(tag)
        elif word:
            out.append(f'<span class="w" style="--i:{i}" aria-hidden="true">{word}</span>'); i += 1
        else: out.append(' ')
    return ''.join(out), i

def plain(html): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip()
def h2(html, extra=''):
    inner, _ = split_words(html)
    return f'<h2 class="split {extra}" aria-label="{plain(html)}">{inner}</h2>'

# ----------------------------- Avis réels (repris tels quels du site) -----------------------------
R = {
 'marie':  dict(q="Un travail remarquable sur notre toiture. Le démoussage a redonné vie à notre toit, résultat impeccable !", n="Marie L.", v="Anglet", i="ML"),
 'pierre': dict(q="Intervention rapide pour une fuite sur le toit. Problème réglé en une journée, prix très correct.", n="Pierre K.", v="Hendaye", i="PK"),
 'fatima': dict(q="Le traitement hydrofuge a transformé notre toiture. Après 2 ans, elle est toujours comme neuve.", n="Fatima B.", v="Saint-Jean-de-Luz", i="FB"),
 'amadou': dict(q="Très satisfait du ravalement de façade. L'équipe est ponctuelle, propre et le rendu est superbe.", n="Amadou D.", v="Bayonne", i="AD"),
 'sofia':  dict(q="Peinture intérieure parfaite, les finitions sont soignées. Je recommande sans hésiter !", n="Sofia M.", v="Biarritz", i="SM"),
}

OPT_TOIT = [("Tuiles", "Tuiles", "layers"), ("Ardoise", "Ardoise", "layers"), ("Zinc / bac acier", "Zinc / bac acier", "layers"), ("Je ne sais pas", "Je ne sais pas", "help")]
OPT_SURF = [("Moins de 80 m²", "Moins de 80 m²", "home"), ("80 à 150 m²", "80 à 150 m²", "home"), ("Plus de 150 m²", "Plus de 150 m²", "home"), ("Je ne sais pas", "Je ne sais pas", "help")]
FAQ_ZONE = ("Quelles villes couvrez-vous ?", "Boucau, Bayonne, Anglet, Biarritz, Bidart, Guéthary, Saint-Jean-de-Luz, Hendaye et les communes du Sud-Landes jusqu'à Capbreton.")
FAQ_GARANTIE = ("Quelles garanties proposez-vous ?", "Tous nos chantiers sont couverts par notre garantie décennale et notre assurance RC Pro. Nous sommes artisan certifié RGE.")
STEPS_TOIT = lambda s2, s3: [("Vous nous appelez", "Décrivez l'état de votre toiture, on cale une visite gratuite rapidement."), ("Diagnostic & devis", s2), ("Intervention", s3), ("Contrôle final", "Vérification tuile par tuile et nettoyage du chantier avant de repartir.")]

PAGES = [
 dict(
  out='index.html', path='/',
  title="Nettoyage & démoussage de toiture — Bayonne · Tonio Rénov'",
  desc="Démoussage et nettoyage de toiture à Bayonne, Côte Basque et Sud-Landes. Traitement hydrofuge, devis gratuit sous 24h, garantie décennale.",
  img='/roof.jpg', pos='60% 38%', crop='28% 74%', alt="Toiture en tuiles canal et gouttière, entretenue par Tonio Rénov'",
  h1="Votre toiture se couvre de mousse ?<br><mark>Tonio Rénov' la nettoie et la protège.</mark>",
  sub="<strong>Nettoyage et démoussage de toiture</strong>, traitement hydrofuge. Artisan couvreur sur la <strong>Côte Basque et les Sud-Landes</strong> — on traite avant que l'eau s'infiltre. Garantie décennale.",
  ghost="Décrire ma toiture", last_trust=("clock", "Réponse sous 24h", "on vous rappelle"),
  signs=dict(t="Votre toiture vous envoie déjà des signaux",
    p="La mousse retient l'humidité contre les tuiles. Non traitée, elle finit par soulever les tuiles et infiltrer la charpente — un <strong>entretien à temps</strong> évite une réfection complète.",
    items=[("sprout", "Mousse verte visible", "Des plaques de mousse ou de lichen apparaissent sur les tuiles, surtout côté nord ou sous les arbres."),
           ("layers", "Tuiles qui se déplacent", "La mousse soulève les tuiles en séchant puis en s'humidifiant : elles finissent par bouger ou casser."),
           ("drop", "Taches d'humidité au plafond", "Une auréole à l'intérieur signale souvent une infiltration déjà en cours sous la couverture."),
           ("waves", "Gouttières qui débordent", "Débris et mousse accumulés bouchent l'évacuation et font stagner l'eau sur la toiture.")]),
  method_steps=STEPS_TOIT("On évalue l'ampleur de la mousse et l'état des tuiles, devis détaillé sous 24h.", "Nettoyage basse pression, traitement hydrofuge sans chlore, produits DALEP 2100."),
  real=dict(t="Démoussage complet avec traitement hydrofuge", items=["Démoussage basse pression, sans abîmer les tuiles", "Traitement hydrofuge biocide sans chlore", "Tenue dans le temps : toiture toujours nette après 2 ans", "Chantier couvert par la garantie décennale"]),
  reviews=['marie', 'pierre', 'fatima'],
  form=dict(t="Votre devis en 4 questions", sub="<strong>30 secondes</strong>, sans engagement — on vous rappelle <strong>sous 24h</strong>",
    t2="Recevez votre devis démoussage", q1="Qu'observez-vous sur votre toiture ?",
    o1=[("Mousse / lichen visible", "Mousse / lichen visible", "sprout"), ("Tuiles cassées ou déplacées", "Tuiles cassées / déplacées", "layers"), ("Fuite ou infiltration", "Fuite / infiltration", "drop"), ("Entretien préventif", "Entretien préventif", "clock")],
    q2="Quel type de toiture avez-vous ?", o2=OPT_TOIT, q3="Surface approximative de la toiture ?", o3=OPT_SURF),
  faq=[("J'ai de la mousse sur mon toit, c'est urgent ?", "Tant qu'elle est en surface, un démoussage suffit. Dès qu'elle soulève les tuiles ou que des taches apparaissent au plafond, l'eau passe déjà — et là, chaque mois compte."),
       ("Intervenez-vous en urgence pour une fuite ?", "Oui, on priorise les urgences (fuite, infiltration) et on peut souvent intervenir sous 48h sur le secteur Bayonne / Côte Basque."),
       FAQ_GARANTIE,
       ("Le démoussage abîme-t-il les tuiles ?", "Non — on travaille en basse pression avec des produits biocides sans chlore, spécifiquement pour préserver l'étanchéité et la couleur des tuiles."),
       FAQ_ZONE],
  cta=dict(t="Une toiture entretenue, c'est une toiture qui dure", p="<strong>Devis gratuit sous 24h</strong>, aucun engagement."),
 ),
 dict(
  out='entretien/index.html', path='/entretien/',
  title="Entretien & traitement hydrofuge de toiture — Bayonne · Tonio Rénov'",
  desc="Entretien préventif et traitement hydrofuge de toiture à Bayonne, Côte Basque et Sud-Landes. Devis gratuit sous 24h, garantie décennale.",
  img='/roof.jpg', pos='55% 40%', crop='72% 62%', alt="Toiture en tuiles canal avec gouttière zinc, entretien par Tonio Rénov'",
  h1="Votre toit s'abîme ?<br><mark>Tonio Rénov' et ses équipes l'entretiennent.</mark>",
  sub="<strong>Entretien de toiture</strong>, contrôle des tuiles et traitement hydrofuge. Artisan couvreur sur la <strong>Côte Basque et les Sud-Landes</strong> — on garde votre toit étanche. Garantie décennale.",
  ghost="Décrire ma toiture", last_trust=("clock", "Réponse sous 24h", "on vous rappelle"),
  signs=dict(t="Ce qui abîme une toiture, c'est le temps qu'on laisse passer",
    p="L'humidité s'installe sans bruit dans la couverture, puis dans la charpente. Le <strong>traitement hydrofuge</strong> et le contrôle régulier arrêtent le processus avant les dégâts.",
    items=[("drop", "Traitement hydrofuge préventif", "Un traitement biocide sans chlore qui empêche la mousse et le lichen de s'installer durablement."),
           ("search", "Contrôle des tuiles", "On vérifie tuile par tuile qu'aucune n'a bougé ou ne s'est fissurée avec le temps et les intempéries."),
           ("waves", "Nettoyage des gouttières", "Débris et feuilles sont évacués pour que l'eau s'écoule normalement, sans stagner sur la toiture."),
           ("clock", "Tenue dans la durée", "Nos traitements DALEP 2100 tiennent plusieurs années — bien moins de passages qu'un entretien classique.")]),
  method_steps=STEPS_TOIT("On évalue l'état des tuiles, des gouttières et des zones à protéger, devis détaillé sous 24h.", "Contrôle complet, nettoyage basse pression, traitement hydrofuge sans chlore, produits DALEP 2100."),
  real=dict(t="Entretien annuel avec traitement hydrofuge DALEP 2100", items=["Contrôle complet de la couverture, tuile par tuile", "Traitement hydrofuge biocide sans chlore, produit pro", "Tenue dans le temps : toiture toujours nette après 2 ans", "Chantier couvert par la garantie décennale"]),
  reviews=['fatima', 'marie', 'pierre'],
  form=dict(t="Votre devis en 4 questions", sub="<strong>30 secondes</strong>, sans engagement — on vous rappelle <strong>sous 24h</strong>",
    t2="Recevez votre devis d'entretien", q1="Quel entretien recherchez-vous ?",
    o1=[("Traitement hydrofuge", "Traitement hydrofuge", "drop"), ("Contrôle général de toiture", "Contrôle général", "search"), ("Nettoyage de gouttières", "Nettoyage gouttières", "waves"), ("Je ne sais pas, à évaluer", "À évaluer sur place", "help")],
    q2="Quel type de toiture avez-vous ?", o2=OPT_TOIT, q3="Surface approximative de la toiture ?", o3=OPT_SURF),
  faq=[("Tous les combien de temps faut-il entretenir sa toiture ?", "En moyenne tous les 2 à 3 ans sur la Côte Basque, selon l'exposition (vent, embruns, arbres à proximité). Nos traitements DALEP 2100 tiennent dans la durée, ce qui espace les passages."),
       ("Comment savoir si ma toiture a besoin d'un passage ?", "Mousse visible, tuiles décalées, gouttière qui déborde, traces sombres au plafond : ces quatre signes suffisent. On vient regarder gratuitement et on vous dit franchement si ça peut attendre."),
       ("Le traitement hydrofuge abîme-t-il les tuiles ?", "Non — on utilise des produits biocides sans chlore, spécifiquement pour préserver l'étanchéité et la couleur des tuiles."),
       FAQ_GARANTIE, FAQ_ZONE],
  cta=dict(t="Une toiture entretenue, c'est une toiture qui dure", p="<strong>Devis gratuit sous 24h</strong>, aucun engagement."),
 ),
 dict(
  out='urgence/index.html', path='/urgence/',
  title="Fuite de toiture & urgence — Bayonne · Tonio Rénov'",
  desc="Fuite ou infiltration sur votre toiture ? Intervention rapide à Bayonne, Côte Basque et Sud-Landes. Artisan local, garantie décennale.",
  img='/roof.jpg', pos='64% 42%', crop='60% 78%', alt="Toiture en tuiles et gouttière, diagnostic et réparation par Tonio Rénov'",
  h1="Une fuite sur votre toiture ?<br><mark>On la répare avant qu'il ne soit trop tard.</mark>",
  sub="<strong>Réparation de fuite</strong>, tuile cassée, infiltration. Artisan couvreur sur la <strong>Côte Basque et les Sud-Landes</strong>, déplacement <strong>en priorité</strong> — une infiltration abîme la charpente en quelques jours.",
  ghost="Décrire mon urgence", last_trust=("clock", "Intervention sous 48h", "priorité aux urgences"),
  signs=dict(t="Une fuite ne s'aggrave pas si vous agissez vite",
    p="<strong>Chaque heure compte</strong> : plus l'eau s'infiltre longtemps, plus les dégâts sur la charpente et l'isolation grandissent. Voici les réflexes à avoir en attendant l'intervention.",
    items=[("drop", "Protégez l'intérieur", "Placez un seau ou une bâche sous la fuite pour limiter les dégâts au plafond et au sol en attendant."),
           ("pin", "Repérez la zone", "Notez l'emplacement précis de l'infiltration : ça nous fait gagner un temps précieux à l'arrivée."),
           ("zap", "Coupez l'électricité si besoin", "Si l'eau approche d'une installation électrique, coupez le disjoncteur de la zone concernée par sécurité."),
           ("phone", "Appelez-nous", "On évalue la situation par téléphone et on priorise les interventions urgentes sur le secteur.")]),
  method_steps=STEPS_TOIT("On localise l'origine de la fuite et l'état de la couverture, prix annoncé avant les travaux.", "Réparation le jour même quand c'est possible : tuiles remplacées, étanchéité reprise."),
  real=dict(t="Fuite réparée en une journée", items=["Diagnostic sur place pour localiser précisément l'infiltration", "Réparation le jour même quand c'est possible", "Prix annoncé avant intervention, pas de surprise", "Réparation couverte par la garantie décennale"]),
  reviews=['pierre', 'marie', 'fatima'],
  form=dict(t="Décrivez votre urgence en 4 questions", sub="<strong>30 secondes</strong> — on vous rappelle <strong>en priorité</strong>",
    t2="Décrivez votre urgence, on vous rappelle", q1="Quelle est votre urgence ?",
    o1=[("Fuite active", "Fuite active", "drop"), ("Infiltration / tache d'humidité", "Infiltration / tache", "waves"), ("Tuiles endommagées", "Tuiles endommagées", "layers"), ("Autre urgence toiture", "Autre urgence", "alert")],
    q2="Quel type de toiture avez-vous ?", o2=OPT_TOIT, q3="Surface approximative de la toiture ?", o3=OPT_SURF),
  faq=[("En combien de temps intervenez-vous en cas de fuite ?", "On priorise systématiquement les urgences (fuite, infiltration) et on peut souvent intervenir sous 48h sur le secteur Bayonne / Côte Basque."),
       ("Et si la fuite abîme déjà la charpente ?", "C'est justement ce qu'on va regarder en premier. Plus l'eau stagne, plus le bois et l'isolation souffrent — on localise l'origine et on arrête l'infiltration avant de reprendre le reste."),
       ("Que faire en attendant votre arrivée ?", "Protégez l'intérieur avec un seau ou une bâche sous la fuite, et coupez l'électricité de la zone si l'eau s'en approche. On vous guide par téléphone si besoin."),
       ("Quelles garanties proposez-vous ?", "Toutes nos réparations sont couvertes par notre garantie décennale et notre assurance RC Pro. Nous sommes artisan certifié RGE."),
       FAQ_ZONE],
  cta=dict(t="Chaque minute compte face à une fuite", p="Appelez-nous, on évalue la situation <strong>tout de suite</strong>."),
 ),
 dict(
  out='ravalement/index.html', path='/ravalement/',
  title="Ravalement & peinture de façade — Bayonne · Tonio Rénov'",
  desc="Ravalement, nettoyage et peinture de façade à Bayonne, Côte Basque et Sud-Landes. Devis gratuit sous 24h, garantie décennale.",
  img='/facade.jpg', pos='50% 42%', crop='30% 58%', alt="Façade blanche à volets rouges ravalée par Tonio Rénov'",
  h1="Votre façade se dégrade ?<br><mark>Tonio Rénov' la ravale et la repeint.</mark>",
  sub="<strong>Ravalement et peinture de façade</strong>, décrassage et reprise des fissures. Artisan façadier sur la <strong>Côte Basque et les Sud-Landes</strong> — on protège le mur, pas seulement la couleur.",
  ghost="Décrire ma façade", last_trust=("clock", "Réponse sous 24h", "on vous rappelle"),
  signs=dict(t="Votre façade vous envoie déjà des signaux",
    p="L'humidité et la pollution s'installent progressivement dans l'enduit. Non traitées, les <strong>fissures s'aggravent</strong> et l'eau finit par s'infiltrer dans les murs.",
    items=[("sprout", "Mousse ou noirceur visible", "Traces vertes ou noires sur l'enduit, souvent côté nord ou dans les zones peu exposées au soleil."),
           ("crack", "Fissures dans l'enduit", "De fines craquelures apparaissent avec le temps et les mouvements du bâti — elles laissent l'eau s'infiltrer."),
           ("roller", "Peinture qui s'écaille", "Le revêtement se décolle ou change de teinte : la protection de la façade s'affaiblit."),
           ("drop", "Taches d'humidité", "Des auréoles sombres apparaissent en bas des murs ou autour des fenêtres, souvent liées à un défaut d'étanchéité.")]),
  method_steps=[("Vous nous appelez", "Décrivez l'état de votre façade, on cale une visite gratuite rapidement."), ("Diagnostic & devis", "On évalue l'état de l'enduit et du revêtement, devis détaillé sous 24h."), ("Décrassage & ravalement", "Nettoyage complet, réparation des fissures, peinture Tollens sur demande."), ("Contrôle final", "Vérification de la finition et nettoyage du chantier avant de repartir.")],
  real=dict(t="Ravalement complet avec peinture Tollens", items=["Décrassage complet de la façade, sans abîmer l'enduit", "Réparation des fissures avant remise en peinture", "Peintures professionnelles Tollens, finitions soignées", "Chantier couvert par la garantie décennale"]),
  reviews=['amadou', 'sofia', 'marie'],
  form=dict(t="Votre devis en 4 questions", sub="<strong>30 secondes</strong>, sans engagement — on vous rappelle <strong>sous 24h</strong>",
    t2="Recevez votre devis ravalement", q1="Qu'observez-vous sur votre façade ?",
    o1=[("Façade encrassée / noircie", "Façade encrassée", "sprout"), ("Fissures apparentes", "Fissures apparentes", "crack"), ("Peinture à refaire", "Peinture à refaire", "roller"), ("Entretien préventif", "Entretien préventif", "clock")],
    q2="Quel type de revêtement avez-vous ?", o2=[("Enduit", "Enduit", "home"), ("Pierre apparente", "Pierre apparente", "home"), ("Crépi", "Crépi", "home"), ("Je ne sais pas", "Je ne sais pas", "help")],
    q3="Surface approximative de la façade ?", o3=OPT_SURF),
  faq=[("Mes fissures sont-elles graves ?", "Une microfissure se traite facilement ; une fissure qui traverse l'enduit laisse l'eau entrer dans le mur et fait remonter l'humidité à l'intérieur. On vient voir sur place et on vous le dit clairement."),
       ("Combien de temps dure un chantier de façade ?", "Ça dépend de la surface et de l'ampleur des réparations, mais on planifie toujours le chantier à l'avance et on respecte les délais annoncés."),
       FAQ_GARANTIE,
       ("Quelles peintures utilisez-vous ?", "Des peintures professionnelles Tollens, adaptées au climat de la Côte Basque (humidité, embruns) pour une tenue durable."),
       FAQ_ZONE],
  cta=dict(t="Une façade entretenue, c'est une maison qui dure", p="<strong>Devis gratuit sous 24h</strong>, aucun engagement."),
 ),
]

# ----------------------------- Médias : photos d'illustration libres de droits (Unsplash) -----------------------------
MEDIA = {
 'index.html': dict(mode='slider', b='demoussage-avant', a='demoussage-apres', tb='Avant', ta='Après',
                    ab="Tuiles couvertes de mousse et de lichen (photo d'illustration)", aa="Tuiles propres après un démoussage (photo d'illustration)",
                    bgm='demoussage-bg-methode', bgc='demoussage-bg-cta'),
 'entretien/index.html': dict(mode='slider', b='entretien-avant', a='entretien-apres', tb='Avant', ta='Après',
                    ab="Gouttière encrassée et bord de toit sale (photo d'illustration)", aa="Gouttière propre et bien entretenue (photo d'illustration)",
                    bgm='entretien-bg-methode', bgc='entretien-bg-cta'),
 'urgence/index.html': dict(mode='split', b='urgence-avant', a='urgence-apres', tb='Le problème', ta="L'intervention",
                    ab="Plafond abîmé par une infiltration d'eau (photo d'illustration)", aa="Couvreur au travail sur une toiture en tuiles (photo d'illustration)",
                    bgm='urgence-bg-methode', bgc='urgence-bg-cta'),
 'ravalement/index.html': dict(mode='slider', b='ravalement-avant', a='ravalement-apres', tb='Avant', ta='Après',
                    ab="Mur dont la peinture s'écaille (photo d'illustration)", aa="Mur blanc fraîchement repeint (photo d'illustration)",
                    bgm='ravalement-bg-methode', bgc='ravalement-bg-cta'),
}

def dims(name):
    try:
        from PIL import Image
        with Image.open(os.path.join(ROOT, 'img', name + '.jpg')) as im:
            return f'width="{im.width}" height="{im.height}"'
    except Exception:
        return ''

def compare(m):
    note = f'<p class="ba-note">{ic("image")}Photos d\'illustration · Unsplash</p>'
    if m['mode'] == 'split':
        return (f'<div class="ba-split reveal"><figure><img src="/img/{m["b"]}.jpg" alt="{m["ab"]}" loading="lazy" decoding="async" {dims(m["b"])}><figcaption class="ba-tag ba-tag-b">{m["tb"]}</figcaption></figure>'
                f'<figure><img src="/img/{m["a"]}.jpg" alt="{m["aa"]}" loading="lazy" decoding="async" {dims(m["a"])}><figcaption class="ba-tag ba-tag-a">{m["ta"]}</figcaption></figure></div>{note}')
    return (f'<figure class="ba reveal" data-mode="slider" style="--pos:50%"><div class="ba-stage">'
            f'<img class="ba-img ba-after" src="/img/{m["a"]}.jpg" alt="{m["aa"]}" loading="lazy" decoding="async" {dims(m["a"])}>'
            f'<img class="ba-img ba-before" src="/img/{m["b"]}.jpg" alt="{m["ab"]}" loading="lazy" decoding="async" {dims(m["b"])}>'
            f'<span class="ba-tag ba-tag-b">{m["tb"]}</span><span class="ba-tag ba-tag-a">{m["ta"]}</span>'
            f'<input class="ba-range" type="range" min="0" max="100" step="0.1" value="50" aria-label="Faire glisser pour comparer avant et après">'
            f'<span class="ba-line" aria-hidden="true"><span class="ba-knob">{ic("lr")}</span></span></div>{note}</figure>')

def bgimg(name):
    return f'<img class="sec-bg" src="/img/{name}.jpg" alt="" aria-hidden="true" loading="lazy" decoding="async" {dims(name)}>'

def opts(name, options, first_focus=False):
    out = []
    for value, label, icon in options:
        out.append(f'<button type="button" class="opt" data-value="{value}" aria-pressed="false">{ic(icon)}<span>{label}</span><span class="tick">{ic("check")}</span></button>')
    return f'<div class="opts" data-field="{name}" role="group">' + ''.join(out) + '</div>'

def render(p):
    s = SITE
    M = MEDIA[p['out']]
    h1_inner, _ = split_words(p['h1'])
    h1 = f'<h1 aria-label="{plain(p["h1"])}">{h1_inner}</h1>'
    trust = [("award", "Plus de 500 chantiers", "sur la Côte Basque"), ("shield-check", "Garantie décennale", "sur tous nos travaux"),
             ("shield", "Assurance RC Pro", "artisan assuré"), ("award", "Certifié RGE", "qualification reconnue"), p['last_trust']]
    trust[0] = ("home", trust[0][1], trust[0][2])
    band = ''.join(f'<li>{ic(i)}<div><b>{a}</b><small>{b}</small></div></li>' for i, a, b in trust)
    signs = ''.join(f'<li class="sign reveal" style="--d:{k}"><span class="sign-ic">{ic(i)}</span><div><h3>{t}</h3><p>{d}</p></div></li>' for k, (i, t, d) in enumerate(p['signs']['items']))
    steps = ''.join(f'<li class="step reveal" style="--d:{k}"><span class="step-n">{k+1}</span><h3>{t}</h3><p>{d}</p></li>' for k, (t, d) in enumerate(p['method_steps']))
    real = ''.join(f'<li>{ic("check")}<span>{t}</span></li>' for t in p['real']['items'])
    revs = []
    for k, key in enumerate(p['reviews']):
        r = R[key]; big = ' big' if k == 0 else ''
        revs.append(f'<figure class="rev{big} reveal" style="--d:{k}">{stars()}<blockquote>« {r["q"]} »</blockquote><figcaption class="rev-who"><span class="rev-av">{r["i"]}</span><span><b>{r["n"]}</b><small>{r["v"]}</small></span></figcaption></figure>')
    f = p['form']
    prog = '<i></i>' * 4
    faq = ''.join(f'<details><summary>{q}{ic("plus")}</summary><p>{a}</p></details>' for q, a in p['faq'])
    zones = ''.join(f'<li class="{"base" if z=="Boucau" else ""}">{ic("pin")}{z}</li>' for z in ZONES)
    tel = f'tel:{s["tel"]}'
    sig_h2 = h2(p['signs']['t'])
    method_h2 = h2("De l'appel au chantier, sans mauvaise surprise", 'on-dark')
    real_h2 = h2(p['real']['t'])
    rev_h2 = h2("Ce que disent nos clients sur la Côte Basque")
    zone_h2 = h2("Basés à Boucau, on se déplace sur toute la Côte Basque")
    faq_h2 = h2("Vos questions avant de nous appeler")
    cta_h2 = h2(p['cta']['t'])
    call_btn = lambda label, extra='': f'''<a class="btn btn-call {extra}" href="{tel}"><span class="sh-spark" aria-hidden="true"><span class="sh-slide"><span class="sh-spin"></span></span></span><span class="sh-back" aria-hidden="true"></span><svg class="ic ring" viewBox="0 0 24 24" aria-hidden="true">{ICONS["phone"]}</svg><span>{label}</span></a>'''
    next_btn = f'''<button type="button" class="btn btn-next" disabled><span class="sh-spark" aria-hidden="true"><span class="sh-slide"><span class="sh-spin"></span></span></span><span class="sh-back" aria-hidden="true"></span><span class="lbl">Continuer</span>{ic("arrow","arr")}</button>'''

    def devis_bloc(pos, titre, ident, hero=False):
        """Un formulaire complet. `pos` rend les identifiants uniques : il y en a deux par page.
        `hero=True` renvoie la carte seule, à poser dans la colonne droite du hero."""
        champs = (
            f'<div class="field"><label for="f-nom-{pos}">Nom</label>'
            f'<input id="f-nom-{pos}" data-champ="nom" type="text" placeholder="Votre nom" autocomplete="name"></div>'
            f'<div class="field"><label for="f-tel-{pos}">Téléphone</label>'
            f'<input id="f-tel-{pos}" data-champ="tel" type="tel" inputmode="tel" placeholder="06 12 34 56 78" autocomplete="tel"></div>'
            f'<div class="field"><label for="f-ville-{pos}">Ville</label>'
            f'<input id="f-ville-{pos}" data-champ="ville" type="text" placeholder="Bayonne, Anglet, Biarritz…" autocomplete="address-level2"></div>'
        )
        corps = f'''<div class="devis-shell">
      <div class="progress" aria-hidden="true">{prog}</div>
      <form class="devis-form" data-pos="{pos}" novalidate>
        <div class="fstep active" data-step="1"><span class="fcount">Étape 1 sur 4</span><p class="fq" tabindex="-1" data-focus>{f['q1']}</p>{opts('probleme', f['o1'])}</div>
        <div class="fstep" data-step="2"><span class="fcount">Étape 2 sur 4</span><p class="fq" tabindex="-1" data-focus>{f['q2']}</p>{opts('toiture', f['o2'])}</div>
        <div class="fstep" data-step="3"><span class="fcount">Étape 3 sur 4</span><p class="fq" tabindex="-1" data-focus>{f['q3']}</p>{opts('surface', f['o3'])}</div>
        <div class="fstep" data-step="4"><span class="fcount">Étape 4 sur 4</span><p class="fq" tabindex="-1" data-focus>Vos coordonnées pour le rappel</p>{champs}</div>
        <div class="fstep" data-step="5" aria-live="polite"><div class="done"><div class="done-ic">{ic("check")}</div><h3 tabindex="-1" data-focus>Demande envoyée</h3><p>Merci ! Un artisan {s['name']} vous rappelle sous 24h pour affiner le devis.</p><a class="btn btn-call" href="{tel}"><span class="sh-spark" aria-hidden="true"><span class="sh-slide"><span class="sh-spin"></span></span></span><span class="sh-back" aria-hidden="true"></span>{ic("phone")}<span>Ou appelez le {s['phone']}</span></a></div></div>
        <div class="factions"><button type="button" class="fback" disabled>{ic("back")}Précédent</button>{next_btn}</div>
      </form>
    </div>'''
        if hero:
            return f'''<div class="hero-form" id="{ident}">
      <div class="hf-head"><h2 class="hf-t">{titre}</h2><p class="hf-sub">{f['sub']}</p></div>
      {corps}
    </div>'''
        return f'''<section class="sec sec-light devis" id="{ident}">
  <div class="wrap">
    <div class="sec-head center">{titre}<p class="lead">{f['sub']}</p></div>
    {corps}
    <p class="alt-call">Vous préférez en parler ? Appelez-nous au <a href="{tel}">{s['phone']}</a></p>
  </div>
</section>'''

    # Le formulaire du haut est dans le hero : texte et boutons à gauche, formulaire à droite
    # sur ordinateur ; en dessous du titre et des boutons d'appel sur mobile.
    devis_haut = devis_bloc('haut', f['t'], 'devis', hero=True)
    devis_bas = devis_bloc('bas', h2(f['t2']), 'devis-bas')

    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<script>document.documentElement.classList.add('js')</script>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{s["gtm"]}');</script>
<!-- End Google Tag Manager -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{p['title']}</title>
<meta name="description" content="{p['desc']}">
<meta name="theme-color" content="#0b1827">
<meta property="og:type" content="website">
<meta property="og:title" content="{p['title']}">
<meta property="og:description" content="{p['desc']}">
<meta property="og:image" content="{s['base']}{p['img']}">
<link rel="canonical" href="{s['base']}{p['path']}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preload" as="image" href="{p['img']}" fetchpriority="high">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet">
<style>
{CSS}
</style>
</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={s['gtm']}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
<a class="skip" href="#devis">Aller au formulaire de devis</a>

<header class="bar">
  <div class="bar-in">
    <a class="brand" href="#top" aria-label="{s['name']} — haut de page">{mark()}<span><b>{s['name']}</b><small>Toiture &amp; façade · Boucau</small></span></a>
    <div class="bar-actions">
      <a class="bar-tel" href="{tel}">{s['phone']}</a>
      <a class="btn btn-call btn-sm" href="{tel}"><span class="sh-spark" aria-hidden="true"><span class="sh-slide"><span class="sh-spin"></span></span></span><span class="sh-back" aria-hidden="true"></span>{ic("phone")}<span>Appeler</span></a>
      <a class="btn btn-ghost btn-sm" href="#devis"><span class="lbl-long">Devis gratuit</span><span class="lbl-short">Devis</span></a>
    </div>
  </div>
</header>

<main id="top">
<section class="hero">
  <div class="hero-bg"><img src="{p['img']}" alt="{p['alt']}" width="1024" height="1024" fetchpriority="high" decoding="async" style="--pos:{p['pos']}"></div>
  <div class="hero-in">
    <div class="hero-copy">
      {h1}
      <p class="hero-sub fade" style="--d:0">{p['sub']}</p>
      <div class="hero-cta fade" style="--d:1">
        {call_btn("Appeler maintenant")}
        <a class="btn btn-ghost" href="#devis"><span>{p['ghost']}</span>{ic("arrow","arr")}</a>
      </div>
      <p class="hero-proof fade" style="--d:2"><span>{stars()}<b>5/5</b> avis vérifiés</span><span>{ic("pin")}Côte Basque &amp; Sud-Landes</span></p>
    </div>
    {devis_haut}
  </div>
</section>

<section class="band" aria-label="Nos garanties"><div class="wrap"><ul>{band}</ul></div></section>

<section class="sec sec-light">
  <div class="wrap signs-grid">
    <div class="signs-head">{sig_h2}<p class="lead reveal" style="--d:1">{p['signs']['p']}</p></div>
    <ul class="signs-list">{signs}</ul>
  </div>
</section>

<section class="sec sec-dark has-bg">
  {bgimg(M["bgm"])}
  <div class="wrap">
    <div class="sec-head center">{method_h2}<p class="lead reveal on-dark" style="--d:1">Un diagnostic sur place, un <strong>devis détaillé</strong>, une intervention propre et planifiée.</p></div>
    <ol class="steps">{steps}</ol>
  </div>
</section>

<section class="sec sec-light">
  <div class="wrap real-grid">
    <div class="real-head">{real_h2}</div>
    <div class="ba-col">{compare(M)}</div>
    <ul class="real-list reveal" style="--d:1">{real}</ul>
  </div>
</section>

<section class="sec sec-light" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head">{rev_h2}<p class="rev-sum reveal">{stars()}<span><b>5/5</b> · avis vérifiés de clients de la Côte Basque et des Landes</span></p></div>
    <div class="rev-grid">{''.join(revs)}</div>
  </div>
</section>

<section class="sec sec-light" style="padding-top:0">
  <div class="wrap zone-grid">
    <div>{zone_h2}<p class="lead reveal" style="--d:1"><strong>Artisan local</strong> — pas d'intermédiaire, pas de sous-traitance. On connaît les toitures et les façades du secteur, exposées au vent et aux embruns.</p></div>
    <ul class="chips reveal" style="--d:2">{zones}</ul>
  </div>
</section>

<section class="sec sec-light" style="padding-top:0">
  <div class="wrap faq-grid">
    <div class="faq-head">{faq_h2}<p class="lead reveal" style="--d:1">Une autre question ? Appelez-nous au <a href="{tel}"><strong>{s['phone']}</strong></a>.</p></div>
    <div class="faq-list reveal" style="--d:1">{faq}</div>
  </div>
</section>

<section class="sec cta has-bg">
  {bgimg(M["bgc"])}
  <div class="wrap">
    {cta_h2}
    <p class="reveal" style="--d:1">{p['cta']['p']}</p>
    <div class="btns reveal" style="--d:2">
      <a class="btn btn-light" href="{tel}">{ic("phone")}<span>{s['phone']}</span></a>
      <a class="btn btn-outline-light" href="#devis-bas"><span>Demander un devis</span>{ic("arrow","arr")}</a>
    </div>
  </div>
</section>
{devis_bas}
</main>

<footer>
  <div class="wrap foot">
    <div><a class="brand" href="#top">{mark()}<span><b>{s['name']}</b><small>Toiture &amp; façade · Boucau</small></span></a><p>Artisan basé à Boucau, spécialisé en entretien de toiture et en peinture, intervenant sur Bayonne, la Côte Basque et les Sud-Landes. Intervention rapide, devis gratuit, garantie décennale.</p></div>
    <div><h4>Contact</h4><ul><li><a class="tel-foot" href="{tel}">+33 6 34 12 23 31</a></li><li><a href="mailto:{s['email']}">{s['email']}</a></li><li>Boucau (64), Pays basque</li></ul></div>
    <div><h4>Prestations</h4><ul><li>Démoussage de toiture</li><li>Traitement hydrofuge</li><li>Entretien de toiture</li><li>Ravalement &amp; peinture de façade</li></ul></div>
  </div>
  <div class="wrap foot-bottom"><span>© 2026 {s['name']} — Tous droits réservés</span><a href="https://toniorenov.fr">toniorenov.fr</a></div>
</footer>

<a class="fab" href="{tel}" aria-label="Appeler {s['name']} au {s['phone']}"><span class="fab-pulse" aria-hidden="true"></span><svg class="ic ring" viewBox="0 0 24 24" aria-hidden="true">{ICONS["phone"]}</svg><span>Appeler</span></a>

<script>
{JS}
</script>
</body>
</html>
'''

if __name__ == '__main__':
    for p in PAGES:
        target = os.path.join(ROOT, p['out'])
        os.makedirs(os.path.dirname(target), exist_ok=True)
        open(target, 'w', encoding='utf-8').write(render(p))
        print('écrit', p['out'], f'{os.path.getsize(target)//1024} Ko')
    fav = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#fff"/>'
           '<g transform="translate(4 15) scale(.0968)"><g transform="translate(-395 -438)">'
           '<polygon fill="#152c48" points="704,442 1008,695 934,695 704,505 476,695 400,695 505,607 505,514 562,514 562,558"/>'
           '<polygon fill="#8c1c2c" points="704,532 901,695 869,695 704,562 539,695 507,695"/></g></g></svg>')
    open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8').write(fav)
