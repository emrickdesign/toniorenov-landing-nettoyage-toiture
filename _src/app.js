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
    url: 'https://alpzagoprkpzirgtrdup.supabase.co/rest/v1/form_submissions',
    key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFscHphZ29wcmtwemlyZ3RyZHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3OTg2MDEsImV4cCI6MjA5MjM3NDYwMX0.R7R6esDFce1W4k_wK-aBtAG20oUtK2SmSNCVKENS91g',
    client: 'db6e370a-71b8-454b-bf42-54e8fdc0de43' /* Tonio Rénov' */
  };

  function param(n) { try { return new URLSearchParams(location.search).get(n) || null; } catch (e) { return null; } }

  function envoyer(reponses, pos) {
    /* Ce que Tonio doit savoir avant de rappeler : type de toiture, surface, page et formulaire d'origine. */
    var details = [reponses.toiture, reponses.surface].filter(Boolean).join(' · ') || null;
    /* Chaque prestation a son sous-domaine (entretien-toiture, ravalement-facade…) :
       c'est lui qui identifie la page, le chemin valant « / » partout. */
    var hote = location.hostname.split('.')[0];
    var page = /toniorenov\.fr$/.test(location.hostname)
      ? hote
      : (location.pathname === '/' ? 'nettoyage-toiture' : location.pathname.replace(/^\/|\/$/g, ''));
    var corps = {
      client_id: LEAD.client,
      prenom: reponses.nom || null,
      telephone: reponses.tel || null,
      ville: reponses.ville || null,
      domaine: reponses.probleme || null,
      details: details,
      source: 'landing-ads ' + page + ' (formulaire ' + pos + ')',
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
    var TOTAL = 4;
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
      actions.style.display = n === 5 ? 'none' : 'flex';
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
      show(5);
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
        lead_ville: reponses.ville,
        lead_formulaire: pos
      });
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
