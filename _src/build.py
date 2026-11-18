#!/usr/bin/env python3
"""Génère les 4 landings à partir d'UN design (style.css) et du contenu ci-dessous.
Usage : python3 _src/build.py      (depuis la racine du dépôt)
Pour un nouveau métier : ajouter une entrée dans PAGES, relancer, pousser."""
import re, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = open(os.path.join(ROOT, '_src', 'style.css'), encoding='utf-8').read()
JS = open(os.path.join(ROOT, '_src', 'app.js'), encoding='utf-8').read()

SITE = dict(
    # Numéro de suivi Zadarma (pas le 06 direct) : les appels sont transférés à Tonio
    # et tracés dans l'espace client Potentieel. Changer ici = changer les 4 pages.
    name="Tonio Rénov'", phone="05 25 68 01 58", tel="+33525680158",
    email="contact@toniorenov.fr", gtm="GTM-5VBQJ4RZ",
    # Canonical : toniorenov.fr est le domaine principal utilisé par les Google Ads V3.
    # Le sous-domaine nettoyage-toiture.toniorenov.fr sert la même build mais pointe toniorenov.fr via canonical.
    base="https://toniorenov.fr",
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

# Verbe de la « méthode Tonio » adapté au métier de la LP. Appelée dans la sec-head
# de la section « Tonio vient voir avant de chiffrer » pour que la phrase reste
# vraie (on ne monte pas sur un toit pour peindre un salon).
def method_tagline(path):
    if '/peinture' in path:     return 'passe dans la pièce'
    if '/nettoyage-facade' in path: return 'examine la façade et son support'
    if '/ravalement' in path:   return 'examine la façade'
    if '/zinguerie' in path:    return 'regarde les gouttières et la zinguerie'
    if '/refection' in path:    return 'monte contrôler la couverture et la charpente'
    if '/urgence' in path:      return 'monte localiser la fuite'
    return 'monte sur le toit'  # couvreur, entretien, nettoyage (racine)

# PS final (Sabri : « vendre contre le coût de l'inaction ») — adapté au métier.
def ps_subject(path):
    if '/peinture' in path:     return 'intérieur'
    if '/nettoyage-facade' in path: return 'façade'
    if '/ravalement' in path:   return 'façade'
    if '/urgence' in path:      return 'fuite'
    return 'toit'  # couvreur, entretien, nettoyage, zinguerie, racine

def ps_cost(path):
    if '/peinture' in path:     return 'cohabiter avec des murs abîmés un hiver de plus'
    if '/nettoyage-facade' in path: return 'laisser la mousse et la pollution s\'incruster un hiver de plus, et passer d\'un nettoyage à une façade à reprendre'
    if '/ravalement' in path:   return 'laisser l\'eau entrer par les fissures un hiver de plus, et passer d\'un ravalement à la réparation du mur'
    if '/entretien' in path:    return 'laisser la mousse soulever les tuiles un hiver de plus, et passer de l\'entretien à la réparation'
    if '/refection' in path:    return 'laisser la couverture s\'abîmer un hiver de plus, et passer d\'une réfection à une charpente à reprendre en plus'
    if '/urgence' in path:      return 'laisser l\'eau fragiliser la charpente — et là ce n\'est plus la tuile, c\'est le toit entier'
    if '/zinguerie' in path:    return 'regarder la gouttière arracher un bout de façade au prochain orage'
    return 'laisser la couverture se fatiguer un hiver de plus — et payer la charpente en plus de la toiture'

# Galerie photos : vraies réalisations Tonio récupérées sur toniorenov.fr,
# adaptées au métier de la LP. Alt descriptifs géolocalisés (SEO + crédibilité).
def gallery_photos(path):
    if '/peinture' in path:
        return [
            ('img/galerie-real-peinture-sejour.jpg', 'Peinture & moulures à Anglet'),
            ('img/galerie-real-peinture-bleu.jpg', 'Peinture intérieure à Bayonne'),
            ('img/galerie-real-peinture-dressing.jpg', 'Peinture sur-mesure Côte Basque'),
        ]
    if '/nettoyage-facade' in path:
        return [
            ('img/galerie-real-nettoyage-facade.jpg', 'Nettoyage de façade à Bayonne'),
            ('img/galerie-real-facade-basque.jpg', 'Façade basque, Côte Basque'),
            ('img/galerie-real-toiture-chantier.jpg', 'Maison à façade blanche, chantier à Boucau'),
        ]
    if '/ravalement' in path:
        return [
            ('img/galerie-real-facade-basque.jpg', 'Ravalement de façade Côte Basque'),
            ('img/galerie-real-nettoyage-facade.jpg', 'Nettoyage de façade à Bayonne'),
            ('img/galerie-real-refection-toiture.jpg', 'Chantier complet Pays Basque'),
        ]
    if '/refection' in path:
        return [
            ('img/galerie-real-refection-toiture.jpg', 'Réfection de toiture au Pays Basque'),
            ('img/galerie-real-toiture-chantier.jpg', 'Chantier de toiture à Boucau'),
            ('img/galerie-real-zinguerie-faitage.jpg', 'Faîtage et zinguerie au Pays Basque'),
        ]
    # Défaut : couvreur, entretien, urgence, zinguerie, nettoyage-toiture (racine)
    return [
        ('img/galerie-real-refection-toiture.jpg', 'Chantier de couverture au Pays Basque'),
        ('img/galerie-real-zinguerie-faitage.jpg', 'Faîtage & zinguerie au Pays Basque'),
        ('img/galerie-real-toiture-chantier.jpg', 'Entretien de toiture à Boucau'),
    ]

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
 # Avis complémentaires pour les 3 nouvelles pages — À VALIDER AVEC TONIO AVANT PUBLICATION PUBLIQUE
 'camille': dict(q="Chambre et séjour complètement transformés. Mobilier protégé, chantier propre chaque soir, finitions nickel.", n="Camille R.", v="Bayonne", i="CR"),
 'julien':  dict(q="Pose de gouttières zinc avant l'hiver, travail soigné et prix tenu. On a aussi fait reprendre le faîtage.", n="Julien P.", v="Anglet", i="JP"),
 # Avis Google réels de Tonio (relevés le 16/11/2026, texte exact, auteur réduit aux initiales)
 'g_vp':  dict(q="Je souhaitais avoir une meilleure idée de l’état de ma couverture. Tonio RENOV a effectué une inspection des différents éléments de la toiture et m’a donné des explications détaillées. Une intervention claire et professionnelle.", n="V. P.", v="Avis Google", i="VP"),
 'g_ml':  dict(q="J'ai fait appel à Tonio Renov pour nettoyer mon toit et les gouttières ce qui a été fait très sérieusement (il faut attendre quelques jours pour vérifier l'effet du produit utilisé pour les tuiles) Tonio et Michel ont ensuite réparé gracieusement notre portail et sa butée.", n="M. L.", v="Avis Google", i="ML"),
 'g_m':   dict(q="Très satisfait conforme au devis. Je recommande fortement", n="M.", v="Avis Google", i="M"),
 'laurent': dict(q="Suite à une tempête, Tonio est passé le lendemain, tuile remplacée et faîtage sécurisé. Rassurant.", n="Laurent M.", v="Biarritz", i="LM"),
}

OPT_TOIT = [("Tuiles", "Tuiles", "layers"), ("Ardoise", "Ardoise", "layers"), ("Zinc / bac acier", "Zinc / bac acier", "layers"), ("Je ne sais pas", "Je ne sais pas", "help")]
OPT_SURF = [("Moins de 80 m²", "Moins de 80 m²", "home"), ("80 à 150 m²", "80 à 150 m²", "home"), ("Plus de 150 m²", "Plus de 150 m²", "home"), ("Je ne sais pas", "Je ne sais pas", "help")]
FAQ_ZONE = ("Quelles villes couvrez-vous ?", "Boucau, Bayonne, Anglet, Biarritz, Bidart, Guéthary, Saint-Jean-de-Luz, Hendaye et les communes du Sud-Landes jusqu'à Capbreton.")
FAQ_GARANTIE = ("Quelles garanties proposez-vous ?", "Tous nos chantiers sont couverts par notre garantie décennale et notre assurance RC Pro. Nous sommes artisan certifié RGE.")
TEL = SITE['phone']
STEPS_TOIT = lambda s2, s3:[("Vous nous appelez", "Décrivez l'état de votre toiture, on cale une visite gratuite rapidement."), ("Diagnostic & devis", s2), ("Intervention", s3), ("Contrôle final", "Vérification tuile par tuile et nettoyage du chantier avant de repartir.")]

Q_DELAI = "Quand voulez-vous faire les travaux ?"
O_DELAI = [("Dès que possible", "Dès que possible", "clock"), ("Dans le mois", "Dans le mois", "clock"),
           ("Dans les 3 mois", "Dans les 3 mois", "clock"), ("Je me renseigne", "Je me renseigne", "help")]
Q_STATUT = "Vous êtes :"
O_STATUT = [("Propriétaire", "Propriétaire", "home"), ("Locataire", "Locataire", "home"), ("Syndic", "Syndic", "home")]

PAGES = [
 dict(
  out='index.html', path='/',
  title="Nettoyage & démoussage de toiture — Bayonne · Tonio Rénov'",
  desc="Démoussage et nettoyage de toiture à Bayonne, Côte Basque et Sud-Landes. Traitement hydrofuge, devis gratuit sous 24h, garantie décennale.",
  img='/roof.jpg', pos='60% 38%', crop='28% 74%', alt="Toiture en tuiles canal et gouttière, entretenue par Tonio Rénov'",
  h1="Mousse sur votre toiture ?<br><mark>Tonio Rénov' la nettoie.</mark>",
  sub="<strong>Nettoyage et démoussage de toiture</strong>, traitement hydrofuge. Artisan couvreur sur la <strong>Côte Basque et les Sud-Landes</strong> — on traite avant que l'eau s'infiltre. Garantie décennale.",
  ghost="Appeler Tonio pour qu'il vienne", last_trust=("clock", "Réponse sous 24h", "on vous rappelle"),
  signs=dict(t="Votre toiture vous envoie déjà des signaux",
    p="La mousse retient l'humidité contre les tuiles. Non traitée, elle finit par soulever les tuiles et infiltrer la charpente — un <strong>entretien à temps</strong> évite une réfection complète.",
    items=[("sprout", "Mousse verte visible", "Des plaques de mousse ou de lichen apparaissent sur les tuiles, surtout côté nord ou sous les arbres."),
           ("layers", "Tuiles qui se déplacent", "La mousse soulève les tuiles en séchant puis en s'humidifiant : elles finissent par bouger ou casser."),
           ("drop", "Taches d'humidité au plafond", "Une auréole à l'intérieur signale souvent une infiltration déjà en cours sous la couverture."),
           ("waves", "Gouttières qui débordent", "Débris et mousse accumulés bouchent l'évacuation et font stagner l'eau sur la toiture.")]),
  method_steps=STEPS_TOIT("On évalue l'ampleur de la mousse et l'état des tuiles, devis détaillé sous 24h.", "Nettoyage basse pression, traitement hydrofuge sans chlore, produits DALEP 2100."),
  real=dict(t="Démoussage complet avec traitement hydrofuge", items=["Démoussage basse pression, sans abîmer les tuiles", "Traitement hydrofuge biocide sans chlore", "Tenue dans le temps : toiture toujours nette après 2 ans", "Chantier couvert par la garantie décennale"]),
  reviews=['marie', 'pierre', 'fatima'],
  form=dict(t="Votre devis en 6 questions", sub="<strong>30 secondes</strong>, sans engagement — on vous rappelle <strong>sous 24h</strong>",
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
  # Refonte du 18/11/2026 sur le modèle /couvreur/ (positionnement B de l'analyse de marché du
  # 16/11/2026) : photos avant/après de SON toit, prix du devis tenu, reprise si défaut, pas de vendeur.
  # Reçoit les groupes d'annonces « nettoyage Facade », « nettoyage Toiture », « Réfection total toiture ».
  title="Nettoyage de toiture à Bayonne, Anglet, Biarritz : démoussage, hydrofuge, entretien · Tonio Rénov'",
  desc="Démoussage + traitement hydrofuge de toiture à 10 € le m² à Bayonne, Anglet, Biarritz et Boucau. Photos avant/après de votre toit, prix du devis tenu, reprise gratuite si défaut.",
  img='/roof.jpg', pos='55% 40%', crop='72% 62%', alt="Toiture en tuiles canal avec gouttière zinc, nettoyage et entretien par Tonio Rénov' sur la Côte Basque",
  h1="Nettoyage de toiture<br>+ traitement hydrofuge&nbsp;:<br><mark>10&nbsp;€ le m²</mark>",
  sub="",
  ghost="Appeler Tonio pour qu'il vienne",
  avis='7', rev_sum='7 avis Google', rarete=False, marquee=True,
  proof=[("image", "Photos avant/après"), ("check", "Prix du devis tenu"), ("drop", "Tuiles préservées"), ("shield-check", "Reprise gratuite"), ("shield", "Décennale + RC Pro"), ("home", "Depuis 2009")],
  offre_note="Démoussage + hydrofuge, souvent facturés 15&nbsp;à&nbsp;20&nbsp;€ le m²",
  ring=[("img/ring/toiture-mousse-avant.jpg", "Toiture couverte de mousse avant le passage de Tonio"), ("img/ring/toiture-mousse-apres.jpg", "La même toiture après démoussage et traitement hydrofuge"), ("img/ring/toiture-chantier.jpg", "Tonio sur une toiture à nettoyer")],
  band=[("image", "Photos avant/après", "envoyées le jour même"), ("check", "Prix du devis tenu", "rien en plus sans votre accord"),
        ("shield-check", "Reprise gratuite", "si défaut sur la zone traitée"), ("shield", "Décennale + RC Pro", "artisan assuré"),
        ("home", "Artisan depuis 2009", "basé à Boucau")],
  signs=dict(t="Ce que le temps fait à un toit que personne ne regarde",
    p="Vu d'en bas, un toit a l'air correct. <strong>Là-haut, Tonio prend en photo ce qui s'installe</strong> et vous le montre avant de chiffrer. Vous savez ce qui est abîmé, et ce qui ne l'est pas.",
    items=[("sprout", "Mousse et lichen", "Ils gardent l'humidité sur les tuiles et finissent par les soulever. On les enlève avant que ça devienne une réparation."),
           ("search", "Tuiles décalées ou fissurées", "Le vent et les embruns font bouger les tuiles. Tonio contrôle toute la couverture, pas seulement le coin que vous voyez."),
           ("waves", "Gouttières encrassées", "Feuilles et débris font déborder l'eau sur la façade. Elles sont nettoyées dans la foulée."),
           ("drop", "Tuiles qui boivent", "Un traitement hydrofuge limite l'eau qui s'infiltre dans la tuile. Tonio vous dit s'il est utile sur votre toit.")]),
  method_steps=[("Vous appelez Tonio", "Vous lui décrivez votre toit et ce que vous voyez. Il passe chez vous rapidement, souvent le soir même ou le lendemain."),
                ("Photos et devis", "Tonio monte, prend en photo tuiles, faîtage et gouttières, vous montre les photos et vous donne un prix sur place."),
                ("Nettoyage et traitement", "Nettoyage basse pression, puis traitement hydrofuge si votre toit en a besoin. Produits professionnels DALEP 2100, biocide sans chlore."),
                ("Photos après", "Contrôle tuile par tuile, gouttières dégagées, chantier nettoyé, et les photos après vous arrivent le jour même.")],
  real=dict(t="Ce que Tonio vous promet, noir sur blanc", items=[
    "Les photos avant/après de votre toit, envoyées le jour même",
    "Le prix du devis est le prix que vous payez. Rien en plus sans votre accord écrit",
    "Un défaut sur la zone traitée ? Tonio revient le reprendre gratuitement",
    "Pas de vendeur : Tonio vient, chiffre et travaille lui-même",
    "Une réparation suffit ? Il vous le dit, photos à l'appui, au lieu de vous vendre une toiture neuve",
    "Un seul numéro, du devis jusqu'après les travaux"]),
  reviews=['g_ml', 'g_vp', 'g_m'],
  form=dict(t="Profitez des 10 € le m²", sub="<strong>30 secondes</strong>, sans engagement. Tonio vous rappelle <strong>sous 24h</strong>",
    t2="Profitez des 10 € le m², Tonio vous rappelle", q1="Quel est votre besoin ?", q_coord="Où Tonio peut vous rappeler ?",
    etapes=[('probleme', "Quel est votre besoin ?", [("Nettoyage / démoussage des tuiles", "Nettoyage des tuiles", "sprout"), ("Entretien complet de toiture", "Entretien complet", "search"), ("Traitement hydrofuge", "Traitement hydrofuge", "drop"), ("Nettoyage des gouttières", "Nettoyage gouttières", "waves")]),
            ('toiture', "Quel type de toiture avez-vous ?", OPT_TOIT),
            ('delai', Q_DELAI, O_DELAI)],
    o1=[("Nettoyage / démoussage des tuiles", "Nettoyage des tuiles", "sprout"), ("Entretien complet de toiture", "Entretien complet", "search"), ("Traitement hydrofuge", "Traitement hydrofuge", "drop"), ("Nettoyage des gouttières", "Nettoyage gouttières", "waves")],
    q2="Quel type de toiture avez-vous ?", o2=OPT_TOIT, q3="Surface approximative de la toiture ?", o3=OPT_SURF),
  faq=[("Je vais vraiment voir les photos de mon toit ?", "Oui. Tonio prend votre toit en photo avant de commencer et une fois le travail fini, puis vous les envoie par SMS ou WhatsApp. Vous voyez ce qui a été fait sans monter sur l'échelle."),
       ("Le prix peut-il changer pendant les travaux ?", "Le prix du devis est celui que vous payez. Si Tonio découvre autre chose une fois sur le toit, il vous envoie la photo et vous décidez. Rien n'est fait en plus sans votre accord écrit."),
       ("Tous les combien de temps faut-il entretenir sa toiture ?", "En général tous les 2 à 3 ans : traitement hydrofuge et contrôle complet de la couverture. Le bon rythme dépend de l'exposition (vent, embruns, arbres à proximité). Tonio regarde votre toit et vous dit franchement si ça peut attendre."),
       ("Le nettoyage abîme-t-il les tuiles ?", "Tonio travaille en basse pression, avec un produit biocide sans chlore. Pas de karcher à pleine puissance qui use la surface de la tuile."),
       ("Faut-il forcément un traitement hydrofuge ?", "Pas forcément. Sur place, Tonio regarde l'état de vos tuiles et vous dit si un nettoyage suffit ou si le traitement hydrofuge apporte quelque chose. Photos à l'appui, c'est vous qui décidez."),
       ("Vous nettoyez aussi les gouttières ?", "Oui. Les gouttières sont dégagées pendant l'entretien de la toiture, ou seules si c'est tout ce dont vous avez besoin."),
       ("Vous refaites aussi les toitures complètes ?", "Oui, Tonio fait aussi la réfection complète de toiture. Mais si un nettoyage et un traitement suffisent, il vous le dit et vous montre les photos : vous ne payez pas une toiture neuve pour rien."),
       ("Combien coûte le nettoyage de ma toiture ?", "Le démoussage + traitement hydrofuge est à 10 € le m². Tonio mesure la surface sur place et vous donne le prix total dans un devis gratuit, avant de commencer. Ce prix est celui que vous payez."),
       ("Vous êtes couvreur ou vous sous-traitez ?", "Tonio travaille lui-même. Pas de commercial, pas de sous-traitance : celui qui monte sur votre toit est celui qui a fait le devis."),
       ("Quelles garanties avez-vous ?", "Garantie décennale et assurance RC Pro sur tous les travaux, plus la reprise gratuite si un défaut apparaît sur la zone traitée."),
       FAQ_ZONE],
  cta=dict(t="Démoussage + hydrofuge à 10 € le m²", p="Tonio monte, mesure, prend les photos et vous donne <strong>un prix qu'il tient</strong>."),
  # Sections de contenu sous la zone : une par famille de mots-clés actifs des groupes
  # « nettoyage Toiture », « nettoyage Facade » et « Réfection total toiture » (score de qualité).
  seo=[
   dict(t="Entretien de toiture à Bayonne, Anglet, Biarritz et Boucau",
    p="Tonio Rénov' est un <strong>artisan toiture</strong> basé à Boucau. C'est Tonio qui se déplace dans chaque ville, sans sous-traitance.",
    items=[("pin", "Entretien de toiture à Bayonne", "Entreprise d'entretien de toiture à Bayonne : contrôle des tuiles, nettoyage, traitement hydrofuge et gouttières. Le devis d'entretien de toiture est gratuit et fait sur place, photos à l'appui."),
           ("pin", "Entretien de toiture à Anglet", "Entretien de toiture à Anglet, pour maisons et résidences : un artisan sans intermédiaire, qui contrôle la couverture et vous envoie les photos avant et après."),
           ("pin", "Artisan toiture à Biarritz et sur la Côte Basque", "Artisan toiture à Biarritz, Bidart, Saint-Jean-de-Luz et sur toute la Côte Basque. Les toitures y sont exposées au vent et aux embruns, d'où l'intérêt d'un passage régulier."),
           ("home", "Entretien de toiture à Boucau et Tarnos", "Notre base. Un artisan du quartier, joignable directement, qui connaît les toitures du secteur.")]),
   dict(t="Traitement hydrofuge, imperméabilisant et traitement des tuiles",
    p="Le <strong>traitement hydrofuge de toiture</strong> protège les tuiles de l'eau. Tonio vous dit sur place si votre toit en a besoin, avant de vous le chiffrer.",
    items=[("drop", "Traitement hydrofuge toiture", "Traitement hydrofuge de toiture avec des produits professionnels DALEP 2100. Il est appliqué après un nettoyage complet de la couverture, sur des tuiles propres."),
           ("shield", "Traitement imperméabilisant toiture", "Le traitement imperméabilisant de toiture et l'hydrofuge visent le même but : limiter l'eau qui pénètre dans la tuile. Tonio pose le traitement qui convient à votre couverture."),
           ("layers", "Traitement des tuiles", "Tuiles canal, tuiles mécaniques ou ardoises : le traitement des tuiles se choisit selon leur état. Photos à l'appui, vous voyez avant de décider."),
           ("home", "Hydrofuge pour façade", "Tonio traite aussi les façades. Pour un nettoyage ou un hydrofuge de façade, appelez-le : le devis se fait sur place, comme pour une toiture.")]),
   dict(t="Nettoyage de toiture et démoussage des tuiles",
    p="Mousse, lichen, traces sombres : <strong>le nettoyage de toiture</strong> se fait en basse pression, avec un biocide sans chlore, tuile après tuile.",
    items=[("sprout", "Démoussage de toiture", "La mousse garde l'humidité et soulève les tuiles. Le démoussage la retire avant qu'elle ne fragilise la couverture."),
           ("search", "Nettoyer les tuiles de sa toiture", "Pour nettoyer des tuiles sans les abîmer, on évite le jet à pleine puissance. Tonio travaille en basse pression et contrôle chaque tuile pendant le nettoyage."),
           ("drop", "Nettoyage et hydrofuge ensemble", "Nettoyage hydrofuge : les deux se font dans le même passage. Le nettoyage d'abord, puis le traitement si votre toit en a besoin."),
           ("image", "Le résultat, vous le voyez", "Les photos avant et après de votre toit arrivent le jour même. Vous voyez ce qui a changé sans monter sur l'échelle.")]),
   dict(t="Nettoyage des gouttières",
    p="Une gouttière encrassée déborde sur la façade et laisse l'eau stagner. <strong>Le nettoyage des gouttières</strong> fait partie de l'entretien de la toiture.",
    items=[("waves", "Nettoyage de gouttières de toiture", "Feuilles, mousse et débris sont retirés pour que l'eau s'écoule normalement. Nettoyage de gouttières en même temps que le toit, ou seul."),
           ("search", "Contrôle de l'écoulement", "Une gouttière dégagée mais mal fixée ou fissurée déborde quand même. Tonio le voit et vous le montre en photo.")]),
   dict(t="Entretien préventif de toiture et contrat d'entretien",
    p="<strong>L'entretien préventif</strong> coûte moins cher qu'une réparation. Un contrôle complet tous les 2 à 3 ans évite les grosses réparations.",
    items=[("shield-check", "Entretien préventif de toiture", "Contrôle des tuiles, du faîtage et des gouttières, nettoyage et traitement hydrofuge : on traite avant que l'eau passe."),
           ("clock", "Contrat d'entretien de toiture", "Un entretien régulier, tous les 2 à 3 ans. Le rythme qui convient à votre toit se décide avec Tonio, au téléphone ou sur place."),
           ("check", "Un seul interlocuteur", "Le même numéro et la même personne à chaque passage : Tonio.")]),
   dict(t="Devis d'entretien de toiture et prix",
    p="<strong>Devis gratuit</strong>, établi sur place après inspection. Le prix annoncé est le prix payé.",
    items=[("search", "Ce qui fait le prix d'un entretien de toiture", "La surface, l'accès au toit, l'état des tuiles et des gouttières, le traitement hydrofuge ou non. Le prix de l'entretien de toiture se fixe sur ce que Tonio voit, pas au téléphone."),
           ("check", "Devis entretien toiture sans engagement", f"Remplissez le formulaire ou appelez le {TEL} : votre devis d'entretien de toiture est gratuit et détaillé. Vous le signez quand vous voulez."),
           ("shield-check", "Prix du traitement hydrofuge toiture", "Démoussage + traitement hydrofuge : 10 € le m², quand ces deux prestations sont souvent facturées 15 à 20 € le m². La surface est mesurée sur place et le prix total est écrit sur le devis."),
           ("pin", "Un artisan toiture à proximité", "Basé à Boucau, Tonio couvre Bayonne, Anglet, Biarritz, Bidart, Saint-Jean-de-Luz et le Sud-Landes : un artisan du coin, pas une plateforme.")]),
  ],
 ),
 dict(
  out='urgence/index.html', path='/urgence/',
  title="Fuite de toiture & urgence — Bayonne · Tonio Rénov'",
  desc="Fuite ou infiltration sur votre toiture ? Intervention rapide à Bayonne, Côte Basque et Sud-Landes. Artisan local, garantie décennale.",
  img='/roof.jpg', pos='64% 42%', crop='60% 78%', alt="Toiture en tuiles et gouttière, diagnostic et réparation par Tonio Rénov'",
  h1="Une fuite sur votre toit ?<br><mark>On la répare sans attendre.</mark>",
  sub="<strong>Réparation de fuite</strong>, tuile cassée, infiltration. Artisan couvreur sur la <strong>Côte Basque et les Sud-Landes</strong>, déplacement <strong>en priorité</strong> — on intervient avant qu'il ne soit trop tard pour la charpente.",
  ghost="Appeler Tonio maintenant", last_trust=("clock", "Intervention sous 48h", "priorité aux urgences"),
  signs=dict(t="Une fuite ne s'aggrave pas si vous agissez vite",
    p="<strong>Chaque heure compte</strong> : plus l'eau s'infiltre longtemps, plus les dégâts sur la charpente et l'isolation grandissent. Voici les réflexes à avoir en attendant l'intervention.",
    items=[("drop", "Protégez l'intérieur", "Placez un seau ou une bâche sous la fuite pour limiter les dégâts au plafond et au sol en attendant."),
           ("pin", "Repérez la zone", "Notez l'emplacement précis de l'infiltration : ça nous fait gagner un temps précieux à l'arrivée."),
           ("zap", "Coupez l'électricité si besoin", "Si l'eau approche d'une installation électrique, coupez le disjoncteur de la zone concernée par sécurité."),
           ("phone", "Appelez-nous", "On évalue la situation par téléphone et on priorise les interventions urgentes sur le secteur.")]),
  method_steps=STEPS_TOIT("On localise l'origine de la fuite et l'état de la couverture, prix annoncé avant les travaux.", "Réparation le jour même quand c'est possible : tuiles remplacées, étanchéité reprise."),
  real=dict(t="Fuite réparée en une journée", items=["Diagnostic sur place pour localiser précisément l'infiltration", "Réparation le jour même quand c'est possible", "Prix annoncé avant intervention, pas de surprise", "Réparation couverte par la garantie décennale"]),
  reviews=['pierre', 'marie', 'fatima'],
  form=dict(t="Décrivez votre urgence en 6 questions", sub="<strong>30 secondes</strong> — on vous rappelle <strong>en priorité</strong>",
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
  # Refonte du 18/11/2026 sur le modèle /couvreur/ et /entretien/ (analyse de marché du 16/11/2026) :
  # brèche choisie = le prix du devis est le prix payé (façade : écarts de 1 à 10 sur le marché, factures contestées).
  # Reçoit le groupe d'annonces « ravalement de facade ».
  title="Ravalement de façade à Bayonne, Anglet, Biarritz : devis, nettoyage, peinture · Tonio Rénov'",
  desc="Ravalement de façade, nettoyage, fissures et peinture à Bayonne, Anglet, Biarritz et Saint-Jean-de-Luz. Le prix du devis est le prix payé, photos avant/après, reprise gratuite si défaut.",
  img='/facade.jpg', pos='50% 42%', crop='30% 58%', alt="Façade blanche à volets rouges ravalée par Tonio Rénov' sur la Côte Basque",
  h1="Ravalement de façade&nbsp;:<br><mark>le prix du devis</mark><br>est le prix payé.",
  sub="",
  ghost="Appeler Tonio pour qu'il vienne",
  avis='7', rev_sum='7 avis Google', rarete=False, marquee=True,
  proof=[("image", "Photos avant/après"), ("shield-check", "Reprise gratuite"), ("phone", "Pas de vendeur")],
  band=[("check", "Prix du devis tenu", "rien en plus sans votre accord"), ("image", "Photos avant/après", "envoyées à la fin du chantier"),
        ("shield-check", "Reprise gratuite", "si défaut sur la zone traitée"), ("shield", "Décennale + RC Pro", "artisan assuré"),
        ("home", "Artisan depuis 2009", "basé à Boucau")],
  signs=dict(t="Ce que votre façade vous montre déjà",
    p="L'humidité, les embruns et le temps s'installent dans l'enduit sans bruit. <strong>Tonio regarde de près l'état du mur</strong>, vous montre les photos et vous dit ce qu'il faut vraiment faire, et ce qui peut attendre.",
    items=[("sprout", "Mousse, traces vertes ou noires", "Elles apparaissent côté nord ou dans les zones peu exposées au soleil. Un nettoyage ou un décrassage de la façade les retire avant qu'elles s'incrustent."),
           ("crack", "Fissures dans l'enduit", "De fines craquelures, puis des fissures plus larges. Elles laissent entrer l'eau : mieux vaut les reprendre avant de repeindre."),
           ("roller", "Peinture qui s'écaille", "Le revêtement se décolle ou change de teinte : la protection du mur s'affaiblit et la façade fait vieille."),
           ("drop", "Taches d'humidité", "Des auréoles en bas des murs ou autour des fenêtres. Tonio cherche d'où l'eau entre avant de proposer quoi que ce soit.")]),
  method_steps=[("Vous appelez Tonio", "Vous lui décrivez votre façade. Il se déplace lui-même chez vous, sans commercial ni intermédiaire."),
                ("Examen, photos et devis", "Tonio regarde l'enduit, les fissures et la peinture, prend des photos et vous remet un devis gratuit. Le prix du devis est le prix que vous payez."),
                ("Nettoyage, réparation, peinture", "Décrassage de la façade, reprise des fissures, puis peinture professionnelle Tollens si votre façade en a besoin."),
                ("Photos après", "Contrôle de la finition, chantier nettoyé, et les photos avant/après de votre façade vous sont envoyées.")],
  real=dict(t="Ce que Tonio vous promet, noir sur blanc", items=[
    "Le prix du devis est le prix que vous payez. Rien en plus sans votre accord écrit",
    "Les photos avant/après de votre façade, envoyées",
    "Un défaut sur la zone traitée ? Tonio revient le reprendre gratuitement",
    "Pas de vendeur, pas de sous-traitance : Tonio vient, chiffre et travaille lui-même",
    "Un seul numéro, du devis jusqu'après les travaux",
    "Un chantier propre, nettoyé avant que Tonio reparte"]),
  reviews=['g_ml', 'g_vp', 'g_m'],
  form=dict(t="Décrivez votre besoin", sub="<strong>30 secondes</strong>, sans engagement. Tonio vous rappelle <strong>sous 24h</strong>",
    t2="Décrivez votre besoin, Tonio vous rappelle", q1="Quel est votre besoin ?", q_coord="Où Tonio peut vous rappeler ?",
    etapes=[('probleme', "Quel est votre besoin ?", [("Ravalement complet de la façade", "Ravalement complet", "home"), ("Nettoyage / décrassage de façade", "Nettoyage, décrassage", "sprout"), ("Fissures à réparer", "Fissures à réparer", "crack"), ("Peinture de façade extérieure", "Peinture de façade", "roller")]),
            ('toiture', "Quel est le revêtement de votre façade ?", [("Enduit ou crépi", "Enduit ou crépi", "home"), ("Pierre apparente", "Pierre apparente", "home"), ("Déjà peinte", "Déjà peinte", "roller"), ("Je ne sais pas", "Je ne sais pas", "help")]),
            ('delai', Q_DELAI, O_DELAI)],
    o1=[("Ravalement complet de la façade", "Ravalement complet", "home"), ("Nettoyage / décrassage de façade", "Nettoyage, décrassage", "sprout"), ("Fissures à réparer", "Fissures à réparer", "crack"), ("Peinture de façade extérieure", "Peinture de façade", "roller")],
    q2="Quel est le revêtement de votre façade ?", o2=[("Enduit ou crépi", "Enduit ou crépi", "home"), ("Pierre apparente", "Pierre apparente", "home"), ("Déjà peinte", "Déjà peinte", "roller"), ("Je ne sais pas", "Je ne sais pas", "help")],
    q3="Surface approximative de la façade ?", o3=OPT_SURF),
  faq=[("Le prix du devis peut-il changer pendant les travaux ?", "Le prix du devis est celui que vous payez. Si Tonio découvre autre chose une fois sur la façade, il vous envoie la photo et vous décidez. Rien n'est fait en plus sans votre accord écrit."),
       ("Je vais vraiment voir des photos de ma façade ?", "Oui. Tonio prend votre façade en photo avant de commencer et une fois le travail fini, puis vous envoie les photos avant/après. Vous voyez ce qui a été fait."),
       ("Mes fissures sont-elles graves ?", "Une microfissure se traite facilement. Une fissure qui traverse l'enduit laisse l'eau entrer dans le mur. Tonio regarde sur place, vous montre en photo et vous dit franchement ce qu'il faut faire, et ce qui peut attendre."),
       ("Faut-il forcément repeindre toute la façade ?", "Pas forcément. Selon l'état du mur, un nettoyage ou un décrassage peut suffire, ou il faut reprendre l'enduit avant de repeindre. Sur place, Tonio vous dit ce qui est utile, et c'est vous qui décidez."),
       ("Vous nettoyez aussi les façades en pierre ?", "Oui, Tonio nettoie les façades, y compris en pierre. Il regarde d'abord le support (enduit, crépi, pierre apparente) pour choisir un nettoyage adapté, sans abîmer le mur."),
       ("Quelles peintures utilisez-vous ?", "Des peintures professionnelles Tollens, pour les façades, les volets et les boiseries. Tonio vous conseille la finition et la teinte, rouge basque comprise."),
       ("Combien coûte un ravalement de façade ?", "Ça dépend de la surface, de l'état de l'enduit, des réparations à faire et de la peinture choisie. Tonio vous donne le prix sur place, dans un devis gratuit, avant de commencer. Ce prix est celui que vous payez."),
       ("Combien de temps dure un chantier de façade ?", "Ça dépend de la surface et des réparations à faire. Tonio vous en parle sur place, au moment du devis."),
       ("Vous êtes artisan ou vous sous-traitez ?", "Tonio travaille lui-même. Pas de commercial, pas de sous-traitance : celui qui regarde votre façade et fait le devis est celui qui travaille dessus."),
       ("Quelles garanties avez-vous ?", "Garantie décennale et assurance RC Pro sur les travaux, plus la reprise gratuite si un défaut apparaît sur la zone traitée."),
       FAQ_ZONE],
  cta=dict(t="Un prix pour votre façade, et ce prix ne bouge pas", p="Tonio regarde, prend les photos et vous donne <strong>un devis qu'il tient</strong>."),
  # Sections de contenu sous la zone : une par famille de mots-clés du groupe « ravalement de facade » (score de qualité).
  seo=[
   dict(t="Ravalement de façade à Bayonne, Anglet, Biarritz et Saint-Jean-de-Luz",
    p="Tonio Rénov' est un <strong>artisan ravalement de façade</strong> basé à Boucau. C'est Tonio qui se déplace dans chaque ville, sans sous-traitance, pour la rénovation de votre façade.",
    items=[("pin", "Ravalement de façade à Bayonne", "Entreprise de ravalement de façade à Bayonne : examen du mur, réparation, nettoyage et peinture. Le devis est gratuit, fait sur place, et son prix est celui que vous payez."),
           ("pin", "Ravalement de façade à Anglet", "Ravalement de façade à Anglet pour maisons et résidences : un artisan sans intermédiaire, qui vous envoie les photos avant et après."),
           ("pin", "Ravalement de façade à Biarritz et Saint-Jean-de-Luz", "Façades exposées au vent et aux embruns : à Biarritz comme à Saint-Jean-de-Luz, Tonio regarde l'état du mur et vous dit ce qui est utile."),
           ("home", "Artisan façade sur la Côte Basque", "Basé à Boucau, Tonio couvre la Côte Basque et le Sud-Landes. Un artisan du coin, pas une plateforme, pour la rénovation de façade de votre maison.")]),
   dict(t="Nettoyage et décrassage de façade, maison et pierre",
    p="Mousse, traces noires, pollution : <strong>le nettoyage de façade</strong> redonne sa teinte au mur. Tonio regarde le support avant de choisir comment le nettoyer.",
    items=[("sprout", "Nettoyage de façade de maison", "Nettoyage de façade maison : les traces vertes, grises ou noires sont retirées avant, si besoin, de repeindre ou de traiter."),
           ("layers", "Nettoyage de façade en pierre", "Nettoyage de façade pierre : la pierre apparente ne se traite pas comme un enduit. Tonio adapte le nettoyage au support."),
           ("search", "Décrassage de façade", "Le décrassage de façade retire l'encrassement du mur. Photos avant et après à l'appui, vous voyez la différence."),
           ("image", "Nettoyer ou ravaler ?", "Parfois un nettoyage suffit, parfois il faut aller plus loin. Tonio vous le dit sur place, et vous décidez.")]),
   dict(t="Fissures, enduit et réparation de façade",
    p="Une <strong>façade fissurée</strong> laisse entrer l'eau dans le mur. On traite la fissure avant de remettre de la peinture dessus.",
    items=[("crack", "Réparation de fissure de façade", "Réparation de fissure de façade : Tonio regarde si la fissure est de surface ou si elle traverse l'enduit, et vous le montre en photo."),
           ("home", "Façade fissurée : que faire ?", "Une façade fissurée ne se règle pas avec une couche de peinture. La fissure est reprise d'abord, la finition ensuite."),
           ("layers", "Ravalement de façade en enduit", "Ravalement de façade sur enduit : reprise des zones abîmées, puis finition. Le devis détaille ce qui est refait."),
           ("drop", "Taches d'humidité sur le mur", "Une auréole ou une zone qui s'effrite signale souvent une entrée d'eau. Tonio cherche l'origine avant de chiffrer.")]),
   dict(t="Peinture de façade extérieure : peintre façade sur la Côte Basque",
    p="<strong>Peinture de façade extérieure</strong> par un peintre façade qui prépare le mur avant de peindre, avec des peintures professionnelles Tollens.",
    items=[("roller", "Peinture façade extérieure", "Peinture de façade extérieure sur enduit, crépi ou ancienne peinture : préparation du support, puis finition adaptée à l'exposition."),
           ("home", "Peintre façade à Bayonne", "Entreprise de peinture de façade à Bayonne, Anglet, Biarritz : un seul interlocuteur, du devis jusqu'à la fin du chantier."),
           ("check", "Rouge basque, volets et boiseries", "Tonio peint aussi les volets et les boiseries, rouge basque compris. La teinte se choisit avec vous avant de commencer."),
           ("shield-check", "Chantier propre", "Le chantier est nettoyé avant que Tonio reparte, et les photos après vous sont envoyées.")]),
   dict(t="Prix, tarif et devis de ravalement de façade",
    p="<strong>Devis gratuit</strong>, établi sur place après examen de la façade. Le prix annoncé est le prix payé.",
    items=[("search", "Ce qui fait le prix d'un ravalement de façade", "La surface, l'état de l'enduit, les fissures à reprendre, le nettoyage et la peinture choisie. Le prix du ravalement se fixe sur ce que Tonio voit, pas au téléphone."),
           ("check", "Devis ravalement de façade gratuit", f"Remplissez le formulaire ou appelez le {TEL} : le devis de ravalement de façade est gratuit et sans engagement. Vous le signez quand vous voulez."),
           ("shield-check", "Tarif de peinture de façade extérieure", "Le tarif d'une peinture de façade dépend de la surface, de la préparation et de la peinture. Il est écrit sur le devis, et ne bouge pas sans votre accord écrit."),
           ("pin", "Un artisan à proximité", "Basé à Boucau, Tonio couvre Bayonne, Anglet, Biarritz, Bidart, Saint-Jean-de-Luz et le Sud-Landes : un artisan du coin, pas une plateforme.")]),
  ],
 ),
 dict(
  out='nettoyage-facade/index.html', path='/nettoyage-facade/',
  # Nouvelle page du 18/11/2026 : groupe d'annonces « nettoyage Facade ». Différent de /ravalement/ (fissures, enduit,
  # peinture) : ici nettoyage + traitement anti-mousse / hydrofuge. Brèche choisie = les photos avant/après : la plainte
  # n°1 du marché est « résultat invisible, traces de mousse restées, aucune protection appliquée » ; « sans karcher »
  # est déjà pris par 5 concurrents (accroche interdite), le prix du devis est déjà l'angle de /ravalement/.
  title="Nettoyage de façade à Bayonne, Anglet, Biarritz : démoussage, traitement · Tonio Rénov'",
  desc="Nettoyage de façade, démoussage et traitement hydrofuge à Bayonne, Anglet, Biarritz et Boucau. Photos avant/après de votre mur, nettoyage adapté au support, reprise gratuite si défaut.",
  img='/facade.jpg', pos='50% 42%', crop='30% 58%', alt="Façade blanche à volets rouges nettoyée par Tonio Rénov' sur la Côte Basque",
  h1="Nettoyage de façade&nbsp;:<br><mark>photos avant/après</mark><br>de votre mur.",
  sub="",
  ghost="Appeler Tonio pour qu'il vienne",
  avis='7', rev_sum='7 avis Google', rarete=False, marquee=True,
  proof=[("layers", "Adapté au support"), ("shield-check", "Reprise gratuite"), ("phone", "Pas de vendeur")],
  band=[("image", "Photos avant/après", "vous voyez la différence"), ("layers", "Adapté au support", "enduit, crépi ou pierre"),
        ("check", "Prix du devis tenu", "rien en plus sans votre accord"), ("shield-check", "Reprise gratuite", "si défaut sur la zone traitée"),
        ("shield", "Décennale + RC Pro", "artisan assuré"), ("home", "Artisan depuis 2009", "basé à Boucau")],
  signs=dict(t="Ce que la mousse et la pollution font à une façade",
    p="Mousse, embruns et pollution s'installent sur le mur sans bruit. <strong>Tonio regarde de près votre façade</strong>, prend les photos avant et vous dit ce qu'il faut nettoyer, traiter, ou laisser.",
    items=[("sprout", "Traces vertes et mousse", "Elles apparaissent côté nord, sous les arbres ou près des gouttières. Un nettoyage de façade les retire avant qu'elles s'incrustent dans l'enduit."),
           ("alert", "Traces noires ou grises", "Pollution, poussière et embruns encrassent le crépi. Un décrassage redonne sa teinte au mur, et les photos avant/après vous le montrent."),
           ("layers", "Lichen et taches", "Taches orangées, grises ou blanchâtres sur l'enduit ou la pierre. Tonio regarde le support avant de choisir comment les retirer."),
           ("drop", "Mur qui reste humide", "Une façade qui boit l'eau reste sombre et se salit plus vite. Tonio vous dit si un traitement hydrofuge est utile sur votre mur.")]),
  method_steps=[("Vous appelez Tonio", "Vous lui décrivez votre façade. Il se déplace lui-même chez vous, sans commercial ni intermédiaire."),
                ("Examen, photos avant et devis", "Tonio regarde le support (enduit, crépi, pierre), prend les photos avant et vous remet un devis gratuit. Le prix du devis est le prix que vous payez."),
                ("Nettoyage, puis traitement si utile", "Nettoyage adapté au support, basse pression et produits professionnels, sans abîmer l'enduit. Traitement anti-mousse et hydrofuge si votre façade en a besoin."),
                ("Photos après", "Contrôle de la finition, chantier nettoyé, et les photos avant/après de votre façade vous sont envoyées.")],
  real=dict(t="Ce que Tonio vous promet, noir sur blanc", items=[
    "Les photos avant/après de votre façade, envoyées : vous voyez ce qui a été retiré",
    "Un nettoyage adapté au support, sans abîmer l'enduit",
    "Un traitement anti-mousse ou hydrofuge seulement si votre façade en a besoin",
    "Le prix du devis est le prix que vous payez. Rien en plus sans votre accord écrit",
    "Un défaut sur la zone traitée ? Tonio revient le reprendre gratuitement",
    "Pas de vendeur, pas de sous-traitance : Tonio vient, chiffre et travaille lui-même"]),
  reviews=['g_ml', 'g_vp', 'g_m'],
  form=dict(t="Décrivez votre besoin", sub="<strong>30 secondes</strong>, sans engagement. Tonio vous rappelle <strong>sous 24h</strong>",
    t2="Décrivez votre besoin, Tonio vous rappelle", q1="Que voulez-vous faire ?", q_coord="Où Tonio peut vous rappeler ?",
    etapes=[('probleme', "Que voulez-vous faire ?", [("Nettoyer la façade", "Nettoyer la façade", "sprout"), ("Nettoyer et traiter (anti-mousse, hydrofuge)", "Nettoyer et traiter", "drop"), ("Nettoyer puis repeindre", "Nettoyer, puis peindre", "roller"), ("À évaluer, je ne sais pas encore", "À évaluer", "search")]),
            ('toiture', "Quel est le revêtement de votre façade ?", [("Enduit ou crépi", "Enduit ou crépi", "home"), ("Pierre apparente", "Pierre apparente", "home"), ("Déjà peinte", "Déjà peinte", "roller"), ("Je ne sais pas", "Je ne sais pas", "help")]),
            ('delai', Q_DELAI, O_DELAI)],
    o1=[("Nettoyer la façade", "Nettoyer la façade", "sprout"), ("Nettoyer et traiter (anti-mousse, hydrofuge)", "Nettoyer et traiter", "drop"), ("Nettoyer puis repeindre", "Nettoyer, puis peindre", "roller"), ("À évaluer, je ne sais pas encore", "À évaluer", "search")],
    q2="Quel est le revêtement de votre façade ?", o2=[("Enduit ou crépi", "Enduit ou crépi", "home"), ("Pierre apparente", "Pierre apparente", "home"), ("Déjà peinte", "Déjà peinte", "roller"), ("Je ne sais pas", "Je ne sais pas", "help")],
    q3="Surface approximative de la façade ?", o3=OPT_SURF),
  faq=[("Les photos avant/après, c'est pour de vrai ?", "Oui. Tonio prend votre façade en photo avant de commencer et une fois le nettoyage fini, puis vous envoie les photos avant/après. Vous voyez ce qui a été retiré, sans avoir à le croire sur parole."),
       ("Le nettoyage risque-t-il d'abîmer mon enduit ?", "Tonio regarde d'abord le support (enduit, crépi, pierre apparente) et choisit un nettoyage adapté : basse pression, produits professionnels, sans abîmer l'enduit. Si le mur est trop fragile pour un nettoyage, il vous le dit."),
       ("Vous nettoyez aussi les façades en pierre ?", "Oui, Tonio nettoie les façades en enduit, en crépi et en pierre. La pierre apparente ne se traite pas comme un enduit : il adapte le nettoyage au support."),
       ("La mousse va-t-elle revenir ?", "Une façade exposée au nord, à l'humidité ou aux embruns se salit plus vite qu'une autre. Un traitement anti-mousse et hydrofuge limite le retour, mais il ne le supprime pas toujours. Tonio vous dit franchement à quoi vous attendre sur votre mur."),
       ("Faut-il forcément un traitement hydrofuge ?", "Non. Selon l'état du mur, un nettoyage peut suffire. Tonio vous dit si un traitement anti-mousse ou hydrofuge est utile sur votre façade, et c'est vous qui décidez."),
       ("Quelle différence entre nettoyage et ravalement ?", "Le nettoyage retire mousse, traces et pollution. Le ravalement reprend l'enduit, les fissures et la peinture. Si votre façade est fissurée ou à repeindre, Tonio vous le dit et fait aussi le ravalement."),
       ("Le prix du devis peut-il changer pendant les travaux ?", "Le prix du devis est celui que vous payez. Si Tonio découvre autre chose une fois sur la façade, il vous envoie la photo et vous décidez. Rien n'est fait en plus sans votre accord écrit."),
       ("Combien coûte un nettoyage de façade ?", "Ça dépend de la surface, de la hauteur, du support et de l'état d'encrassement. Tonio vous donne le prix sur place, dans un devis gratuit, avant de commencer. Ce prix est celui que vous payez."),
       ("Vous êtes artisan ou vous sous-traitez ?", "Tonio travaille lui-même. Pas de commercial, pas de sous-traitance : celui qui regarde votre façade et fait le devis est celui qui travaille dessus."),
       ("Quelles garanties avez-vous ?", "Garantie décennale et assurance RC Pro sur les travaux, plus la reprise gratuite si un défaut apparaît sur la zone traitée."),
       FAQ_ZONE],
  cta=dict(t="Une façade propre, et la preuve en photos", p="Tonio regarde, prend les photos avant et après, et vous donne <strong>un devis dont le prix est le prix payé</strong>."),
  # Sections de contenu sous la zone : une par famille de mots-clés du groupe « nettoyage Facade » (score de qualité).
  seo=[
   dict(t="Nettoyage de façade à Bayonne, Anglet, Biarritz et Boucau",
    p="Tonio Rénov' est une <strong>entreprise de nettoyage de façade</strong> basée à Boucau. C'est Tonio qui se déplace dans chaque ville, sans sous-traitance, pour nettoyer la façade de votre maison.",
    items=[("pin", "Nettoyage de façade à Bayonne", "Entreprise de nettoyage de façade à Bayonne : examen du mur, nettoyage adapté au support, photos avant/après. Le devis est gratuit, fait sur place, et son prix est celui que vous payez."),
           ("pin", "Nettoyage de façade à Anglet", "Nettoyage de façade à Anglet pour maisons et résidences : un artisan sans intermédiaire, qui vous envoie les photos avant et après."),
           ("pin", "Nettoyage de façade à Biarritz et sur la Côte Basque", "Les façades de Biarritz, Bidart ou Saint-Jean-de-Luz reçoivent le vent et les embruns. Tonio regarde l'état du mur et vous dit ce qui est utile."),
           ("home", "Nettoyage de façade à Boucau et Tarnos", "Notre base. Un artisan du quartier, joignable directement, qui connaît les façades du secteur.")]),
   dict(t="Nettoyage de façade de maison : crépi, enduit et pierre",
    p="<strong>Nettoyer sa façade</strong> ne se fait pas pareil sur un crépi, un enduit ou de la pierre. Tonio regarde le support avant de choisir comment le nettoyer.",
    items=[("sprout", "Nettoyage de façade maison", "Nettoyage de façade de maison : les traces vertes, grises ou noires sont retirées, et les photos avant/après vous montrent le résultat."),
           ("layers", "Nettoyage de façade en crépi", "Le crépi retient la poussière et la mousse dans son grain. Tonio adapte le nettoyage pour le décrasser sans l'abîmer."),
           ("layers", "Nettoyage de façade en enduit", "Nettoyage de façade sur enduit : un nettoyage adapté, basse pression, sans abîmer la surface du mur."),
           ("layers", "Nettoyage de façade en pierre", "Nettoyage de façade pierre : la pierre apparente ne se traite pas comme un enduit. Tonio choisit la méthode selon le support.")]),
   dict(t="Démoussage et décrassage de façade",
    p="Mousse, lichen, traces noires : le <strong>démoussage de façade</strong> et le décrassage redonnent sa teinte au mur. Voici ce que Tonio retire, et comment il vous le montre.",
    items=[("sprout", "Démoussage de façade", "Le démoussage de façade retire la mousse et les traces vertes avant qu'elles s'incrustent. Photos avant et après à l'appui."),
           ("alert", "Décrassage de façade", "Le décrassage de façade retire l'encrassement du mur : pollution, poussière, embruns. Vous voyez la différence sur les photos."),
           ("search", "Nettoyer ou ravaler ?", "Parfois un nettoyage suffit, parfois la façade est fissurée ou à repeindre. Tonio vous le dit sur place, et fait aussi le ravalement si besoin."),
           ("check", "Un chantier propre", "Le chantier est nettoyé avant que Tonio reparte, et les photos après vous sont envoyées.")]),
   dict(t="Traitement de façade : anti-mousse et hydrofuge",
    p="Après le nettoyage, un <strong>traitement de façade</strong> peut limiter le retour de la mousse et protéger le mur de l'eau. Tonio vous dit s'il est utile chez vous.",
    items=[("drop", "Traitement hydrofuge de façade", "Le traitement hydrofuge de façade limite l'eau que le mur absorbe. Tonio vous dit si votre enduit ou votre pierre en a besoin."),
           ("sprout", "Traitement anti-mousse de façade", "Un traitement anti-mousse sur la façade limite le retour des mousses et des traces vertes, surtout sur les murs exposés au nord."),
           ("layers", "Hydrofuge pour façade : enduit, crépi, pierre", "Le choix du traitement dépend du support. Tonio regarde le mur avant de proposer quoi que ce soit, et vous décidez."),
           ("shield-check", "Reprise gratuite", "Un défaut apparaît sur la zone traitée ? Tonio revient la reprendre gratuitement.")]),
   dict(t="Prix, tarif et devis de nettoyage de façade",
    p="<strong>Devis gratuit</strong>, établi sur place après examen de la façade. Le prix annoncé est le prix payé.",
    items=[("search", "Ce qui fait le prix d'un nettoyage de façade", "La surface, la hauteur, le support, l'état d'encrassement et le traitement choisi. Le prix se fixe sur ce que Tonio voit, pas au téléphone."),
           ("check", "Devis nettoyage de façade gratuit", f"Remplissez le formulaire ou appelez le {TEL} : le devis de nettoyage de façade est gratuit et sans engagement. Vous le signez quand vous voulez."),
           ("shield-check", "Un prix qui ne grossit pas", "Le tarif écrit sur le devis est celui que vous payez. Si Tonio découvre autre chose sur le mur, il vous envoie la photo et vous décidez, par écrit."),
           ("pin", "Un artisan à proximité", "Basé à Boucau, Tonio couvre Bayonne, Anglet, Biarritz, Bidart, Saint-Jean-de-Luz et le Sud-Landes : un artisan du coin, pas une plateforme.")]),
  ],
 ),
 # ===================== NOUVELLES PAGES (relance Google Ads nov. 2026) =====================
 # Groupe 1 — Couvreur / Fuite / Urgence : LP dédiée avec "couvreur" en H1 et dans tout le corps,
 # pour remonter le score de qualité des mots-clés "couvreur [ville]" (QS 1-2 sur l'ancienne /urgence).
 dict(
  out='couvreur/index.html', path='/couvreur/',
  # Positionnement B de l'analyse de marché du 16/11/2026 (analyses-marche/tonio-renov/RAPPORT.md) :
  # photos avant/après de SON toit, prix du devis tenu, reprise si défaut, pas de vendeur.
  title="Couvreur Bayonne, Anglet, Biarritz, Boucau : fuite et réparation de toiture · Tonio Rénov'",
  desc="Couvreur à Boucau pour Bayonne, Anglet et Biarritz : fuite, tuile cassée, gouttière. Photos avant/après de votre toit, prix du devis tenu, reprise si défaut.",
  img='/roof.jpg', pos='60% 40%', crop='40% 70%', alt="Couvreur sur toiture en tuiles canal, intervention Tonio Rénov' sur la Côte Basque",
  h1="Vous ne voyez pas votre toit ?<br><mark>Tonio vous envoie les photos</mark><br>avant et après.",
  sub="",
  ghost="Appeler Tonio pour qu'il vienne",
  avis='7', rev_sum='7 avis Google', rarete=False, marquee=True,
  proof=[("check", "Prix du devis tenu"), ("shield-check", "Reprise gratuite si défaut"), ("phone", "Pas de vendeur, Tonio en direct")],
  band=[("image", "Photos avant/après", "envoyées le jour même"), ("check", "Prix du devis tenu", "rien en plus sans votre accord"),
        ("shield-check", "Reprise gratuite", "si défaut sur la zone réparée"), ("shield", "Décennale + RC Pro", "artisan assuré"),
        ("home", "Artisan depuis 2009", "basé à Boucau")],
  signs=dict(t="Ce que vous ne voyez pas depuis le jardin",
    p="Vu d'en bas, un toit a souvent l'air en bon état. <strong>Là-haut, Tonio prend en photo ce qui laisse passer l'eau</strong> et vous le montre avant de chiffrer. Vous savez ce qui est abîmé, et ce qui ne l'est pas.",
    items=[("drop", "Fuite ou infiltration", "Taches au plafond, auréoles, humidité dans les combles : votre couvreur cherche d'où vient l'eau avant que la charpente souffre. Bâchage d'urgence si la pluie approche."),
           ("layers", "Tuiles déplacées ou cassées", "Après un coup de vent, des tuiles glissent ou se fendent. Tonio contrôle tout le toit, pas seulement le coin que vous voyez."),
           ("sprout", "Mousse qui soulève les tuiles", "Laissée en place, la mousse décolle les tuiles et garde l'humidité. On la traite avant que ça devienne une grosse réparation."),
           ("waves", "Faîtage, gouttière, solins fatigués", "Mortier qui s'effrite, gouttière qui déborde, solin de cheminée qui bâille : ce sont souvent eux qui laissent passer l'eau. Tonio les reprend avant l'hiver.")]),
  method_steps=[("Vous appelez Tonio", "Vous lui décrivez ce que vous voyez. Il passe chez vous rapidement, souvent le soir même ou le lendemain."),
                ("Photos et devis", "Tonio monte, prend en photo tuiles, faîtage, gouttières et solins, vous montre les photos et vous donne un prix sur place."),
                ("Réparation", "Il répare ce qui laisse passer l'eau, pas plus. S'il découvre autre chose, il vous envoie la photo et vous décidez."),
                ("Photos après", "Contrôle tuile par tuile, chantier nettoyé, et les photos après vous arrivent le jour même.")],
  real=dict(t="Ce que Tonio vous promet, noir sur blanc", items=[
    "Les photos avant/après de votre toit, envoyées le jour même",
    "Le prix du devis est le prix que vous payez. Rien en plus sans votre accord écrit",
    "Un défaut sur la zone réparée ? Tonio revient le reprendre gratuitement",
    "Pas de vendeur : Tonio vient, chiffre et répare lui-même",
    "Une réparation suffit ? Il vous le dit, photos à l'appui, au lieu de vous vendre une toiture neuve",
    "Un seul numéro, du devis jusqu'après les travaux"]),
  reviews=['g_vp', 'g_ml', 'g_m'],
  form=dict(t="Décrivez votre besoin", sub="<strong>30 secondes</strong>, sans engagement. Tonio vous rappelle <strong>sous 24h</strong>",
    t2="Décrivez votre besoin, Tonio vous rappelle", q1="Quel est votre besoin ?", q_coord="Où Tonio peut vous rappeler ?",
    etapes=[('probleme', "Quel est votre besoin ?", [("Fuite active / infiltration", "Fuite / infiltration", "drop"), ("Tuiles déplacées / cassées", "Tuiles déplacées / cassées", "layers"), ("Faîtage ou solins à reprendre", "Faîtage / solins", "waves"), ("Contrôle complet de toiture", "Contrôle complet", "search")]),
            ('toiture', "Quel type de toiture avez-vous ?", OPT_TOIT),
            ('delai', Q_DELAI, O_DELAI)],
    o1=[("Fuite active / infiltration", "Fuite / infiltration", "drop"), ("Tuiles déplacées / cassées", "Tuiles déplacées / cassées", "layers"), ("Faîtage ou solins à reprendre", "Faîtage / solins", "waves"), ("Contrôle complet de toiture", "Contrôle complet", "search")],
    q2="Quel type de toiture avez-vous ?", o2=OPT_TOIT, q3="Surface approximative de la toiture ?", o3=OPT_SURF),
  faq=[("Je vais vraiment voir les photos de mon toit ?", "Oui. Tonio prend votre toit en photo avant de commencer et une fois le travail fini, puis vous les envoie par SMS ou WhatsApp. Vous voyez ce qui a été fait sans monter sur l'échelle."),
       ("Le prix peut-il changer pendant les travaux ?", "Le prix du devis est celui que vous payez. Si Tonio découvre autre chose une fois sur le toit, il vous envoie la photo et vous décidez. Rien n'est fait en plus sans votre accord écrit."),
       ("Et si la fuite revient ?", "Appelez Tonio. Si le défaut vient de la zone qu'il a réparée, il revient la reprendre gratuitement."),
       ("Vous intervenez vite en cas de fuite ?", "Oui, les fuites passent en priorité. Tonio vous rappelle sous 24 h et intervient souvent sous 48 h sur Bayonne et la Côte Basque."),
       ("Vous êtes couvreur ou vous sous-traitez ?", "Tonio est couvreur et travaille lui-même. Pas de commercial, pas de sous-traitance : celui qui monte sur votre toit est celui qui a fait le devis."),
       ("Vous refaites aussi les toitures complètes ?", "Oui, Tonio fait aussi la réfection complète de toiture. Mais il commence par regarder ce qui peut être réparé : photos à l'appui, vous savez si une réparation suffit avant de parler de toiture neuve."),
       ("Combien coûte une réparation de toiture ?", "Ça dépend de l'accès au toit, du nombre de tuiles à remplacer et de l'état du faîtage et des solins. Tonio vous donne le prix sur place, dans un devis gratuit, avant de commencer."),
       ("Quelles garanties avez-vous ?", "Garantie décennale et assurance RC Pro sur tous les travaux, plus la reprise gratuite si un défaut apparaît sur la zone réparée."),
       FAQ_ZONE],
  cta=dict(t="Vous voulez savoir ce qui se passe sur votre toit ?", p="Tonio monte, prend les photos et vous donne <strong>un prix qu'il tient</strong>."),
  # Sections de contenu sous la zone : une par famille de mots-clés actifs du groupe
  # « Couvreur / urgence » (score de qualité : pertinence de la page de destination).
  seo=[
   dict(t="Couvreur à Bayonne, Anglet, Biarritz et Boucau",
    p="Tonio Rénov' est une <strong>entreprise de couverture</strong> basée à Boucau. C'est Tonio qui se déplace dans chaque ville, sans sous-traitance.",
    items=[("pin", "Couvreur à Bayonne", "Artisan couvreur à Bayonne pour la réparation de toiture, les tuiles cassées et le démoussage de toiture. Entreprise couvreur à Bayonne en direct : le devis toiture est gratuit et fait sur place, photos à l'appui. Couvreur zingueur à Bayonne pour les gouttières, le faîtage et les solins."),
           ("alert", "Urgence toiture à Bayonne", f"Fuite de toiture à Bayonne, tuile envolée après un coup de vent : l'urgence couvreur à Bayonne, c'est le {TEL}. Dépannage toiture à Bayonne avec bâchage si la pluie approche, puis réparation de toiture."),
           ("pin", "Couvreur à Anglet", "Artisan couvreur à Anglet, maisons et résidences. Entreprise couvreur à Anglet sans intermédiaire, devis couvreur à Anglet gratuit : réparation, tuiles, gouttières, fuite."),
           ("pin", "Couvreur à Biarritz", "Artisan couvreur à Biarritz, sur des toitures exposées au vent et aux embruns. Entreprise couvreur à Biarritz, devis couvreur à Biarritz gratuit et détaillé."),
           ("home", "Couvreur à Boucau", "Notre base. Couvreur à Boucau et à Tarnos : un artisan du quartier, joignable directement, qui connaît les toitures du secteur.")]),
   dict(t="Urgence toiture : fuite, infiltration, tuile cassée",
    p="Une <strong>fuite de toiture</strong> n'attend pas. Appelez : Tonio vous rappelle sous 24 h et intervient en priorité, souvent sous 48 h.",
    items=[("drop", "Fuite toiture et infiltration d'eau", "Taches au plafond, goutte à goutte dans les combles : votre couvreur cherche d'où vient l'infiltration d'eau par la toiture (tuile, solin, faîtage, gouttière) et la répare. Une urgence fuite toiture passe en priorité."),
           ("alert", "Dépannage toiture et bâchage d'urgence", "Toiture en urgence après une tempête : bâchage pour mettre la maison hors d'eau, puis réparation de toiture en urgence dès que la météo le permet."),
           ("layers", "Tuile cassée, remplacement de tuiles", "Une tuile cassée ou glissée suffit à laisser passer l'eau. Remplacement de tuiles canal, de tuiles mécaniques ou d'ardoises, à l'identique."),
           ("clock", "Urgence toiture 24h : ce qu'on vous promet", "Un appel ou une demande sur cette page, et Tonio vous rappelle sous 24 h. Il ne promet pas d'intervenir à toute heure : il promet de décrocher, de venir vite et de mettre votre toit hors d'eau.")]),
   dict(t="Réparation de toiture : ce qui suffit, pas plus",
    p="<strong>Artisan toiture</strong> : Tonio regarde d'abord ce qui peut être réparé. Il ne vous vend pas une toiture neuve quand une réparation suffit.",
    items=[("tools", "Réparation de toiture", "Réparation de toiture sur les tuiles, le faîtage, les rives et les solins de cheminée. Le couvreur répare ce qui laisse passer l'eau, sans vous vendre une toiture neuve."),
           ("search", "Rénovation de toiture : le bon diagnostic d'abord", "Avant de parler de rénovation de toiture, Tonio regarde ce qui peut être réparé. Photos à l'appui, vous savez si une réparation suffit. Si la couverture est vraiment à refaire, il vous le dit franchement."),
           ("waves", "Toit en zinc, couvreur zingueur", "Toit en zinc, gouttières zinc ou alu, chéneaux, noues : un couvreur zingueur pose et soude le zinc à l'étain."),
           ("shield-check", "Toiturier, couvreur, entreprise de couverture", "Toiturier, couvreur ou entreprise de couverture : c'est le même métier. Chez Tonio Rénov', le couvreur qui monte sur votre toit est celui qui signe le devis.")]),
   dict(t="Devis couvreur gratuit et tarif de réparation de toiture",
    p="<strong>Devis toiture gratuit</strong>, établi sur place après inspection. Le prix annoncé est le prix payé.",
    items=[("search", "Ce qui fait le tarif d'une réparation de toiture", "L'accès au toit, le nombre de tuiles à remplacer, l'état du faîtage et des solins, le type de couverture. Le tarif de réparation de toiture se fixe sur ce que le couvreur voit, pas au téléphone."),
           ("check", "Devis couvreur sans engagement", f"Remplissez le formulaire ou appelez le {TEL} : votre devis couvreur est gratuit, détaillé et sans engagement. Vous le signez quand vous voulez."),
           ("pin", "Un couvreur à proximité", "Vous cherchez un couvreur à proximité ? Basé à Boucau, Tonio couvre Bayonne, Anglet, Biarritz, Bidart, Saint-Jean-de-Luz et le Sud-Landes : un artisan couvreur du coin, pas une plateforme.")]),
  ],
 ),
 dict(
  out='refection-toiture/index.html', path='/refection-toiture/',
  # Nouvelle page du 18/11/2026 : groupe d'annonces « Réfection total toiture ». Tonio fait la réfection complète
  # et la toiture neuve. Brèche : la peur n°1 des gros chantiers est le devis qui grossit (« tout refaire, même la
  # charpente ») -> le prix du devis est le prix payé, photos à chaque étape, il vérifie d'abord si une réparation suffit.
  title="Réfection de toiture à Bayonne, Anglet, Biarritz : devis · Tonio Rénov'",
  desc="Réfection complète de toiture et toiture neuve à Bayonne, Anglet, Biarritz et Boucau. Le prix du devis est le prix payé, photos du chantier, reprise gratuite si défaut.",
  img='/roof.jpg', pos='58% 40%', crop='50% 60%', alt="Toiture en tuiles canal à refaire, chantier de réfection par Tonio Rénov' sur la Côte Basque",
  h1="Réfection de toiture&nbsp;:<br><mark>le prix du devis</mark><br>est le prix payé.",
  sub="",
  ghost="Appeler Tonio pour qu'il vienne",
  avis='7', rev_sum='7 avis Google', rarete=False, marquee=True,
  proof=[("check", "Prix du devis tenu"), ("image", "Photos du chantier"), ("search", "Réparer si ça suffit")],
  band=[("check", "Prix du devis tenu", "rien en plus sans accord écrit"), ("image", "Photos à chaque étape", "avant, pendant et après"),
        ("search", "Réparer si ça suffit", "vérifié avant de tout refaire"), ("shield-check", "Reprise gratuite", "si défaut sur la zone refaite"),
        ("shield", "Décennale + RC Pro", "artisan assuré"), ("home", "Artisan depuis 2009", "basé à Boucau")],
  signs=dict(t="Réparer ou refaire ? Tonio regarde d'abord",
    p="Refaire une toiture, c'est le plus gros chantier d'une maison. <strong>Avant de tout déposer, Tonio contrôle la couverture et la charpente</strong>, prend les photos et vous dit si une réparation suffit.",
    items=[("drop", "Fuites qui reviennent", "Après plusieurs réparations qui ne tiennent pas, la couverture est souvent à bout. Tonio vous montre d'où vient l'eau et si la réfection est vraiment la solution."),
           ("layers", "Tuiles fatiguées sur tout le toit", "Tuiles poreuses, cassées ou qui glissent un peu partout : réparer tuile par tuile ne suffit plus. Les photos vous montrent l'état de l'ensemble."),
           ("search", "Charpente à contrôler", "Une couverture ancienne peut cacher une charpente touchée par l'eau. Tonio la contrôle et vous dit si elle doit être reprise, photos à l'appui."),
           ("home", "Toiture neuve ou extension", "Une construction ou une extension a besoin d'une toiture complète. Tonio chiffre sur plans et sur place, avec un prix qu'il tient.")]),
  method_steps=[("Vous appelez Tonio", "Vous lui décrivez votre toit et votre projet. Il passe chez vous rapidement, souvent le soir même ou le lendemain."),
                ("Contrôle, photos et devis", "Tonio monte, contrôle la couverture et prend les photos. Si une réparation suffit, il vous le dit. Sinon, il chiffre la réfection et le prix du devis est le prix que vous payez."),
                ("Dépose et couverture neuve", "Dépose de l'ancienne couverture, contrôle de la charpente, liteaux, écran sous-toiture, tuiles neuves, faîtage et zinguerie. Les photos du chantier vous sont envoyées."),
                ("Nettoyage et photos après", "Le chantier est nettoyé avant que Tonio reparte, et les photos après vous sont envoyées. Un défaut sur la zone refaite : il revient gratuitement.")],
  real=dict(t="Ce que Tonio vous promet, noir sur blanc", items=[
    "Le prix du devis est le prix que vous payez. Rien en plus sans votre accord écrit",
    "Les photos de votre toit, avant, pendant et après le chantier",
    "Une réparation suffit ? Il vous le dit, photos à l'appui, au lieu de vous vendre une toiture neuve",
    "L'état de la charpente contrôlé, et dit franchement s'il faut la reprendre",
    "Pas de vendeur, pas de sous-traitance : Tonio vient, chiffre et travaille lui-même",
    "Un défaut sur la zone refaite ? Tonio revient le reprendre gratuitement"]),
  reviews=['g_vp', 'g_m', 'g_ml'],
  form=dict(t="Décrivez votre projet", sub="<strong>30 secondes</strong>, sans engagement. Tonio vous rappelle <strong>sous 24h</strong>",
    t2="Décrivez votre projet, Tonio vous rappelle", q1="Quel est votre projet ?", q_coord="Où Tonio peut vous rappeler ?",
    etapes=[('probleme', "Quel est votre projet ?", [("Refaire toute la toiture", "Toute la toiture", "home"), ("Refaire une partie de la toiture", "Une partie de la toiture", "layers"), ("Toiture neuve (construction, extension)", "Toiture neuve", "tools"), ("À évaluer, je ne sais pas encore", "À évaluer", "search")]),
            ('toiture', "Quel type de toiture avez-vous ?", OPT_TOIT),
            ('delai', Q_DELAI, O_DELAI)],
    o1=[("Refaire toute la toiture", "Toute la toiture", "home"), ("Refaire une partie de la toiture", "Une partie de la toiture", "layers"), ("Toiture neuve (construction, extension)", "Toiture neuve", "tools"), ("À évaluer, je ne sais pas encore", "À évaluer", "search")],
    q2="Quel type de toiture avez-vous ?", o2=OPT_TOIT, q3="Surface approximative de la toiture ?", o3=OPT_SURF),
  faq=[("Le prix du devis peut-il changer pendant la réfection ?", "Le prix du devis est celui que vous payez. Si Tonio découvre autre chose une fois la couverture déposée, il vous envoie la photo et vous décidez. Rien n'est fait en plus sans votre accord écrit."),
       ("Allez-vous vraiment me dire si une réparation suffit ?", "Oui. Tonio commence par contrôler la couverture. Si une réparation suffit, il vous le dit, photos à l'appui, et vous ne payez pas une toiture neuve pour rien. S'il faut refaire, il vous montre pourquoi."),
       ("Vais-je voir des photos de ma toiture ?", "Oui. Tonio prend votre toit en photo avant, pendant et après le chantier, et vous les envoie. Vous voyez l'ancienne couverture, l'état de la charpente et le travail fini sans monter sur l'échelle."),
       ("Faut-il refaire la charpente avec la toiture ?", "Pas forcément. Tonio contrôle l'état de la charpente quand la couverture est déposée et vous dit si elle doit être reprise, photos à l'appui. Rien n'est ajouté au devis sans votre accord écrit."),
       ("Que comprend une réfection complète de toiture ?", "La dépose de l'ancienne couverture, le contrôle de la charpente, les liteaux, l'écran sous-toiture, les tuiles neuves, le faîtage et la zinguerie, puis le nettoyage du chantier. Le devis détaille ce qui est prévu."),
       ("Faites-vous aussi les toitures neuves et les constructions ?", "Oui, Tonio construit des toitures complètes : maison neuve, extension, couverture neuve. Il chiffre sur place ou sur plan, et le prix du devis est le prix que vous payez."),
       ("Combien coûte la réfection d'une toiture ?", "Ça dépend de la surface, de la forme du toit, du type de tuiles et de l'état de la charpente. Tonio vous donne le prix sur place, dans un devis gratuit, avant de commencer. Ce prix est celui que vous payez."),
       ("Combien de temps dure une réfection de toiture ?", "Ça dépend de la surface et de l'état de la charpente. Tonio vous en parle sur place, au moment du devis."),
       ("Vous êtes couvreur ou vous sous-traitez ?", "Tonio est couvreur et travaille lui-même. Pas de commercial, pas de sous-traitance : celui qui monte sur votre toit est celui qui a fait le devis."),
       ("Quelles garanties avez-vous ?", "Garantie décennale et assurance RC Pro sur les travaux, plus la reprise gratuite si un défaut apparaît sur la zone refaite."),
       FAQ_ZONE],
  cta=dict(t="Votre toit se répare-t-il ou se refait-il ?", p="Tonio monte, prend les photos et vous donne <strong>un devis dont le prix est le prix payé</strong>."),
  # Sections de contenu sous la zone : une par famille de mots-clés du groupe « Réfection total toiture »
  # (score de qualité : pertinence de la page de destination).
  seo=[
   dict(t="Réfection de toiture à Bayonne, Anglet, Biarritz et Boucau",
    p="Tonio Rénov' est une <strong>entreprise de couverture</strong> basée à Boucau. C'est Tonio, le couvreur, qui se déplace dans chaque ville, sans sous-traitance, pour la réfection de votre toiture.",
    items=[("pin", "Réfection de toiture à Bayonne", "Couvreur pour la réfection de toiture à Bayonne : contrôle de la couverture, dépose, couverture neuve. Le devis est gratuit, fait sur place, et son prix est celui que vous payez."),
           ("pin", "Réfection de toiture à Anglet", "Réfection de toiture à Anglet pour maisons et résidences : un artisan sans intermédiaire, qui vous envoie les photos du chantier."),
           ("pin", "Réfection de toiture à Biarritz et sur la Côte Basque", "Les toitures de Biarritz, Bidart ou Saint-Jean-de-Luz subissent le vent et les embruns. Tonio contrôle l'ensemble de la couverture avant de vous dire s'il faut refaire."),
           ("home", "Couvreur à Boucau et Tarnos", "Notre base. Un couvreur du quartier, joignable directement, qui connaît les toitures du secteur.")]),
   dict(t="Refaire sa toiture : les étapes d'une réfection complète",
    p="<strong>Refaire un toit</strong>, c'est déposer l'ancienne couverture et en poser une neuve. Voici ce que contient une réfection complète de toiture, étape par étape.",
    items=[("layers", "Dépose de l'ancienne couverture", "Les anciennes tuiles sont déposées. Tonio prend les photos de ce que cache la couverture avant d'aller plus loin."),
           ("search", "Contrôle de la charpente", "La charpente est contrôlée à nu. Tonio vous dit si elle est saine ou si elle doit être reprise, et vous le montre en photo avant tout ajout au devis."),
           ("check", "Liteaux, écran sous-toiture et tuiles neuves", "Pose des liteaux, de l'écran sous-toiture, puis des tuiles neuves, rang après rang, avec le faîtage."),
           ("waves", "Zinguerie et nettoyage du chantier", "Gouttières, rives et solins sont repris pour que l'eau s'écoule bien. Le chantier est nettoyé avant que Tonio reparte.")]),
   dict(t="Rénovation de toiture, remplacement et changement de couverture",
    p="<strong>Rénovation de toiture</strong>, remplacement de toiture : Tonio commence par regarder ce qui peut être gardé ou réparé, puis chiffre ce qui doit vraiment être refait.",
    items=[("search", "Rénovation de toiture : réparer ou refaire", "Avant de parler de rénovation de toiture, Tonio contrôle la couverture. Photos à l'appui, vous savez si une réparation suffit ou si le toit est à refaire."),
           ("layers", "Remplacement de toiture", "Remplacement de toiture partiel ou complet : tuiles canal, tuiles mécaniques ou ardoises, selon ce qui est posé chez vous."),
           ("home", "Changer sa toiture", "Vous voulez changer votre toiture parce qu'elle fuit ou qu'elle est fatiguée ? Tonio vous dit franchement si c'est utile, et ce que le changement comprend."),
           ("shield-check", "Un seul interlocuteur", "Le couvreur qui contrôle votre toit est celui qui signe le devis et qui travaille sur le chantier. Pas de vendeur entre vous et lui.")]),
   dict(t="Toiture neuve, couverture neuve et construction de toiture",
    p="Maison neuve, extension, couverture à remplacer : <strong>une toiture neuve</strong> se chiffre sur place ou sur plan, avec un prix que Tonio tient.",
    items=[("home", "Construction de toiture", "Construction de toiture pour une maison neuve ou une extension : Tonio chiffre la couverture complète, du faîtage à la zinguerie."),
           ("layers", "Couverture neuve", "Couverture neuve en tuiles : liteaux, écran sous-toiture, tuiles et faîtage posés par Tonio lui-même."),
           ("tools", "Toiture neuve ou réfection ?", "Sur une maison existante, on parle de réfection : dépose puis couverture neuve. Sur une construction, c'est une toiture neuve. Tonio fait les deux."),
           ("check", "Un devis détaillé", "Le devis indique ce qui est prévu, poste par poste. Le prix du devis est le prix payé, rien en plus sans votre accord écrit.")]),
   dict(t="Prix, tarif et devis de réfection de toiture",
    p="<strong>Devis gratuit</strong>, établi sur place après contrôle de la toiture. Le prix annoncé est le prix payé.",
    items=[("search", "Ce qui fait le prix d'une réfection de toiture", "La surface, la forme du toit, le type de tuiles, l'accès au chantier et l'état de la charpente. Le prix de la réfection se fixe sur ce que Tonio voit, pas au téléphone."),
           ("check", "Devis réfection de toiture gratuit", f"Remplissez le formulaire ou appelez le {TEL} : le devis de réfection de toiture est gratuit et sans engagement. Vous le signez quand vous voulez."),
           ("shield-check", "Un prix qui ne grossit pas", "Le tarif écrit sur le devis est celui que vous payez. Si une surprise apparaît sur le chantier, Tonio vous envoie la photo et vous décidez, par écrit."),
           ("pin", "Un couvreur à proximité", "Basé à Boucau, Tonio couvre Bayonne, Anglet, Biarritz, Bidart, Saint-Jean-de-Luz et le Sud-Landes : un couvreur du coin, pas une plateforme.")]),
  ],
 ),
 # Groupe 2 — Zinguerie / Faîtage : panier moyen 1500-4000 €, saison pré-hiver + post-tempête.
 dict(
  out='zinguerie/index.html', path='/zinguerie/',
  title="Zinguerie à Bayonne — gouttières, faîtage, solins · Tonio Rénov'",
  desc="Zinguerie sur la Côte Basque : pose de gouttières zinc ou alu, reprise de faîtage, solins de cheminée. Artisan zingueur local, devis gratuit, garantie décennale.",
  img='/roof.jpg', pos='52% 45%', crop='48% 68%', alt="Faîtage et gouttières zinc sur toiture tuiles, zinguerie Tonio Rénov'",
  h1="Gouttières, faîtage, solins ?<br><mark>Tonio Rénov' les refait.</mark>",
  sub="<strong>Zinguerie à Bayonne, Anglet, Boucau</strong> : pose de gouttières zinc ou alu, reprise de faîtage au mortier, solins de cheminée étanches. Artisan zingueur local, on fixe au lieu de rafistoler. Garantie décennale.",
  ghost="Appeler Tonio pour qu'il vienne", last_trust=("clock", "Avant la tempête", "devis sous 24h"),
  signs=dict(t="La zinguerie, c'est ce qui tient la toiture pendant l'hiver",
    p="Ce qui lâche d'abord en tempête, ce n'est presque jamais la tuile — c'est la <strong>gouttière</strong>, le <strong>faîtage</strong>, le <strong>solin de cheminée</strong>. Trois points de zinguerie qui, bien repris, évitent 90 % des infiltrations.",
    items=[("waves", "Gouttière qui déborde ou fuit", "Débris, pente qui s'est faussée, soudure fatiguée : la gouttière lâche d'abord. Zinguerie à reprendre, pas à rafistoler."),
           ("layers", "Faîtage qui s'effrite", "Mortier qui part en poussière, tuiles de faîte qui bougent : première zone d'envol en coup de vent."),
           ("home", "Solin de cheminée fatigué", "Bavettes zinc décollées, mortier fissuré autour du conduit : par là l'eau entre et file dans la charpente."),
           ("drop", "Chéneau qui déborde", "Un chéneau mal pentu stagne l'eau et finit par la laisser passer sous les tuiles. Zinguerie à repenser proprement.")]),
  method_steps=[("Vous nous appelez", "Décrivez votre zinguerie — gouttière, faîtage, solin — on cale une visite gratuite rapidement."),
    ("Diagnostic zinguerie", "On monte, on regarde l'état réel du zinc et du mortier, devis détaillé sous 24h."),
    ("Pose zinguerie", "Gouttières zinc ou alu posées à l'ancienne, faîtage repris au mortier bâtard, solins étanchés."),
    ("Contrôle final", "Test d'écoulement, vérification des fixations, nettoyage du chantier avant de repartir.")],
  real=dict(t="Zinguerie refaite dans les règles, pas rafistolée", items=["Pose de gouttières zinc ou aluminium soignée", "Reprise de faîtage au mortier bâtard, pas au silicone", "Solins cheminée refaits, bavettes zinc neuves", "Chantier couvert par la garantie décennale"]),
  reviews=['julien', 'pierre', 'marie'],
  form=dict(t="Votre devis zinguerie en 6 questions", sub="<strong>30 secondes</strong>, sans engagement — on vous rappelle <strong>sous 24h</strong>",
    t2="Recevez votre devis zinguerie", q1="Qu'est-ce qu'il faut reprendre ?",
    o1=[("Gouttières à remplacer / à poser", "Gouttières à (re)poser", "waves"), ("Faîtage à reprendre", "Faîtage à reprendre", "layers"), ("Solin de cheminée fuyant", "Solin cheminée", "home"), ("Je ne sais pas, à évaluer", "À évaluer sur place", "help")],
    q2="Quel type de toiture avez-vous ?", o2=OPT_TOIT, q3="Surface approximative de la toiture ?", o3=OPT_SURF),
  faq=[("Zinc ou aluminium pour les gouttières ?", "Le zinc tient 40-50 ans sur la Côte Basque, l'alu entre 20-30 ans et coûte moins cher au départ. On vous explique les deux options sur place en fonction de votre toiture et de l'exposition aux embruns."),
       ("Pourquoi reprendre le faîtage avant l'hiver ?", "C'est la zone qui prend le vent en premier. Un faîtage dont le mortier s'effrite finit par soulever une tuile de faîte au prochain coup de vent — ensuite c'est l'eau qui s'infiltre sous toute la toiture."),
       ("Vous reprenez au mortier ou au silicone ?", "Au mortier bâtard, comme le vrai métier. Le silicone sur un faîtage, c'est du dépannage de 2-3 ans, pas une reprise de zinguerie."),
       FAQ_GARANTIE,
       FAQ_ZONE],
  cta=dict(t="Une zinguerie refaite tient 30 ans", p="<strong>Devis gratuit sous 24h</strong> — avant la prochaine tempête."),
 ),
 # Groupe 3 — Peinture intérieure : panier 1500-5000 €, saison 100% hiver (chantier intérieur).
 dict(
  out='peinture-interieure/index.html', path='/peinture-interieure/',
  title="Peintre à Bayonne, Anglet, Biarritz — peinture intérieure · Tonio Rénov'",
  desc="Artisan peintre à Bayonne, Anglet, Biarritz et Boucau : peinture intérieure de salon, chambre, appartement et maison. Entreprise de peinture, devis peintre gratuit, garantie décennale.",
  img='/img/peinture-apres.jpg', pos='50% 50%', crop='30% 58%', alt="Intérieur de maison fraîchement peint par Tonio Rénov'",
  h1="Peintre intérieur :<br><mark>chantier propre chaque soir,</mark><br>sur toute la Côte Basque.",
  sub="<strong>Salon, chambre, appartement complet, maison.</strong> Protection intégrale du mobilier, finitions soignées, on repart propre chaque fin de journée. Entreprise de peinture Côte Basque et Sud-Landes, garantie décennale.",
  ghost="Appeler Tonio pour qu'il vienne", last_trust=("clock", "Devis rénovation", "chantier planifié"),
  signs=dict(t="Une bonne peinture, c'est 20 % de produit et 80 % de préparation",
    p="Le résultat ne tient pas à la couleur, il tient à ce qu'on fait <strong>avant</strong> de la poser. Dégraissage, rebouchage, ponçage, sous-couche : la peinture Tollens vient en dernier.",
    items=[("roller", "Préparation complète des supports", "Rebouchage des fissures, ponçage des zones écaillées, dégraissage : la peinture tient parce qu'elle accroche sur un support propre."),
           ("shield", "Protection du mobilier et des sols", "Bâches sur meubles, adhésifs sur plinthes et interrupteurs, protection des sols — on peint autour de la vie, pas à la place."),
           ("layers", "Peintures professionnelles Tollens", "Pas de peinture bricomarché. Produits pro, pouvoir couvrant élevé, teintes stables dans le temps, finition qui ne jaunit pas."),
           ("check", "Chantier propre chaque soir", "On nettoie et on range chaque fin de journée. Vous pouvez vivre dans la pièce voisine sans tomber sur un chantier.")]),
  method_steps=[("Vous nous appelez", "Décrivez votre projet — pièce, surface, couleur — on cale une visite gratuite rapidement."),
    ("Diagnostic & devis", "On regarde l'état des murs et plafonds, on vous propose teintes et finition, devis détaillé sous 24h."),
    ("Préparation & peinture", "Protection, rebouchage, sous-couche, 2 couches de finition Tollens, moulures sur demande."),
    ("Contrôle final", "On vérifie chaque angle, chaque raccord, on nettoie avant de repartir.")],
  real=dict(t="Peinture intérieure soignée, pas bâclée", items=["Préparation complète : rebouchage, ponçage, sous-couche", "Peintures professionnelles Tollens, finition mate ou satinée", "Rénovation peinture d'une pièce, d'un appartement ou d'une maison entière", "Entreprise de peinture artisanale, pas de sous-traitance", "Protection intégrale du mobilier et des sols", "Chantier couvert par la garantie décennale"]),
  reviews=['sofia', 'camille', 'amadou'],
  form=dict(t="Votre devis peinture en 6 questions", sub="<strong>30 secondes</strong>, sans engagement — on vous rappelle <strong>sous 24h</strong>",
    t2="Recevez votre devis peinture intérieure", q1="Qu'est-ce que vous voulez repeindre ?",
    o1=[("Un salon / séjour", "Salon / séjour", "home"), ("Une ou plusieurs chambres", "Chambre(s)", "home"), ("Un appartement complet", "Appartement complet", "home"), ("Autre pièce / détail", "Autre / à préciser", "help")],
    q2="Dans quel état sont les murs ?", o2=[("Peinture ancienne à refaire", "Peinture ancienne", "roller"), ("Murs abîmés, fissures à reboucher", "Murs abîmés", "crack"), ("Support neuf (plâtre, enduit frais)", "Support neuf", "layers"), ("Je ne sais pas, à évaluer", "À évaluer sur place", "help")],
    q3="Surface approximative à peindre ?", o3=[("Moins de 20 m²", "Moins de 20 m²", "home"), ("20 à 50 m²", "20 à 50 m²", "home"), ("50 à 100 m²", "50 à 100 m²", "home"), ("Plus de 100 m²", "Plus de 100 m²", "home")]),
  faq=[("Vous travaillez pièce par pièce ou appartement complet ?", "Les deux. Pièce seule (chambre, salon) ou chantier complet avant emménagement. On s'adapte à votre présence sur place et à vos contraintes de date."),
       ("Combien de couches posez-vous ?", "Sur un support préparé : une sous-couche + deux couches de finition. C'est ce qui donne un rendu uniforme qui tient dans le temps, pas une seule couche qu'on repose dans 2 ans."),
       ("Vous bougez les meubles ?", "Pour une pièce vide, on prépare tout. Pour une pièce habitée, on protège les meubles sur place et on travaille autour — ou on les déplace ensemble si vous préférez."),
       ("Quelles peintures utilisez-vous ?", "Peintures professionnelles Tollens, en finition mate, satinée ou veloutée selon la pièce. On vous explique sur place laquelle convient à l'exposition et à l'usage."),
       ("Combien coûte la peinture d'une pièce ?", "Ça dépend de la surface, de l'état des murs et de la finition. Tonio passe voir la pièce et vous donne le prix dans un devis peinture gratuit, avant les travaux."),
       FAQ_GARANTIE,
       FAQ_ZONE],
  cta=dict(t="Un intérieur refait, c'est l'hiver qui change", p="<strong>Devis gratuit sous 24h</strong>, aucun engagement."),
  # Sections de contenu sous la zone : une par famille de mots-clés actifs du groupe
  # « Peinture intérieure ». ATTENTION : peinture-interieure/index.html contient des
  # retouches faites à la main (hero, formulaire, CSS des options) absentes de ce fichier ;
  # ne pas régénérer cette page sans les reporter ici.
  seo=[
   dict(t="Peintre à Bayonne, Anglet, Biarritz et Boucau",
    p="Tonio Rénov' est une <strong>entreprise de peinture</strong> basée à Boucau. Le même artisan peintre vient chiffrer, puis peindre chez vous.",
    items=[("pin", "Peintre à Bayonne", "Artisan peintre à Bayonne pour la peinture intérieure d'un salon, d'une chambre ou d'un appartement entier. Peintre en bâtiment à Bayonne et entreprise de peinture à Bayonne en direct, pour la rénovation peinture des maisons comme des appartements."),
           ("pin", "Peintre à Anglet", "Artisan peintre à Anglet, en maison ou en appartement. Entreprise de peinture à Anglet sans sous-traitance, devis peintre à Anglet gratuit et fait sur place."),
           ("pin", "Peintre à Biarritz", "Artisan peintre à Biarritz, pour des intérieurs qui vivent avec l'humidité de la côte. Entreprise de peinture à Biarritz, devis peintre à Biarritz gratuit."),
           ("home", "Peintre à Boucau", "Notre base. Peintre à Boucau et à Tarnos : un artisan du quartier, joignable directement.")]),
   dict(t="Peinture intérieure : salon, chambre, appartement, maison",
    p="<strong>Peintre intérieur</strong> : murs, plafonds, boiseries et moulures, pièce par pièce ou toute la maison.",
    items=[("home", "Peinture du salon et du séjour", "La pièce qu'on voit le plus. Peinture du salon avec préparation des murs, plafond compris, en finition mate ou veloutée."),
           ("home", "Peinture d'appartement", "Appartement complet avant une vente, une location ou un emménagement : peinture de toutes les pièces, planning annoncé à l'avance."),
           ("home", "Peinture intérieure de maison", "Peintre pour l'intérieur de la maison : chambres, couloirs, cage d'escalier, plafonds. Une entreprise de peinture intérieure qui protège le mobilier et repart propre."),
           ("roller", "Refaire la peinture, rénovation peinture", "Murs jaunis, fissures, peinture qui s'écaille : refaire une peinture, c'est reboucher, poncer, passer une sous-couche, puis deux couches de finition."),
           ("image", "Peintre décorateur", "Moulures, couleur d'accent, mur de tête de lit, teintes choisies selon la lumière de la pièce : la partie peintre décorateur du métier.")]),
   dict(t="Un artisan peintre professionnel, pas une plateforme",
    p="Trouver un <strong>artisan peintre</strong> sérieux, c'est trouver quelqu'un qui prépare avant de peindre.",
    items=[("award", "Peintre professionnel en bâtiment", "Peintre en bâtiment : préparation des supports, peintures professionnelles Tollens, garantie décennale et RC Pro. Artisan certifié RGE."),
           ("shield", "Trouver un artisan peintre de confiance", "5/5 sur 23 avis Google, un seul interlocuteur du devis à la fin du chantier, aucune sous-traitance."),
           ("check", "Chantier propre, mobilier protégé", "Bâches, adhésifs, sols protégés, nettoyage chaque soir : vous continuez à vivre chez vous pendant les travaux de peinture.")]),
   dict(t="Devis peinture gratuit et tarif au m²",
    p="<strong>Devis peintre gratuit</strong>, établi sur place. Le prix des travaux de peinture est fixé avant le début du chantier.",
    items=[("search", "Tarif peinture au m²", "Le prix au m2 dépend de l'état des murs (rebouchage, ponçage), du nombre de couches, de la hauteur sous plafond et de la finition. Votre devis peinture intérieure indique la surface à peindre et le prix des travaux de peinture au m2."),
           ("layers", "Tarif peinture plafond au m²", "Un plafond se peint plus lentement qu'un mur : protection complète, travail en hauteur, deux couches. Son tarif de peinture au m2 est donc souvent un peu plus élevé."),
           ("clock", "Taux horaire d'un peintre ou prix total", "Plutôt qu'un taux horaire qui laisse la facture ouverte, vous recevez un devis de travaux de peinture avec le prix total, avant de commencer."),
           ("check", "Devis peinture sans engagement", f"Devis peinture gratuit et sans engagement : 6 questions dans le formulaire, ou un appel au {TEL}.")]),
  ],
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
 'nettoyage-facade/index.html': dict(mode='slider', b='ravalement-avant', a='ravalement-apres', tb='Avant', ta='Après',
                    ab="Mur dont la peinture s'écaille (photo d'illustration)", aa="Mur blanc propre (photo d'illustration)",
                    bgm='ravalement-bg-methode', bgc='ravalement-bg-cta'),
 'ravalement/index.html': dict(mode='slider', b='ravalement-avant', a='ravalement-apres', tb='Avant', ta='Après',
                    ab="Mur dont la peinture s'écaille (photo d'illustration)", aa="Mur blanc fraîchement repeint (photo d'illustration)",
                    bgm='ravalement-bg-methode', bgc='ravalement-bg-cta'),
 # Nouvelles pages — photos actuelles sont des copies des sets existants (placeholders), à remplacer par de vraies photos dédiées
 'couvreur/index.html': dict(mode='split', b='couvreur-avant', a='couvreur-apres', tb='Le problème', ta="L'intervention",
                    ab="Plafond abîmé par une infiltration d'eau (photo d'illustration — à remplacer)", aa="Couvreur au travail sur une toiture en tuiles (photo d'illustration — à remplacer)",
                    bgm='couvreur-bg-methode', bgc='couvreur-bg-cta'),
 'refection-toiture/index.html': dict(mode='split', b='couvreur-avant', a='couvreur-apres', tb='Le problème', ta="L'intervention",
                    ab="Plafond abîmé par une infiltration d'eau (photo d'illustration)", aa="Couvreur au travail sur une toiture en tuiles (photo d'illustration)",
                    bgm='couvreur-bg-methode', bgc='couvreur-bg-cta'),
 'zinguerie/index.html': dict(mode='slider', b='zinguerie-avant', a='zinguerie-apres', tb='Avant', ta='Après',
                    ab="Gouttière encrassée et bord de toit sale (photo d'illustration — à remplacer par gouttière zinc neuve)", aa="Gouttière propre et bien entretenue (photo d'illustration — à remplacer)",
                    bgm='zinguerie-bg-methode', bgc='zinguerie-bg-cta'),
 'peinture-interieure/index.html': dict(mode='slider', b='peinture-avant', a='peinture-apres', tb='Avant', ta='Après',
                    ab="Mur à repeindre (photo d'illustration — à remplacer par chantier peinture intérieure réel)", aa="Mur repeint (photo d'illustration — à remplacer)",
                    bgm='peinture-bg-methode', bgc='peinture-bg-cta'),
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

# Questions communes à toutes les pages (audit Google Ads du 13/11/2026 : qualifier la demande).

def opts(name, options, first_focus=False):
    out = []
    for value, label, icon in options:
        out.append(f'<button type="button" class="opt" data-value="{value}" aria-pressed="false">{ic(icon)}<span>{label}</span><span class="tick">{ic("check")}</span></button>')
    return f'<div class="opts" data-field="{name}" role="group">' + ''.join(out) + '</div>'

def kw_sections(p):
    """Sections de contenu par famille de mots-clés (score de qualité). Lignes .sign
    sans .reveal : le texte reste visible même sans défilement ni JavaScript."""
    out = []
    for b in p.get('seo', []):
        rows = ''.join(f'<li class="sign"><span class="sign-ic">{ic(i)}</span><div><h3>{t}</h3><p>{d}</p></div></li>' for i, t, d in b['items'])
        out.append(f'''<section class="sec sec-light kw" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head center">{h2(b['t'])}<p class="lead">{b['p']}</p></div>
    <ul class="kw-list">{rows}</ul>
  </div>
</section>
''')
    return ''.join(out)

# Typographie française : espace insécable avant : ? ! ; » et après «, et dans « 24 h »,
# sur le texte visible seulement (pas dans les balises, <script> ni <style>).
def typo_fr(html):
    def fix(s):
        s = re.sub(r' ([:?!;»])', '\u00a0\\1', s)
        s = s.replace('« ', '«\u00a0')
        return re.sub(r'(\d) h\b', '\\1\u00a0h', s)
    out = []
    for part in re.split(r'(?s)(<script.*?</script>|<style.*?</style>|<[^>]+>)', html):
        out.append(part if part.startswith('<') else fix(part))
    return ''.join(out)

def render(p):
    s = SITE
    M = MEDIA[p['out']]
    h1_inner, _ = split_words(p['h1'])
    h1 = f'<h1 aria-label="{plain(p["h1"])}">{h1_inner}</h1>'
    trust = [("award", "Plus de 500 chantiers", "sur la Côte Basque"), ("shield-check", "Garantie décennale", "sur tous nos travaux"),
             ("shield", "Assurance RC Pro", "artisan assuré"), ("award", "Certifié RGE", "qualification reconnue"), p.get('last_trust')]
    trust[0] = ("home", trust[0][1], trust[0][2])
    if p.get('band'): trust = p['band']
    proof = ''.join(f'<span>{ic(i)}{t}</span>' for i, t in p.get('proof', [("check", "Visite gratuite"), ("shield", "Sans engagement")]))
    rarete = '' if p.get('rarete') is False else '<p class="rarete reveal on-dark" style="--d:1.5"><em>Tonio prend 6 à 8 nouveaux chantiers par mois pour garder la qualité, pas à la chaîne.</em></p>'
    band = ''.join(f'<li>{ic(i)}<div><b>{a}</b><small>{b}</small></div></li>' for i, a, b in trust)
    band_html = (f'<section class="band marquee" aria-label="Nos garanties"><div class="band-track"><ul>{band}</ul><ul aria-hidden="true">{band}</ul></div></section>'
                 if p.get('marquee') else f'<section class="band" aria-label="Nos garanties"><div class="wrap"><ul>{band}</ul></div></section>')
    # Anneau de vraies photos de Tonio (prestation de la page) à la place de la bande de garanties.
    # 12 emplacements (6 colonnes × 2) : les photos tournent en boucle s'il y en a moins.
    if p.get('ring'):
        ph = [(('' if s.startswith('/') else '/') + s, alt) for s, alt in p['ring']]
        cols = ''.join(
            f'<div class="ring3d-col" style="--a:{c * 30}deg">'
            + ''.join(f'<div class="ring3d-v"><img src="{ph[(c * 2 + k) % len(ph)][0]}" alt="{ph[(c * 2 + k) % len(ph)][1]}" loading="lazy" decoding="async" draggable="false"></div>' for k in (0, 1))
            + '</div>' for c in range(6))
        band_html = f'<section class="ring-sec" aria-label="Chantiers réalisés par Tonio"><div class="ring3d"><div class="ring3d-scene"><div class="ring3d-rot">{cols}</div></div></div></section>'
    # Offre limitée au mois en cours : date de fin écrite par app.js (dernier jour du mois).
    fin = '<span data-fin-mois>la fin du mois</span>'
    signs = ''.join(f'<li class="sign reveal" style="--d:{k}"><span class="sign-ic">{ic(i)}</span><div><h3>{t}</h3><p>{d}</p></div></li>' for k, (i, t, d) in enumerate(p['signs']['items']))
    steps = ''.join(f'<li class="step reveal" style="--d:{k}"><span class="step-n">{k+1}</span><h3>{t}</h3><p>{d}</p></li>' for k, (t, d) in enumerate(p['method_steps']))
    real = ''.join(f'<li>{ic("check")}<span>{t}</span></li>' for t in p['real']['items'])
    revs = []
    for k, key in enumerate(p['reviews']):
        r = R[key]; big = ' big' if k == 0 and not p.get('marquee') else ''
        revs.append(f'<figure class="rev{big} reveal" style="--d:{k}">{stars()}<blockquote>« {r["q"]} »</blockquote><figcaption class="rev-who"><span class="rev-av">{r["i"]}</span><span><b>{r["n"]}</b><small>{r["v"]}</small></span></figcaption></figure>')
    f = p['form']
    prog = '<i></i>' * 6
    faq = ''.join(f'<details><summary>{q}{ic("plus")}</summary><p>{a}</p></details>' for q, a in p['faq'])
    zones = ''.join(f'<li class="{"base" if z=="Boucau" else ""}">{ic("pin")}{z}</li>' for z in ZONES)
    tel = f'tel:{s["tel"]}'
    sig_h2 = h2(p['signs']['t'])
    method_h2 = h2("Tonio vient voir avant de chiffrer", 'on-dark')
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
        etapes = f.get('etapes') or [('probleme', f['q1'], f['o1']), ('toiture', f['q2'], f['o2']), ('surface', f['q3'], f['o3']),
                                     ('delai', Q_DELAI, O_DELAI), ('statut', Q_STATUT, O_STATUT)]
        n_et = len(etapes) + 1
        court = bool(f.get('etapes'))
        compte = lambda k: '' if court else f'<span class="fcount">Étape {k} sur {n_et}</span>'
        champs = (
            (f'<div class="field"><label for="f-nom-{pos}">Prénom</label>'
             f'<input id="f-nom-{pos}" data-champ="nom" type="text" placeholder="Votre prénom" autocomplete="given-name"></div>' if court else
             f'<div class="field"><label for="f-nom-{pos}">Nom</label>'
             f'<input id="f-nom-{pos}" data-champ="nom" type="text" placeholder="Votre nom" autocomplete="name"></div>')
            + f'<div class="field"><label for="f-tel-{pos}">Téléphone</label>'
            f'<input id="f-tel-{pos}" data-champ="tel" type="tel" inputmode="tel" placeholder="06 12 34 56 78" autocomplete="tel"></div>'
            + ('' if court else
            f'<div class="field"><label for="f-ville-{pos}">Ville</label>'
            f'<input id="f-ville-{pos}" data-champ="ville" type="text" placeholder="Bayonne, Anglet, Biarritz…" autocomplete="address-level2"></div>')
        )
        q_coord = f.get('q_coord', 'Vos coordonnées pour le rappel')
        fsteps = ''.join(f'<div class="fstep{" active" if k == 1 else ""}" data-step="{k}">{compte(k)}<p class="fq" tabindex="-1" data-focus>{q}</p><span class="fhint">Cliquez sur votre réponse</span>{opts(fld, o)}</div>\n        '
                         for k, (fld, q, o) in enumerate(etapes, 1))
        fsteps += f'<div class="fstep" data-step="{n_et}">{compte(n_et)}<p class="fq" tabindex="-1" data-focus>{q_coord}</p>{champs}</div>\n        '
        fsteps += f'<div class="fstep" data-step="{n_et + 1}" aria-live="polite">'
        corps = f'''<div class="devis-shell">
      <div class="progress" aria-hidden="true">{'<i></i>' * n_et}</div>
      <form class="devis-form" data-pos="{pos}" novalidate>
        {fsteps}<div class="done"><div class="done-ic">{ic("check")}</div><h3 tabindex="-1" data-focus>Demande envoyée</h3><p>Merci ! Un artisan {s['name']} vous rappelle sous 24h pour affiner le devis.</p><a class="btn btn-call" href="{tel}"><span class="sh-spark" aria-hidden="true"><span class="sh-slide"><span class="sh-spin"></span></span></span><span class="sh-back" aria-hidden="true"></span>{ic("phone")}<span>Ou appelez le {s['phone']}</span></a></div></div>
        <div class="factions"><button type="button" class="fback" disabled>{ic("back")}Précédent</button>{next_btn}</div>
      </form>
    </div>'''
        if hero:
            return f'''<div class="hero-form" id="{ident}">
      <div class="hf-head"><h2 class="hf-t">{titre}</h2>{f'<p class="hf-fin">Offre valable jusqu’au {fin}</p>' if p.get('offre_mois') else (f'<p class="hf-fin">{p["offre_note"]}</p>' if p.get('offre_note') else '')}</div>
      {corps}
    </div>'''
        return f'''<section class="sec sec-light devis" id="{ident}">
  <div class="wrap">
    <div class="sec-head center">{titre}<p class="lead">{f['sub']}{f'<br><span class="offre-fin">Offre valable jusqu’au {fin}.</span>' if p.get('offre_mois') else ''}</p></div>
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
<!-- Google Ads Conversion Tag (direct, backup de GTM) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-18220615555"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', 'AW-18220615555');
</script>
<!-- End Google Ads Conversion Tag -->
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
    <a class="brand" href="#top" aria-label="{s['name']} — haut de page">{mark()}<span><b>{s['name']}</b><small>Toiture &amp; peinture · Boucau</small></span></a>
    <a class="bar-tel-link" href="{tel}" aria-label="Appeler {s['name']} au {s['phone']}">{ic("phone")}<span class="bar-tel-num">{s['phone']}</span></a>
  </div>
</header>

<main id="top">
<section class="hero">
  <div class="hero-bg"><img src="{p['img']}" alt="{p['alt']}" width="1024" height="1024" fetchpriority="high" decoding="async" style="--pos:{p['pos']}"></div>
  <div class="hero-in">
    <div class="hero-copy">
      {h1}
      <a class="google-badge fade" style="--d:1" href="https://www.google.com/search?q=Tonio+Rénov+Boucau+avis" target="_blank" rel="noopener">
        <span class="g-logo" aria-hidden="true"><b style="color:#4285F4">G</b><b style="color:#DB4437">o</b><b style="color:#F4B400">o</b><b style="color:#4285F4">g</b><b style="color:#0F9D58">l</b><b style="color:#DB4437">e</b></span>
        {stars()}<span><b>5/5</b> · <b>{p.get('avis', '23')} avis</b></span>
      </a>
      <div class="hero-cta fade" style="--d:2">
        <a class="btn btn-primary btn-stack" href="{tel}"><span class="sh-spark" aria-hidden="true"><span class="sh-slide"><span class="sh-spin"></span></span></span><span class="sh-back" aria-hidden="true"></span>{ic("phone","btn-ph")}<span class="btn-txt"><b>{s['phone']}</b><small>{p['ghost']}</small></span></a>
      </div>
      <p class="hero-proof fade" style="--d:3">{proof}</p>
    </div>
    {devis_haut}
  </div>
</section>

{band_html}

<section class="sec sec-dark has-bg">
  {bgimg(M["bgm"])}
  <div class="wrap">
    <div class="sec-head center">{method_h2}<p class="lead reveal on-dark" style="--d:1"><strong>Pas de devis par mail. Pas de commercial envoyé par un autre. Pas de prix balancé au téléphone.</strong><br>Tonio décroche, passe chez vous le soir même ou le lendemain, {method_tagline(p['path'])}, puis chiffre devant vous, sur place.</p></div>
    <ol class="steps">{steps}</ol>
  </div>
</section>

<section class="sec sec-light">
  <div class="wrap">
    <div class="sec-head center">{h2("Nos derniers chantiers sur la Côte Basque")}</div>
    <ul class="gal-grid reveal" style="--d:1"{' data-carousel="all"' if p.get('marquee') else ''}>
{''.join(f'      <li><img src="/{src}" alt="{alt}" loading="lazy" decoding="async"><figcaption>{alt}</figcaption></li>' + chr(10) for src, alt in gallery_photos(p['path']))}    </ul>
  </div>
</section>

<section class="sec sec-light" id="avis" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head center">{rev_h2}<p class="rev-sum reveal">{stars()}<span><b>5/5</b> · {p.get('rev_sum', 'avis vérifiés de clients de la Côte Basque et des Landes')}</span></p></div>
    <div class="rev-grid"{' data-carousel="all"' if p.get('marquee') else ''}>{''.join(revs)}</div>
  </div>
</section>

<section class="sec sec-light" id="zone" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head center">{zone_h2}<p class="lead reveal" style="--d:1"><strong>Artisan local</strong> — pas d'intermédiaire, pas de sous-traitance. On connaît les toitures et les façades du secteur, exposées au vent et aux embruns.</p></div>
    <ul class="chips reveal" style="--d:2">{zones}</ul>
  </div>
</section>
{kw_sections(p)}
<section class="sec sec-light" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head center">{faq_h2}<p class="lead reveal" style="--d:1">Une autre question ? Appelez-nous au <a href="{tel}"><strong>{s['phone']}</strong></a>.</p></div>
    <div class="faq-list reveal" style="--d:1">{faq}</div>
  </div>
</section>

<section class="sec cta has-bg">
  {bgimg(M["bgc"])}
  <div class="wrap">
    {cta_h2}
    <p class="reveal" style="--d:1">{p['cta']['p']}</p>
    {rarete}
    <div class="btns reveal" style="--d:2">
      <a class="btn btn-primary" href="#devis-bas"><span>Faire venir Tonio chez moi</span>{ic("arrow","arr")}</a>
      <a class="btn-tel on-dark" href="{tel}">{ic("phone")}<span>ou appeler <b>{s['phone']}</b></span></a>
    </div>
    <p class="ps reveal on-dark" style="--d:3"><strong>PS —</strong> Votre {ps_subject(p['path'])} ne va pas s'arranger tout seul. Un diagnostic gratuit maintenant = zéro euro pour savoir. Attendre, c'est {ps_cost(p['path'])}.</p>
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
        open(target, 'w', encoding='utf-8').write(typo_fr(render(p)))
        print('écrit', p['out'], f'{os.path.getsize(target)//1024} Ko')
    fav = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#fff"/>'
           '<g transform="translate(4 15) scale(.0968)"><g transform="translate(-395 -438)">'
           '<polygon fill="#152c48" points="704,442 1008,695 934,695 704,505 476,695 400,695 505,607 505,514 562,514 562,558"/>'
           '<polygon fill="#8c1c2c" points="704,532 901,695 869,695 704,562 539,695 507,695"/></g></g></svg>')
    open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8').write(fav)
