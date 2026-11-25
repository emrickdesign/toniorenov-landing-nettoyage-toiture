/* Comportement des landings : barre fixe au scroll, révélations, suivi GTM, formulaire à choix.
   Événements GTM conservés à l'identique : click_call et leads_entrer. */
(function () {
  var doc = document;
  window.dataLayer = window.dataLayer || [];
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Barre du haut : visible dès l'arrivée ; on ajoute juste une ombre quand on a scrollé */
  var ticking = false;
  window.addEventListener('scroll', function () {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(function () {
        doc.body.classList.toggle('scrolled', (window.scrollY || window.pageYOffset) > 8);
        tracerEtapes();
        placerFab();
        ticking = false;
      });
    }
  }, { passive: true });

  /* Bouton d'appel flottant : présent tout le long, sauf quand les boutons du hero, un
     formulaire, l'appel final ou le pied de page sont à l'écran (il ne doit jamais les
     recouvrir). Calcul au scroll plutôt qu'en IntersectionObserver : un saut d'ancre ne
     franchit aucun seuil, et le bouton restait alors posé sur « Continuer ». */
  var hideZones = [].slice.call(doc.querySelectorAll('.hero-cta, .devis-shell, .cta, footer'));
  function placerFab() {
    var vh = window.innerHeight || 800;
    var gene = hideZones.some(function (z) {
      var r = z.getBoundingClientRect();
      var visible = Math.min(r.bottom, vh) - Math.max(r.top, 0);
      return visible >= Math.min(140, r.height * 0.9);
    });
    doc.body.classList.toggle('fab-off', gene);
  }
  window.addEventListener('resize', placerFab, { passive: true });
  window.addEventListener('load', placerFab);
  placerFab();

  /* Trait de progression de la section « Comment ça marche » : purement décoratif.
     Aucun contenu n'est masqué en attente — voir le commentaire dans style.css. */
  var etapes = [].slice.call(doc.querySelectorAll('.steps'));
  function tracerEtapes() {
    etapes = etapes.filter(function (el) {
      if (el.getBoundingClientRect().top < (window.innerHeight || 800) * 0.92) { el.classList.add('in'); return false; }
      return true;
    });
  }
  window.addEventListener('resize', tracerEtapes, { passive: true });
  window.addEventListener('load', tracerEtapes);
  tracerEtapes();

  /* Suivi GTM : clic sur un numéro d'appel */
  [].slice.call(doc.querySelectorAll('a[href^="tel:"]')).forEach(function (a) {
    a.addEventListener('click', function () {
      var zone = a.closest('.fab') ? 'bouton_flottant'
        : a.closest('.bar') ? 'barre_sticky'
        : a.closest('.hero') ? 'hero'
        : a.closest('.cta') ? 'cta_final'
        : a.closest('.done') ? 'devis_succes'
        : a.closest('footer') ? 'footer'
        : a.closest('.devis') ? 'devis'
        : 'autre';
      window.dataLayer.push({
        event: 'click_call',
        call_zone: zone,
        call_number: a.getAttribute('href').replace('tel:', '')
      });
      /* Backup de GTM : si le tag GTM ne fire pas (bloqueur, timing, bug), la conv remonte quand même. ONE_PER_CLICK dédoublonne côté Ads. */
      if (typeof gtag === 'function') {
        gtag('event', 'conversion', { 'send_to': 'AW-18220615555/6RlhCNez6vgcEIOPovBD' });
      }
    });
  });

  /* Comparaison avant / après (curseur accessible : c'est un vrai <input type=range>) */
  [].slice.call(doc.querySelectorAll('.ba[data-mode="slider"]')).forEach(function (ba) {
    var r = ba.querySelector('.ba-range');
    var touched = false;
    function set(v) { ba.style.setProperty('--pos', v + '%'); }
    r.addEventListener('input', function () { touched = true; set(r.value); });
    function hint() {
      var t0 = null, from = 96, to = 50, dur = 1200;
      function step(ts) {
        if (touched) return;
        if (!t0) t0 = ts;
        var p = Math.min(1, (ts - t0) / dur), e = 1 - Math.pow(1 - p, 3), v = from + (to - from) * e;
        r.value = v; set(v);
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }
    if (!reduce && 'IntersectionObserver' in window) {
      var o = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { o.disconnect(); hint(); } });
      }, { threshold: 0.6 });
      o.observe(ba);
    }
  });

  /* ---------------------------------------------------------------
     Formulaires de devis — il y en a deux par page (haut et bas).
     Chacun vit sa vie : ses réponses, son étape, son envoi.
     --------------------------------------------------------------- */

  /* Destination des demandes : espace client Potentieel (table form_submissions).
     Le lead apparaît dans la fiche du client, à côté des appels du numéro de suivi. */
  var LEAD = {
    url: 'https://ktzegmikprmltuelxsgi.supabase.co/rest/v1/form_submissions',
    key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt0emVnbWlrcHJtbHR1ZWx4c2dpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM3MjExMzEsImV4cCI6MjEwOTI5NzEzMX0.yg0-RZgekOcy8GNKpdg3OUpxp6vp5jZu2iIFJK21TAk',
    client: 'db6e370a-71b8-454b-bf42-54e8fdc0de43' /* Tonio Rénov' */
  };

  function param(n) { try { return new URLSearchParams(location.search).get(n) || null; } catch (e) { return null; } }

  function envoyer(reponses, pos, form) {
    /* Ce que Tonio doit savoir avant de rappeler : type de toiture, surface, délai, statut, page et formulaire d'origine. */
    if (!LEAD.client) return Promise.reject(new Error('Fiche CRM du client non branchée'));
    var details = [reponses.toiture, reponses.surface, reponses.delai, reponses.statut].filter(Boolean).join(' · ') || null;
    var page = location.pathname === '/' ? '' : location.pathname.replace(/\/$/, '');
    var corps = {
      client_id: LEAD.client,
      prenom: reponses.nom || null,
      telephone: reponses.tel || null,
      ville: reponses.ville || null,
      /* Sans question « besoin » (ex. nettoyage toiture), le métier vient de data-domaine du formulaire (19/11). */
      domaine: reponses.probleme || (form && form.getAttribute('data-domaine')) || (/peinture/.test(location.pathname) ? 'Peinture intérieure' : null),
      details: details,
      source: 'landing-ads' + page + ' (formulaire ' + pos + ')',
      campagne: param('utm_campaign'),
      publicite: param('utm_term') || param('utm_content'),
      gclid: param('gclid'),
      fields_filled: Object.keys(reponses).length
    };
    return fetch(LEAD.url, {
      method: 'POST',
      headers: { 'apikey': LEAD.key, 'Authorization': 'Bearer ' + LEAD.key, 'Content-Type': 'application/json' },
      body: JSON.stringify(corps)
    }).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); });
  }

  function initDevis(form) {
    var shell = form.closest('.devis-shell');
    var pos = form.getAttribute('data-pos') || 'haut';
    var steps = [].slice.call(form.querySelectorAll('.fstep'));
    var bars = [].slice.call(shell.querySelectorAll('.progress i'));
    var next = form.querySelector('.btn-next');
    var back = form.querySelector('.fback'); /* absent depuis le 24/11 : formulaire en un seul écran */
    var actions = form.querySelector('.factions');
    var lbl = next.querySelector('.lbl');
    var TOTAL = steps.length - 1; /* étapes avec réponse (coordonnées incluses) ; l'étape TOTAL + 1 = demande envoyée */
    var cur = 1;
    var reponses = {};
    var envoye = false;

    function champ(n) { return form.querySelector('[data-champ="' + n + '"]'); }
    function val(n) { var e = champ(n); return e ? (e.value || '').trim() : ''; }
    function fieldOf(n) {
      var g = form.querySelector('.fstep[data-step="' + n + '"] [data-field]');
      return g ? g.getAttribute('data-field') : null;
    }
    function validate() {
      if (cur === TOTAL) {
        next.disabled = !(val('nom').length > 1 && val('tel').replace(/\D/g, '').length >= 9);
        lbl.textContent = 'Envoyer';
      } else if (cur < TOTAL) {
        next.disabled = !reponses[fieldOf(cur)];
        lbl.textContent = 'Continuer';
      }
    }
    function show(n) {
      cur = n;
      steps.forEach(function (st) { st.classList.toggle('active', Number(st.getAttribute('data-step')) === n); });
      bars.forEach(function (b, i) { b.classList.toggle('on', i < Math.min(n, TOTAL)); });
      if (back) back.disabled = n === 1;
      actions.style.display = n === TOTAL + 1 ? 'none' : 'flex';
      validate();
      var h = form.querySelector('.fstep.active [data-focus]');
      if (h && n > 1) { try { h.focus({ preventScroll: true }); } catch (e) {} }
    }

    [].slice.call(form.querySelectorAll('.opt')).forEach(function (opt) {
      opt.addEventListener('click', function () {
        var group = opt.closest('[data-field]');
        [].slice.call(group.querySelectorAll('.opt')).forEach(function (o) {
          o.classList.remove('on'); o.setAttribute('aria-pressed', 'false');
        });
        opt.classList.add('on');
        opt.setAttribute('aria-pressed', 'true');
        reponses[group.getAttribute('data-field')] = opt.getAttribute('data-value');
        validate();
        setTimeout(function () { if (cur < TOTAL) show(cur + 1); }, 320);
      });
    });
    ['nom', 'tel', 'ville'].forEach(function (n) {
      var e = champ(n); if (e) e.addEventListener('input', validate);
    });

    function submit() {
      if (envoye) return;
      envoye = true;
      reponses.nom = val('nom');
      reponses.tel = val('tel');
      reponses.ville = val('ville');
      show(TOTAL + 1);
      /* Si l'envoi échoue (réseau coupé), on réessaie une fois, puis on invite à appeler. */
      envoyer(reponses, pos, form).catch(function () {
        return new Promise(function (ok) { setTimeout(ok, 1500); }).then(function () { return envoyer(reponses, pos, form); });
      }).catch(function (e) {
        console.error('Envoi de la demande impossible', e);
        var d = form.querySelector('.done');
        var lien = doc.querySelector('a[href^="tel:"]'); /* le numéro affiché sur la page */
        if (d && lien && !d.querySelector('.done-fallback')) {
          var pEl = doc.createElement('p');
          pEl.className = 'done-fallback';
          pEl.innerHTML = "Votre demande n'a pas pu être transmise. Appelez-nous directement au "
            + '<a href="' + lien.getAttribute('href') + '">' + lien.textContent.trim() + '</a>.';
          d.appendChild(pEl);
        }
      });
      window.dataLayer.push({
        event: 'leads_entrer',
        lead_probleme: reponses.probleme,
        lead_toiture: reponses.toiture,
        lead_surface: reponses.surface,
        lead_delai: reponses.delai,
        lead_statut: reponses.statut,
        lead_ville: reponses.ville,
        lead_formulaire: pos
      });
      /* Backup de GTM : si le tag GTM ne fire pas (bloqueur, timing, bug), la conv remonte quand même. ONE_PER_CLICK dédoublonne côté Ads. */
      if (typeof gtag === 'function') {
        gtag('event', 'conversion', { 'send_to': 'AW-18220615555/01TxCPPv6fgcEIOPovBD' });
      }
    }

    next.addEventListener('click', function () {
      if (next.disabled) return;
      if (cur === TOTAL) submit(); else if (cur < TOTAL) show(cur + 1);
    });
    if (back) back.addEventListener('click', function () { if (cur > 1) show(cur - 1); });
    form.addEventListener('submit', function (e) { e.preventDefault(); if (!next.disabled) next.click(); });
    show(1);
  }

  [].slice.call(doc.querySelectorAll('form.devis-form')).forEach(initDevis);
})();

/* ---------------------------------------------------------------------
   Suivi des visiteurs — ce que les gens font vraiment sur la page.
   Écrit dans tonio_page_events (CRM Potentieel OS). Un identifiant de
   session tient le temps d'un onglet. Aucune donnée personnelle n'est
   envoyée : pathname, référent, utm/gclid, et les actions sur la page.
   --------------------------------------------------------------------- */
(function () {
  var TRACK = {
    url: 'https://ktzegmikprmltuelxsgi.supabase.co/rest/v1/tonio_page_events',
    key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt0emVnbWlrcHJtbHR1ZWx4c2dpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM3MjExMzEsImV4cCI6MjEwOTI5NzEzMX0.yg0-RZgekOcy8GNKpdg3OUpxp6vp5jZu2iIFJK21TAk'
  };

  function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 10); }
  function param(n) { try { return new URLSearchParams(location.search).get(n) || null; } catch (e) { return null; } }

  /* Identifiant de session : un par onglet, perdu à la fermeture. Plus fidèle à "une visite". */
  var SID;
  try {
    SID = sessionStorage.getItem('tonio_sid');
    if (!SID) { SID = uid(); sessionStorage.setItem('tonio_sid', SID); }
  } catch (e) { SID = uid(); }

  var PAGE = location.pathname;
  var REF = document.referrer || '';
  var UA = navigator.userAgent || '';
  var START = Date.now();
  var MAX_SCROLL = 0;
  var SCROLL_SENT = {};
  var ENGAGED_SENT = {};
  var FORM_IN_VIEW_SENT = false;
  var FORM_START_SENT = false;
  var LAST_STEP = {};
  var EXIT_SENT = false;

  var UTM = {
    gclid: param('gclid'),
    utm_source: param('utm_source'),
    utm_medium: param('utm_medium'),
    utm_campaign: param('utm_campaign'),
    utm_term: param('utm_term'),
    utm_content: param('utm_content')
  };

  function send(type, meta, beacon) {
    var corps = JSON.stringify({
      event_type: type,
      page: PAGE,
      session_id: SID,
      user_agent: UA,
      referrer: REF,
      meta: Object.assign({}, UTM, meta || {})
    });
    try {
      /* 19/11 : sendBeacon avec un corps JSON est refusé par le navigateur (envoi cross-origin non simple) :
         page_exit n'arrivait jamais. fetch keepalive survit à la fermeture de l'onglet et garde les en-têtes. */
      {
        fetch(TRACK.url, {
          method: 'POST',
          keepalive: !!beacon,
          headers: {
            'apikey': TRACK.key,
            'Authorization': 'Bearer ' + TRACK.key,
            'Content-Type': 'application/json'
          },
          body: corps
        }).catch(function () {});
      }
    } catch (e) {}
  }

  /* 1. Page vue */
  send('pageview', { title: document.title });

  /* 2. Scroll : 10 paliers de 10% pour voir précisément jusqu'où on descend */
  var SEUILS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
  function pctScroll() {
    var h = document.documentElement;
    var sc = h.scrollTop || document.body.scrollTop;
    var dh = Math.max(h.scrollHeight, document.body.scrollHeight) - h.clientHeight;
    return dh > 0 ? Math.min(100, Math.round(sc / dh * 100)) : 0;
  }
  function checkScroll() {
    var p = pctScroll();
    if (p > MAX_SCROLL) MAX_SCROLL = p;
    for (var i = 0; i < SEUILS.length; i++) {
      var s = SEUILS[i];
      if (p >= s && !SCROLL_SENT[s]) {
        SCROLL_SENT[s] = true;
        send('scroll_' + s);
      }
    }
  }
  var scrollRaf = false;
  window.addEventListener('scroll', function () {
    if (scrollRaf) return;
    scrollRaf = true;
    requestAnimationFrame(function () { checkScroll(); scrollRaf = false; });
  }, { passive: true });

  /* 3. Temps passé : jalons visiteur engagé */
  [10, 15, 30, 60, 120, 180, 300].forEach(function (s) {
    setTimeout(function () {
      if (!document.hidden && !ENGAGED_SENT[s]) {
        ENGAGED_SENT[s] = true;
        send('engaged_' + s + 's');
      }
    }, s * 1000);
  });

  /* 4 & 5. Clics sur téléphone et sur bouton "Devis gratuit" */
  document.addEventListener('click', function (ev) {
    var t = ev.target;
    if (!t || !t.closest) return;
    var a = t.closest('a[href^="tel:"]');
    if (a) {
      var zone = a.closest('.fab') ? 'bouton_flottant'
        : a.closest('.bar') ? 'barre_sticky'
        : a.closest('.hero') ? 'hero'
        : a.closest('.cta') ? 'cta_final'
        : a.closest('.done') ? 'devis_succes'
        : a.closest('footer') ? 'footer'
        : a.closest('.devis') ? 'devis'
        : 'autre';
      send('click_call', { zone: zone, numero: (a.getAttribute('href') || '').replace('tel:', '') });
      return;
    }
    var btn = t.closest('a[href="#devis"], a[href="#devis-bas"]');
    if (btn) {
      var z = btn.closest('.bar') ? 'barre_sticky'
        : btn.closest('.hero') ? 'hero'
        : btn.closest('.cta') ? 'cta_final'
        : btn.closest('footer') ? 'footer'
        : 'autre';
      send('click_cta_devis', { zone: z, href: btn.getAttribute('href') });
    }
  }, true);

  /* 6. Formulaire visible dans l'écran */
  if ('IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting || FORM_IN_VIEW_SENT) return;
        FORM_IN_VIEW_SENT = true;
        var f = e.target.querySelector('form.devis-form');
        var pos = f ? (f.getAttribute('data-pos') || 'haut') : 'haut';
        send('form_in_view', { pos: pos });
      });
    }, { threshold: 0.4 });
    [].slice.call(document.querySelectorAll('.devis-shell')).forEach(function (sh) { obs.observe(sh); });
  }

  /* 7. Interactions dans le formulaire : premier clic (= démarrage) + chaque étape */
  [].slice.call(document.querySelectorAll('form.devis-form')).forEach(function (form) {
    var pos = form.getAttribute('data-pos') || 'haut';

    form.addEventListener('click', function (ev) {
      var opt = ev.target && ev.target.closest && ev.target.closest('.opt');
      if (opt && !FORM_START_SENT) {
        FORM_START_SENT = true;
        send('form_start', { pos: pos, premier_choix: opt.getAttribute('data-value') });
      }
    });
    /* 24/11 : formulaire en un seul écran, le démarrage = premier champ touché (prénom ou téléphone). */
    form.addEventListener('focusin', function (ev) {
      var c = ev.target && ev.target.getAttribute && ev.target.getAttribute('data-champ');
      if (c && !FORM_START_SENT) {
        FORM_START_SENT = true;
        send('form_start', { pos: pos, premier_champ: c });
      }
    });

    function etapeActuelle() {
      var a = form.querySelector('.fstep.active');
      return a ? parseInt(a.getAttribute('data-step'), 10) : null;
    }
    /* On n'envoie form_step_N que pour N >= 2 : l'étape 1 est active au chargement,
       elle n'indique rien d'intéressant. Chaque étape suivante = une case de plus remplie. */
    var mo = new MutationObserver(function () {
      var n = etapeActuelle();
      if (n && n >= 2 && LAST_STEP[pos] !== n) {
        LAST_STEP[pos] = n;
        send('form_step_' + n, { pos: pos });
      }
    });
    mo.observe(form, { attributes: true, subtree: true, attributeFilter: ['class'] });
    LAST_STEP[pos] = etapeActuelle();
  });

  /* 8. Succès du formulaire : on se branche sur dataLayer.push (déjà émis par le submit) */
  (function () {
    var dl = window.dataLayer;
    if (!Array.isArray(dl)) return;
    var pushOrigine = dl.push;
    dl.push = function () {
      try {
        for (var i = 0; i < arguments.length; i++) {
          var e = arguments[i];
          if (e && e.event === 'leads_entrer') {
            send('form_submit_success', {
              pos: e.lead_formulaire,
              probleme: e.lead_probleme,
              toiture: e.lead_toiture,
              surface: e.lead_surface,
              delai: e.lead_delai,
              statut: e.lead_statut,
              ville: e.lead_ville
            });
          }
        }
      } catch (ex) {}
      return pushOrigine.apply(this, arguments);
    };
  })();

  /* 9. Sortie de page : temps total + scroll maximum atteint, envoyé via sendBeacon */
  function partir(cause) {
    if (EXIT_SENT) return;
    EXIT_SENT = true;
    send('page_exit', {
      cause: cause || 'unload',
      time_on_page_s: Math.round((Date.now() - START) / 1000),
      max_scroll: MAX_SCROLL,
      form_in_view: FORM_IN_VIEW_SENT,
      form_start: FORM_START_SENT,
      derniere_etape: LAST_STEP
    }, true);
  }
  document.addEventListener('visibilitychange', function () { if (document.hidden) partir('hidden'); });
  window.addEventListener('pagehide', function () { partir('pagehide'); });
  window.addEventListener('beforeunload', function () { partir('beforeunload'); });
})();

/* ---------- Carrousels : glisser au doigt, points, défilement auto (pause dès que le visiteur touche) ---------- */
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  [].forEach.call(document.querySelectorAll('[data-carousel]'), function (c) {
    var items = [].slice.call(c.children);
    var dots = document.createElement('div');
    dots.className = 'carousel-dots';
    c.parentNode.insertBefore(dots, c.nextSibling);
    var stops = [], pauseUntil = 0, visible = false, raf = 0;
    /* Flèches (ordinateur) : le carrousel est enveloppé pour les poser sur ses bords */
    var wrap = document.createElement('div'); wrap.className = 'car-wrap';
    c.parentNode.insertBefore(wrap, c); wrap.appendChild(c);
    var fl = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>';
    var prev = document.createElement('button'), next = document.createElement('button');
    prev.type = next.type = 'button'; prev.className = 'car-btn car-prev'; next.className = 'car-btn car-next';
    prev.setAttribute('aria-label', 'Précédent'); next.setAttribute('aria-label', 'Suivant');
    prev.innerHTML = next.innerHTML = fl;
    wrap.appendChild(prev); wrap.appendChild(next);
    prev.addEventListener('click', function () { pause(); go(Math.max(0, current() - 1)); });
    next.addEventListener('click', function () { pause(); go(Math.min(stops.length - 1, current() + 1)); });

    function pos(i) { return items[i].offsetLeft - items[0].offsetLeft; }
    function layout() {
      var scrollable = c.scrollWidth > c.clientWidth + 4;
      dots.hidden = !scrollable;
      /* 24/11/2026 : pas de flèches quand toutes les cartes tiennent à l'écran */
      wrap.classList.toggle('car-fixe', !scrollable);
      prev.hidden = next.hidden = !scrollable;
      if (!scrollable) { stops = []; dots.innerHTML = ''; prev.disabled = next.disabled = true; return; }
      var max = c.scrollWidth - c.clientWidth;
      stops = [];
      for (var i = 0; i < items.length; i++) { var p = Math.min(pos(i), max); if (!stops.length || p - stops[stops.length - 1] > 4) stops.push(p); }
      dots.innerHTML = '';
      stops.forEach(function (p, i) {
        var b = document.createElement('button');
        b.type = 'button';
        b.setAttribute('aria-label', 'Aller à l’élément ' + (i + 1));
        b.addEventListener('click', function () { pause(); go(i); });
        dots.appendChild(b);
      });
      mark();
    }
    function current() {
      var l = c.scrollLeft, best = 0, bd = Infinity;
      stops.forEach(function (p, i) { var d = Math.abs(p - l); if (d < bd) { bd = d; best = i; } });
      return best;
    }
    function mark() {
      var k = current();
      [].forEach.call(dots.children, function (b, i) { b.classList.toggle('on', i === k); });
      prev.disabled = !stops.length || k === 0; next.disabled = !stops.length || k === stops.length - 1;
    }
    function go(i) { c.scrollTo({ left: stops[i] || 0, behavior: reduce ? 'auto' : 'smooth' }); }
    function pause() { pauseUntil = Date.now() + 12000; }

    c.addEventListener('scroll', function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(mark); }, { passive: true });
    ['pointerdown', 'touchstart', 'wheel', 'mouseenter', 'focusin'].forEach(function (ev) { c.addEventListener(ev, pause, { passive: true }); });
    window.addEventListener('resize', function () { clearTimeout(c._t); c._t = setTimeout(layout, 150); });
    window.addEventListener('load', layout);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }, { threshold: 0.5 }).observe(c);
    }
    layout();
    if (!reduce) {
      setInterval(function () {
        if (!visible || !stops.length || Date.now() < pauseUntil || document.hidden) return;
        var k = current();
        go(k + 1 < stops.length ? k + 1 : 0);
      }, 4500);
    }
  });
})();

/* Anneau 3D de photos (repris de 2rprenov.fr) : rotation continue (un tour en 40 s), glissement
   au doigt ou à la souris qui s'ajoute à la rotation, pause hors écran et si l'animation est réduite. */
(function () {
  var rings = document.querySelectorAll('.ring3d');
  if (!rings.length) return;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function echelle(l, h) {
    if (l >= 1200) return 1;
    if (l >= 810) return Math.min(0.92, l / 1280, h / 1100);
    return Math.max(0.34, Math.min(0.66, l / 1000, (h - 420) / 650));
  }
  var e = 1, largeur = window.innerWidth;
  // Anneau dans le hero : l'échelle suit la largeur de son bloc (pleine largeur sur mobile, colonne sur ordinateur).
  function echelleHero(el) { return window.innerWidth >= 1060 ? Math.max(0.5, Math.min(0.78, el.clientWidth / 1700)) : Math.max(0.3, Math.min(0.46, el.clientWidth / 1000)); }
  function poserEchelle() {
    e = echelle(window.innerWidth, window.innerHeight);
    document.querySelectorAll('.ring-sec').forEach(function (s) { s.style.setProperty('--e', e); });
    document.querySelectorAll('.ring-hero').forEach(function (s) { var eh = echelleHero(s); s.style.setProperty('--e', eh); s._e = eh; });
  }
  poserEchelle();
  // Seule la largeur compte : la barre d'adresse iOS qui se replie change la hauteur en plein défilement.
  window.addEventListener('resize', function () { if (window.innerWidth === largeur) return; largeur = window.innerWidth; poserEchelle(); });
  rings.forEach(function (ring) {
    var rot = ring.querySelector('.ring3d-rot'), angle = 0, drag = 0, vu = true, prec = null, x0 = null, base = 0;
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { vu = es[0].isIntersecting; }, { threshold: 0, rootMargin: '400px 0px' }).observe(ring);
    function tour(t) {
      var dt = prec == null ? 0 : t - prec; prec = t;
      if (vu || x0 != null) {
        if (!reduce && !document.hidden && x0 == null) angle = (angle + dt / 40000 * 360) % 360;
        rot.style.transform = 'rotateY(' + (angle + drag) + 'deg)';
      }
      requestAnimationFrame(tour);
    }
    requestAnimationFrame(tour);
    var cible = null, xClic = 0;
    rot.addEventListener('pointerdown', function (ev) { cible = ev.target && ev.target.closest ? ev.target.closest('.ring3d-v') : null; xClic = ev.clientX; x0 = ev.clientX; base = drag; try { rot.setPointerCapture(ev.pointerId); } catch (_) {} });
    /* 24/11 : un clic (sans glisser) sur une photo de l'anneau l'ouvre en grand */
    rot.addEventListener('pointerup', function (ev) {
      if (cible && Math.abs(ev.clientX - xClic) < 6 && window.ouvrirPhoto) { var im = cible.querySelector('img'); if (im) window.ouvrirPhoto(im); }
      cible = null;
    });
    rot.addEventListener('pointermove', function (ev) { if (x0 != null) drag = base + (ev.clientX - x0) * 0.2 / (ring.parentNode._e || e); });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (n) { rot.addEventListener(n, function () { x0 = null; }); });
  });
})();

/* Fin d'offre : « jusqu'au 30 novembre » = dernier jour du mois en cours, recalculé à chaque visite. */
(function () {
  var els = document.querySelectorAll('[data-fin-mois]');
  if (!els.length) return;
  var d = new Date(), fin = new Date(d.getFullYear(), d.getMonth() + 1, 0);
  var mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
  els.forEach(function (el) { el.textContent = fin.getDate() + ' ' + mois[fin.getMonth()]; });
})();

/* H1 « modèle B » : la ligne la plus large du H1 prend exactement la largeur disponible
   (mobile : toute la largeur, comme le bouton d'appel ; ordinateur : 520 px max), sans dépasser un plafond. */
(function () {
  var h1s = document.querySelectorAll('h1.h1-b');
  if (!h1s.length) return;
  function caler() {
    var bureau = window.innerWidth >= 1060;
    h1s.forEach(function (h) {
      var hi = h.closest('.hero-in'); if (!hi) return;
      var cs = getComputedStyle(hi);
      var dispo = hi.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      if (bureau) dispo = Math.min(520, parseFloat(cs.gridTemplateColumns) || dispo);
      h.style.fontSize = '100px';
      var large = 0;
      h.querySelectorAll('.h1-l, .h1-sub, .h1-offre').forEach(function (l) { large = Math.max(large, l.getBoundingClientRect().width); });
      if (!large) { h.style.fontSize = ''; return; }
      h.style.fontSize = Math.min(bureau ? 46 : 34, Math.floor(100 * dispo / large * 10) / 10) + 'px';
      // L'offre courte (« 9 €/m² ») grossit jusqu'à la largeur du bloc, sans dépasser 2,2 fois les lignes 1-2.
      var prix = h.querySelector('.h1-offre mark'), offre = h.querySelector('.h1-offre');
      if (prix && offre) {
        prix.style.fontSize = '';
        var pw = prix.getBoundingClientRect().width, reste = offre.getBoundingClientRect().width - pw;
        var k = Math.min(2.2 / 1.4, (Math.min(dispo, large * parseFloat(h.style.fontSize) / 100) - reste) / pw * 0.98);
        if (k > 1.02) prix.style.fontSize = (1.4 * k).toFixed(2) + 'em';
      }
    });
  }
  caler();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(caler);
  var larg = window.innerWidth;
  window.addEventListener('resize', function () { if (window.innerWidth === larg) return; larg = window.innerWidth; caler(); });
})();

/* ---------- Avis : « Lire la suite » seulement quand le texte dépasse 6 lignes ---------- */
(function () {
  var revs = document.querySelectorAll('.rev');
  function caler() {
    revs.forEach(function (r) {
      var q = r.querySelector('.rev-q'), b = r.querySelector('.rev-more'); if (!q || !b) return;
      if (r.classList.contains('open')) return;
      b.hidden = q.scrollHeight <= q.clientHeight + 2;
    });
  }
  revs.forEach(function (r) {
    var b = r.querySelector('.rev-more'); if (!b) return;
    b.addEventListener('click', function () { var o = r.classList.toggle('open'); b.textContent = o ? 'Réduire' : 'Lire la suite'; });
  });
  caler();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(caler);
  window.addEventListener('resize', function () { clearTimeout(caler._t); caler._t = setTimeout(caler, 200); });
})();

/* ---------- « Chercher ma ville » : accepte fautes de frappe, accents, tirets, espaces, majuscules ---------- */
(function () {
  var input = document.getElementById('ville-q'); if (!input) return;
  var res = document.querySelector('.ville-res'), defile = document.querySelector('.ville-defile');
  var PRENOM = input.form && input.form.getAttribute('data-prenom') || 'l’artisan';
  var chips = [].slice.call(document.querySelectorAll('.ville-defile li[data-ville]'));
  var villes = []; chips.forEach(function (c) { var v = c.getAttribute('data-ville'); if (villes.indexOf(v) < 0) villes.push(v); });
  function norm(s) {
    return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/\bste?\b\.?/g, function (m) { return m.indexOf('e') > 0 ? 'sainte' : 'saint'; })
      .replace(/[^a-z]/g, '');
  }
  function lev(a, b) {
    var m = a.length, n = b.length, d = [], i, k;
    for (i = 0; i <= m; i++) d[i] = [i];
    for (k = 0; k <= n; k++) d[0][k] = k;
    for (i = 1; i <= m; i++) for (k = 1; k <= n; k++)
      d[i][k] = Math.min(d[i - 1][k] + 1, d[i][k - 1] + 1, d[i - 1][k - 1] + (a[i - 1] === b[k - 1] ? 0 : 1));
    return d[m][n];
  }
  var idx = villes.map(function (v) { return { v: v, n: norm(v), court: norm(v.split(/[-\s]sur[-\s]|-/)[0]) }; });
  function chercher(q) {
    var n = norm(q); if (n.length < 3) return null;
    var best = null, bd = Infinity;
    idx.forEach(function (o) {
      var d;
      if (o.n === n || o.court === n) d = 0;
      else if (o.n.indexOf(n) === 0) d = 0.5;
      else if (n.length >= 4 && o.n.indexOf(n) > 0) d = 1;
      else {
        var tol = n.length <= 5 ? 1 : n.length <= 9 ? 2 : 3;
        d = Math.min(lev(n, o.n), lev(n, o.court), n.length >= 5 ? lev(n, o.n.slice(0, n.length)) + 0.5 : 99);
        if (d > tol) d = Infinity; else d += 1;
      }
      if (d < bd) { bd = d; best = o.v; }
    });
    return best;
  }
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var tel = document.querySelector('a[href^="tel:"]');
  function maj() {
    var q = input.value.trim(), v = chercher(q);
    chips.forEach(function (c) { c.classList.toggle('hit', !!v && c.getAttribute('data-ville') === v); });
    if (defile) defile.classList.toggle('pause', !!v);
    if (!q || norm(q).length < 3) { res.hidden = true; return; }
    res.hidden = false;
    if (v) { res.className = 'ville-res ok'; res.innerHTML = '✓ Oui, ' + PRENOM + ' intervient à <b>' + esc(v) + '</b>.'; }
    else {
      res.className = 'ville-res';
      res.innerHTML = '<b>' + esc(q) + '</b> n’est pas dans la liste. Appelez ' + PRENOM + (tel ? ' au <a href="' + tel.getAttribute('href') + '">' + tel.textContent.replace(/[^\d ]/g, '').trim() + '</a>' : '') + ' : on vous dit si on peut venir.';
    }
  }
  input.addEventListener('input', maj);
  input.form && input.form.addEventListener('submit', function (e) { e.preventDefault(); maj(); input.blur(); });
})();

/* ---------- Carte des communes : « Voir plus » ouvre la fiche de la ville, un clic à côté la ferme ---------- */
(function () {
  var cartes = document.querySelectorAll('.carte'); if (!cartes.length) return;
  function fermer(c) {
    c.querySelectorAll('.carte-pop').forEach(function (p) { p.hidden = true; });
    c.querySelectorAll('.carte-lab').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
  }
  cartes.forEach(function (c) {
    c.querySelectorAll('.carte-lab').forEach(function (b) {
      b.setAttribute('aria-expanded', 'false');
      b.addEventListener('click', function (e) {
        e.stopPropagation();
        var p = document.getElementById(b.getAttribute('aria-controls')), ouvert = p && !p.hidden;
        fermer(c);
        if (p && !ouvert) { p.hidden = false; b.setAttribute('aria-expanded', 'true'); var x = p.querySelector('.pop-x'); if (x) x.focus({ preventScroll: true }); }
      });
    });
    c.querySelectorAll('.carte-pop').forEach(function (p) {
      p.addEventListener('click', function (e) { e.stopPropagation(); });
      var x = p.querySelector('.pop-x'); if (x) x.addEventListener('click', function () { fermer(c); });
    });
  });
  document.addEventListener('click', function () { cartes.forEach(fermer); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') cartes.forEach(fermer); });
})();

/* ---------- FAQ : « Voir les autres questions » (mobile) ---------- */
(function () {
  document.querySelectorAll('.faq-plus').forEach(function (b) {
    b.addEventListener('click', function () { var l = b.previousElementSibling; if (l) l.classList.add('tout'); b.remove(); });
  });
})();

/* Fenêtre d'agrandissement des photos (24/11, Emrick) : clic sur une photo de l'anneau ou de la galerie
   -> la photo s'ouvre au centre ; croix bien visible, clic à côté ou Échap pour fermer. */
(function () {
  var box = document.createElement('div');
  box.className = 'lb'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true'); box.setAttribute('aria-label', 'Photo agrandie'); box.hidden = true;
  box.innerHTML = '<button type="button" class="lb-x" aria-label="Fermer la photo"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button><figure class="lb-fig"><img class="lb-img" alt=""><figcaption class="lb-cap"></figcaption></figure>';
  document.body.appendChild(box);
  var img = box.querySelector('.lb-img'), cap = box.querySelector('.lb-cap'), x = box.querySelector('.lb-x'), avant = null;
  function fermer() { box.hidden = true; document.documentElement.classList.remove('lb-ouvert'); img.removeAttribute('src'); if (avant && avant.focus) try { avant.focus({ preventScroll: true }); } catch (e) {} }
  window.ouvrirPhoto = function (src) {
    avant = document.activeElement;
    img.src = src.getAttribute('data-full') || src.currentSrc || src.src;
    img.alt = src.alt || ''; cap.textContent = src.alt || '';
    box.hidden = false; document.documentElement.classList.add('lb-ouvert'); x.focus({ preventScroll: true });
  };
  box.addEventListener('click', function (ev) { if (ev.target !== img) fermer(); });
  document.addEventListener('keydown', function (ev) { if (!box.hidden && ev.key === 'Escape') fermer(); });
  [].forEach.call(document.querySelectorAll('.gal-grid img'), function (im) {
    im.style.cursor = 'zoom-in';
    im.addEventListener('click', function () { window.ouvrirPhoto(im); });
  });
})();

/* 25/11/2026 : le contour qui « respire » sur les champs s'arrête dès qu'on a cliqué une fois dedans. */
document.addEventListener('focusin', function (e) {
  if (e.target && e.target.matches && e.target.matches('.field input')) e.target.classList.add('vu');
});
