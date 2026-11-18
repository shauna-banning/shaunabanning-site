/* Home value funnel. Step 1 (/home-value/) captures name, email, address.
   Step 2 (/home-value/thank-you/) adds details to the SAME lead row.
   Leads post to a Google Apps Script web app that writes to the
   "Home Value Leads" Google Sheet and emails Shauna instantly. */
(function () {
  var ENDPOINT = "https://script.google.com/macros/s/AKfycbyunFT8S23yZvRsy1BzDBOjYHq0gNh2grHWRURtz7ErTVhku-tPqhzcIcXnDpNu6RNV/exec";
  var KEY = "sb_hv_lead";

  function qs(name) { return new URLSearchParams(location.search).get(name) || ""; }
  function store(get, val) {
    try { if (get) return JSON.parse(sessionStorage.getItem(KEY) || "{}"); sessionStorage.setItem(KEY, JSON.stringify(val)); } catch (e) { return {}; }
  }
  function send(data) {
    if (ENDPOINT.indexOf("http") !== 0) { console.warn("Home value endpoint not set", data); return Promise.resolve(); }
    var body = new URLSearchParams(data);
    // keepalive lets the request finish even as we navigate to the next page
    return fetch(ENDPOINT, { method: "POST", mode: "no-cors", body: body, keepalive: true })
      .catch(function () { return new Promise(function (r) { setTimeout(r, 300); }); });
  }

  /* Video: autoplay muted, "Tap for sound" restarts with audio */
  document.querySelectorAll(".hv-video").forEach(function (box) {
    var v = box.querySelector("video"), btn = box.querySelector(".hv-sound");
    if (!v) return;
    function ready() { box.classList.add("has-video"); if (btn) btn.hidden = false; }
    v.addEventListener("loadeddata", ready);
    v.addEventListener("playing", ready);
    if (v.readyState >= 2) ready(); // video may load before this script runs
    v.addEventListener("error", function () { box.classList.remove("has-video"); }, true);
    if (btn) btn.addEventListener("click", function () {
      v.muted = false; v.currentTime = 0; v.loop = false; v.controls = true; v.play(); btn.hidden = true;
    });
  });

  /* Step 1: popup form */
  var modal = document.getElementById("hv-modal");
  if (modal) {
    var form = modal.querySelector("form");
    function open() { modal.classList.add("open"); modal.setAttribute("aria-hidden", "false"); setTimeout(function () { form.querySelector("input").focus(); }, 60); }
    function close() { modal.classList.remove("open"); modal.setAttribute("aria-hidden", "true"); }
    document.querySelectorAll("[data-hv-open]").forEach(function (b) { b.addEventListener("click", open); });
    modal.querySelector(".hv-close").addEventListener("click", close);
    modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
    if (location.hash === "#start") open();

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var err = form.querySelector(".err");
      var d = Object.fromEntries(new FormData(form).entries());
      if (!d.email || !d.address || d.address.trim().length < 6) { err.classList.add("show"); return; }
      err.classList.remove("show");
      var id = (Date.now().toString(36) + Math.random().toString(36).slice(2, 7)).toUpperCase();
      var lead = { step: "1", id: id, name: d.name || "", email: d.email, address: d.address,
                   source: qs("source") || qs("utm_source") || "direct", page: location.pathname, website: d.website || "" };
      store(false, lead);
      var b = form.querySelector("button"); b.disabled = true; b.textContent = "Sending…";
      send(lead).then(function () { location.href = "thank-you/?id=" + encodeURIComponent(id); });
    });
  }

  /* Step 2: thank-you details */
  var ty = document.getElementById("ty-form");
  if (ty) {
    var lead = store(true) || {};
    var id = qs("id") || lead.id || "";
    var first = (lead.name || "").trim().split(/\s+/)[0];
    if (first) document.querySelectorAll("[data-first]").forEach(function (el) { el.textContent = ", " + first; });
    if (lead.address) document.querySelectorAll("[data-address]").forEach(function (el) { el.textContent = lead.address; el.parentNode.hidden = false; });

    ty.addEventListener("submit", function (e) {
      e.preventDefault();
      var d = Object.fromEntries(new FormData(ty).entries());
      var err = ty.querySelector(".err");
      if (!d.phone || d.phone.replace(/\D/g, "").length < 10) { err.classList.add("show"); return; }
      err.classList.remove("show");
      d.step = "2"; d.id = id; d.email = lead.email || ""; d.address = lead.address || ""; d.name = lead.name || "";
      var b = ty.querySelector("button"); b.disabled = true; b.textContent = "Sending…";
      send(d).then(function () { ty.closest(".ty-card").classList.add("sent"); window.scrollTo({ top: 0, behavior: "smooth" }); });
    });
  }
})();
