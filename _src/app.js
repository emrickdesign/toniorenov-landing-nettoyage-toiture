/* Comportement des landings : barre fixe au scroll, révélations, suivi GTM, formulaire à choix.
   Événements GTM conservés à l'identique : click_call et leads_entrer. */
(function () {
  var doc = document;
  window.dataLayer = window.dataLayer || [];

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

  /* Bouton d'appel flottant : présent partout, sauf quand le formulaire, l'appel final ou le pied de page sont à l'écran */
  var hideZones = [].slice.call(doc.querySelectorAll('.devis-shell, .cta, footer'));
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

  function submit() {
    answers.nom = val('f-nom');
    answers.tel = val('f-tel');
    answers.ville = val('f-ville');
    show(5);
    /* -> brancher ici l'envoi réel (fetch vers un endpoint / CRM) avec `answers` */
    console.log('Demande de devis', answers);
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
