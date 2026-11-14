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
     Le lead apparaît dans la fiche du client, à côté des appels Twilio. */
  var LEAD = {
    url: 'https://ktzegmikprmltuelxsgi.supabase.co/rest/v1/form_submissions',
    key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt0emVnbWlrcHJtbHR1ZWx4c2dpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM3MjExMzEsImV4cCI6MjEwOTI5NzEzMX0.yg0-RZgekOcy8GNKpdg3OUpxp6vp5jZu2iIFJK21TAk',
    client: 'db6e370a-71b8-454b-bf42-54e8fdc0de43' /* Tonio Rénov' */
  };

  function param(n) { try { return new URLSearchParams(location.search).get(n) || null; } catch (e) { return null; } }

  function envoyer(reponses, pos) {
    /* Ce que Tonio doit savoir avant de rappeler : type de toiture, surface, délai, statut, page et formulaire d'origine. */
    var details = [reponses.toiture, reponses.surface, reponses.delai, reponses.statut].filter(Boolean).join(' · ') || null;
    var page = location.pathname === '/' ? '' : location.pathname.replace(/\/$/, '');
    var corps = {
      client_id: LEAD.client,
      prenom: reponses.nom || null,
      telephone: reponses.tel || null,
      ville: reponses.ville || null,
      domaine: reponses.probleme || null,
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
    var back = form.querySelector('.fback');
    var actions = form.querySelector('.factions');
    var lbl = next.querySelector('.lbl');
    var TOTAL = 6; /* étapes avec réponse ; l'étape TOTAL + 1 = demande envoyée */
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
        lbl.textContent = 'Envoyer ma demande';
      } else if (cur < TOTAL) {
        next.disabled = !reponses[fieldOf(cur)];
        lbl.textContent = 'Continuer';
      }
    }
    function show(n) {
      cur = n;
      steps.forEach(function (st) { st.classList.toggle('active', Number(st.getAttribute('data-step')) === n); });
      bars.forEach(function (b, i) { b.classList.toggle('on', i < Math.min(n, TOTAL)); });
      back.disabled = n === 1;
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
      envoyer(reponses, pos).catch(function () {
        return new Promise(function (ok) { setTimeout(ok, 1500); }).then(function () { return envoyer(reponses, pos); });
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
    back.addEventListener('click', function () { if (cur > 1) show(cur - 1); });
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
      if (beacon && navigator.sendBeacon) {
        /* sendBeacon ne porte pas d'en-tête ; Supabase accepte apikey en query string */
        navigator.sendBeacon(TRACK.url + '?apikey=' + encodeURIComponent(TRACK.key),
                             new Blob([corps], { type: 'application/json' }));
      } else {
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
