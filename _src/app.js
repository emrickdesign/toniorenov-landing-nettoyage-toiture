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
        ticking = false;
      });
    }
  }, { passive: true });

  /* Bouton d'appel flottant : présent tout le long, sauf quand les boutons du hero, le formulaire, l'appel final ou le pied de page sont déjà à l'écran (il ne doit jamais les recouvrir) */
  var hideZones = [].slice.call(doc.querySelectorAll('.hero-cta, .devis-shell, .cta, footer'));
  if ('IntersectionObserver' in window && hideZones.length) {
    var seen = {};
    var fio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { seen[hideZones.indexOf(e.target)] = e.isIntersecting; });
      var any = Object.keys(seen).some(function (k) { return seen[k]; });
      doc.body.classList.toggle('fab-off', any);
    }, { threshold: 0.15 });
    hideZones.forEach(function (z) { fio.observe(z); });
  }

  /* Révélations au scroll (IntersectionObserver) — le contenu reste visible sans JS */
  var targets = [].slice.call(doc.querySelectorAll('.reveal, .split, .steps'));
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.05 });
    targets.forEach(function (t) { io.observe(t); });
  } else {
    targets.forEach(function (t) { t.classList.add('in'); });
  }

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

  /* Formulaire multi-étapes à choix */
  var form = doc.getElementById('devisForm');
  if (!form) return;
  var steps = [].slice.call(form.querySelectorAll('.fstep'));
  var bars = [].slice.call(doc.querySelectorAll('#progress i'));
  var next = doc.getElementById('btnNext');
  var back = doc.getElementById('btnBack');
  var actions = doc.getElementById('fActions');
  var lbl = next.querySelector('.lbl');
  var TOTAL = 4;
  var cur = 1;
  var answers = {};

  function val(id) { return (doc.getElementById(id).value || '').trim(); }
  function fieldOf(n) {
    var g = form.querySelector('.fstep[data-step="' + n + '"] [data-field]');
    return g ? g.getAttribute('data-field') : null;
  }
  function validate() {
    if (cur === TOTAL) {
      next.disabled = !(val('f-nom').length > 1 && val('f-tel').replace(/\D/g, '').length >= 9);
      lbl.textContent = 'Envoyer ma demande';
    } else if (cur < TOTAL) {
      next.disabled = !answers[fieldOf(cur)];
      lbl.textContent = 'Continuer';
    }
  }
  function show(n) {
    cur = n;
    steps.forEach(function (s) { s.classList.toggle('active', Number(s.getAttribute('data-step')) === n); });
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
      [].slice.call(group.querySelectorAll('.opt')).forEach(function (o) { o.classList.remove('on'); o.setAttribute('aria-pressed', 'false'); });
      opt.classList.add('on');
      opt.setAttribute('aria-pressed', 'true');
      answers[group.getAttribute('data-field')] = opt.getAttribute('data-value');
      validate();
      setTimeout(function () { if (cur < TOTAL) show(cur + 1); }, 320);
    });
  });
  ['f-nom', 'f-tel', 'f-ville'].forEach(function (id) { doc.getElementById(id).addEventListener('input', validate); });

  /* Envoi de la demande dans l'espace client Potentieel (table form_submissions).
     Le lead apparaît dans la fiche du client, à côté des appels Twilio. */
  var LEAD = {
    url: 'https://alpzagoprkpzirgtrdup.supabase.co/rest/v1/form_submissions',
    key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFscHphZ29wcmtwemlyZ3RyZHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3OTg2MDEsImV4cCI6MjA5MjM3NDYwMX0.R7R6esDFce1W4k_wK-aBtAG20oUtK2SmSNCVKENS91g',
    client: 'db6e370a-71b8-454b-bf42-54e8fdc0de43' /* Tonio Rénov' */
  };

  function param(n) { try { return new URLSearchParams(location.search).get(n) || null; } catch (e) { return null; } }

  function envoyer() {
    /* Ce que Tonio doit savoir avant de rappeler : type de toiture, surface, page d'origine. */
    var details = [answers.toiture, answers.surface].filter(Boolean).join(' · ') || null;
    var corps = {
      client_id: LEAD.client,
      prenom: answers.nom || null,
      telephone: answers.tel || null,
      ville: answers.ville || null,
      domaine: answers.probleme || null,
      details: details,
      source: 'landing-ads' + (location.pathname === '/' ? '' : location.pathname),
      campagne: param('utm_campaign'),
      publicite: param('utm_term') || param('utm_content'),
      gclid: param('gclid'),
      fields_filled: Object.keys(answers).length
    };
    return fetch(LEAD.url, {
      method: 'POST',
      headers: { 'apikey': LEAD.key, 'Authorization': 'Bearer ' + LEAD.key, 'Content-Type': 'application/json' },
      body: JSON.stringify(corps)
    }).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
    });
  }

  function submit() {
    answers.nom = val('f-nom');
    answers.tel = val('f-tel');
    answers.ville = val('f-ville');
    show(5);
    /* Si l'envoi échoue (réseau coupé), on réessaie une fois, puis on invite à appeler. */
    envoyer().catch(function () {
      return new Promise(function (ok) { setTimeout(ok, 1500); }).then(envoyer);
    }).catch(function (e) {
      console.error('Envoi de la demande impossible', e);
      var d = doc.querySelector('.done');
      var lien = doc.querySelector('a[href^="tel:"]'); /* le numéro affiché sur la page */
      if (d && lien) {
        var p = doc.createElement('p');
        p.className = 'done-fallback';
        p.innerHTML = "Votre demande n'a pas pu être transmise. Appelez-nous directement au "
          + '<a href="' + lien.getAttribute('href') + '">' + lien.textContent.trim() + '</a>.';
        d.appendChild(p);
      }
    });
    window.dataLayer.push({
      event: 'leads_entrer',
      lead_probleme: answers.probleme,
      lead_toiture: answers.toiture,
      lead_surface: answers.surface,
      lead_ville: answers.ville
    });
  }
  next.addEventListener('click', function () {
    if (next.disabled) return;
    if (cur === TOTAL) submit(); else if (cur < TOTAL) show(cur + 1);
  });
  back.addEventListener('click', function () { if (cur > 1) show(cur - 1); });
  form.addEventListener('submit', function (e) { e.preventDefault(); if (!next.disabled) next.click(); });
  show(1);
})();
