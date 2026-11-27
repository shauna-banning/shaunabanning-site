/* Lead-capture slide-in for area + MacDill pages.
   Usage: <script src="../assets/js/slidein.js" data-title="Get the Brandon Update" data-sub="..." defer></script>
   Reuses the page's own Flodesk form (first #fd-form-<id>), so sign-ups land in the right segment
   and trigger the welcome workflow. Shows once: after ~60% scroll, or on exit intent (desktop).
   Closed -> hidden 7 days. Signed up anywhere on the page -> never shown again. */
(function () {
  var me = document.currentScript;
  var KEY_CLOSED = 'sb_slide_closed', KEY_DONE = 'sb_signed_up', WEEK = 7 * 864e5;
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  // Anyone who submits any form on the site counts as signed up.
  document.addEventListener('submit', function () { set(KEY_DONE, '1'); }, true);

  var preview = /[?&]slidein=1/.test(location.search); // add ?slidein=1 to any page to preview it
  if (!preview) {
    if (get(KEY_DONE)) return;
    if (Date.now() - (+get(KEY_CLOSED) || 0) < WEEK) return;
  }

  // Optional: data-form="<flodesk id>" picks a specific form (e.g. a guide form inside a modal),
  // and data-watch="#section" is the on-page block that should suppress the pop-up while visible.
  var pick = me.getAttribute('data-form');
  var host = pick ? document.getElementById('fd-form-' + pick)
    : (document.querySelector('#monthly [id^="fd-form-"]') || document.querySelector('[id^="fd-form-"]:not(.dl-form)'));
  if (!host || !window.fd) return;
  var formId = host.id.replace('fd-form-', '');
  var watchEl = me.getAttribute('data-watch') ? document.querySelector(me.getAttribute('data-watch')) : null;
  var title = me.getAttribute('data-title') || 'Get the Monthly Update';
  var eyebrow = me.getAttribute('data-eyebrow') || 'Free · Monthly';
  var sub = me.getAttribute('data-sub') || 'Buying or selling here? One email a month: what sold, what it sold for and how fast homes are moving.';

  // Don't pop up while the page's own sign-up form is on screen.
  var formInView = false;
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { formInView = es[0].isIntersecting; }, { threshold: 0.3 })
      .observe(watchEl || host.closest('section') || host);
  }

  var shown = false, el;
  function show() {
    if (shown || (formInView && !preview)) return;
    shown = true;
    el = document.createElement('aside');
    el.className = 'slidein';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-label', title);
    el.innerHTML =
      '<button class="slidein-x" type="button" aria-label="Close">&times;</button>' +
      '<span class="eyebrow"></span>' +
      '<h3></h3><p class="slidein-sub"></p>' +
      '<div class="form slidein-form"><div id="fd-slide-' + formId + '"></div>' +
      '<small>No spam, unsubscribe anytime. Shauna Banning, Coldwell Banker Realty.</small></div>';
    el.querySelector('.eyebrow').textContent = eyebrow;
    el.querySelector('h3').textContent = title;
    el.querySelector('.slidein-sub').textContent = sub;
    document.body.appendChild(el);
    window.fd('form', { formId: formId, containerEl: '#fd-slide-' + formId });
    requestAnimationFrame(function () { el.classList.add('open'); });
    el.querySelector('.slidein-x').addEventListener('click', close);
    if (window.gtag) gtag('event', 'slidein_shown', { page_path: location.pathname });
  }
  function close() {
    set(KEY_CLOSED, String(Date.now()));
    el.classList.remove('open');
    setTimeout(function () { el.remove(); }, 400);
    if (window.gtag) gtag('event', 'slidein_closed', { page_path: location.pathname });
  }

  function onScroll() {
    var h = document.documentElement;
    if ((h.scrollTop + innerHeight) / h.scrollHeight >= 0.6) { removeEventListener('scroll', onScroll); show(); }
  }
  addEventListener('scroll', onScroll, { passive: true });
  if (matchMedia('(pointer:fine)').matches) {
    document.addEventListener('mouseout', function (e) {
      if (!e.relatedTarget && e.clientY <= 0 && (Date.now() - start) > 8000) show();
    });
  }
  var start = Date.now();
  if (preview) setTimeout(show, 1500);
})();
