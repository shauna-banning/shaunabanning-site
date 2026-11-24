#!/usr/bin/env python3
"""Generate community pages from _tools/communities.json.
Usage: python3 _tools/build_communities.py [slug ...]   (no args = all)
Each page lands at /<slug>/index.html, using the same stylesheet as the FishHawk page."""
import json, sys, html, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, "_tools", "communities.json")))
LOADER = """<script>
  (function(w, d, t, h, s, n) {
    w.FlodeskObject = n;
    var fn = function() { (w[n].q = w[n].q || []).push(arguments); };
    w[n] = w[n] || fn;
    var f = d.getElementsByTagName(t)[0];
    var v = '?v=' + Math.floor(new Date().getTime() / (120 * 1000)) * 60;
    var sm = d.createElement(t); sm.async = true; sm.type = 'module'; sm.src = h + s + '.mjs' + v;
    f.parentNode.insertBefore(sm, f);
    var sn = d.createElement(t); sn.async = true; sn.noModule = true; sn.src = h + s + '.js' + v;
    f.parentNode.insertBefore(sn, f);
  })(window, document, 'script', 'https://assets.flodesk.com', '/universal', 'fd');
</script>"""
E = html.escape
ICONS = {
 "price": '<path d="M3 12V4h8l9 9-8 8-9-9z"/><circle cx="7.5" cy="8.5" r="1.5"/>',
 "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
 "hoa": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>',
 "cdd": '<path d="M4 7h16v12H4z"/><path d="M4 11h16"/><path d="M8 3v4M16 3v4"/>',
 "school": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/>',
 "car": '<path d="M5 16l1.5-5h11L19 16"/><rect x="3" y="16" width="18" height="4" rx="1"/><circle cx="7" cy="20" r="1.5"/><circle cx="17" cy="20" r="1.5"/>',
 "pin": '<path d="M12 21s-7-6.5-7-12a7 7 0 0114 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
 "water": '<path d="M2 12c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/><path d="M2 17c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/>',
 "plane": '<path d="M2 16l20-7-3-2-7 3-5-5-2 1 3 6-4 2-2-1-1 1z"/>',
 "hospital": '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M12 8v8M8 12h8"/>',
 "build": '<path d="M3 21h18"/><path d="M5 21V8l7-4 7 4v13"/><path d="M9 21v-5h6v5"/>',
}
def icon_for(label):
    l = label.lower()
    for k, key in [("price","price"),("homes","home"),("hoa","hoa"),("cdd","cdd"),("school","school"),("macdill","car"),("downtown","car"),("airport","plane"),("general","hospital"),("size","pin"),("setting","pin"),("built","build"),("flood","water")]:
        if k in l: return ICONS[key]
    return ICONS["pin"]

def stats(c):
    s = c.get("stats")
    if not s:
        cells = [("—", "Homes sold, last 90 days"), ("—", "Median sold price"), ("—", "Median days to contract"), ("—", "Homes for sale right now")]
        note = f"First monthly numbers drop {c['first_update']}. Source: Stellar MLS, {E(c.get('scope', c['name'] + ' subdivisions'))}."
    else:
        cells = s["cells"]; note = s["note"]
    return "\n".join(f'          <div class="stat"><b>{E(v)}</b><span>{E(l)}</span></div>' for v, l in cells), note

def form(c):
    if c.get("flodesk_form_id"):
        fid = c["flodesk_form_id"]
        return f"""<div class="form">
      <div id="fd-form-{fid}"></div>
      <script>window.fd('form',{{formId:'{fid}',containerEl:'#fd-form-{fid}'}});</script>
      <small>By signing up you agree to receive emails from Shauna Banning, Coldwell Banker Realty.</small>
    </div>"""
    return f"""<!-- FLODESK TODO: create form "{c['name']} – Monthly Update (Website)" → segment "{c['name']}", then put its id in communities.json -->
    <div class="form">
      <p style="margin:0 0 14px;color:var(--ink)"><b>The monthly signup opens with the first update.</b> Want it now? Text me and I'll add you.</p>
      <a class="btn btn-dark" href="sms:+14254954577?&body={E(c['name']).replace(' ','%20')}%20update%20-%20Hi%20Shauna!%20Please%20add%20me%20to%20the%20monthly%20{E(c['name']).replace(' ','%20')}%20update.">Text Me "UPDATE"</a>
      <small>Shauna Banning, Coldwell Banker Realty.</small>
    </div>"""

def band(c):
    b = (c.get("photos") or {}).get("band")
    if not b: return ""
    return f'<div class="photo-band" role="img" aria-label="{E(b["alt"])}" style="background-image:url(../assets/img/{b["src"]})"></div>'

def school_img(c):
    b = (c.get("photos") or {}).get("schools")
    if not b: return ""
    return f'<img class="school-photo" src="../assets/img/{b["src"]}" alt="{E(b["alt"])}" loading="lazy">'

def hoods(c):
    h = c.get("hoods")
    if not h: return ""
    cards = "\n".join(f'      <div class="card"><span class="tag">{E(t)}</span><h3>{E(name)}</h3><p>{p}</p>' + (f'<p><a href="../{link}/"><b>Read the {E(name)} guide &rarr;</b></a></p>' if link else '') + '</div>' for t, name, p, link in h["cards"])
    return f"""<!-- ===== NEIGHBORHOODS ===== -->
<section class="alt">
  <div class="wrap">
    <span class="eyebrow">Where to Look</span>
    <h2>{E(h['h2'])}</h2>
    <p class="lead">{h['lead']}</p>
    <div class="grid-3" style="margin-top:34px">
{cards}
    </div>
  </div>
</section>
"""

# ===== FREE DOWNLOADS (same on every page). Fill in Flodesk form ids to switch the section on. =====
DOWNLOADS = [
 # (title, blurb, flodesk_form_id)
 ("The Complete Guide to Buying a Home", "Every step from pre-approval to keys, with Florida costs nobody mentions.", ""),
 ("Moving Checklist", "What to do 8 weeks, 4 weeks and 1 week out, plus your first week here.", ""),
 ("The Complete Guide to Selling a Home", "How to price, prep and market your home to sell for top dollar.", ""),
 ("30-Day Plan to Prep Your Home for Sale", "A simple day-by-day list to get your home photo-ready in a month.", ""),
]
def downloads(slug):
    if not all(d[2] for d in DOWNLOADS): return "<!-- FREE DOWNLOADS: hidden until all 4 Flodesk form ids are filled in DOWNLOADS -->"
    cards = "\n".join(f'''      <div class="card dl"><span class="tag">Free Download</span><h3>{E(t)}</h3><p>{E(b)}</p>
        <div id="fd-form-{fid}"></div><script>window.fd('form',{{formId:'{fid}',containerEl:'#fd-form-{fid}'}});</script></div>''' for t, b, fid in DOWNLOADS)
    return f'''<!-- ===== FREE DOWNLOADS ===== -->
<section id="downloads" class="alt">
  <div class="wrap">
    <span class="eyebrow">Free Downloads</span>
    <h2>Guides for Buying, Selling &amp; Moving</h2>
    <p class="lead">Pick what fits where you are. Each one lands in your inbox.</p>
    <div class="grid-2" style="margin-top:34px">
{cards}
    </div>
  </div>
</section>
'''

GA = """<!-- Google Analytics (GA4). Every form submit (home value, Flodesk sign-ups) is sent as a generate_lead event. -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-SLBMHTPVP9"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-SLBMHTPVP9');
document.addEventListener('submit',function(e){var f=e.target||{};gtag('event','generate_lead',{form_name:(f.getAttribute&&(f.getAttribute('class')||f.id))||'form',page_path:location.pathname});},true);</script>
"""

def page(slug, c):
    url = f"https://shaunabanning.com/{slug}/"
    stat_html, note = stats(c)
    faq = c["faq"]
    faq_ld = ",\n".join(json.dumps({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}) for q, a in faq)
    if not c.get("hero") and (c.get("photos") or {}).get("hero"): c["hero"] = c["photos"]["hero"]
    hero_img = f'<img class="bg" src="../assets/img/{c["hero"]["src"]}" alt="{E(c["hero"]["alt"])}">' if c.get("hero") else ""
    hero_cls = "hero" if c.get("hero") else "hero hero-type"
    glance = "\n".join(f'        <li><i><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{icon_for(k)}</svg></i><div><span>{E(k)}</span><b>{E(v)}</b></div></li>' for k, v in c["glance"])
    lat, lon = c["coords"]
    life = "\n".join(f'      <div class="card"><span class="tag">{E(t)}</span><h3>{E(h)}</h3><p>{p}</p></div>' for t, h, p in c["life"])
    costs = "\n".join(f"        <tr><td>{E(a)}</td><td>{E(b)}</td><td>{d}</td></tr>" for a, b, d in c["costs"])
    gr = lambda g: f'<span class="grade">{g}</span>' if g else "—"
    schools = "\n".join(f"        <tr><td>{E(r[0])}</td><td>{E(r[1])}</td><td>{gr(r[2])}</td><td>{gr(r[3])}</td></tr>" for r in c["schools"]) if c["schools"] else '        <tr><td colspan="2">Zoning varies by section. I\'ll confirm the schools for any address you\'re considering.</td></tr>'
    tips = "\n".join(f'      <div class="tip"><h3>{E(h)}</h3><p>{p}</p></div>' for h, p in c["tips"])
    faqs = "\n".join(f"      <details><summary>{E(q)}</summary><p>{a}</p></details>" for q, a in faq)
    n = E(c["name"])
    return f"""<!doctype html>
<html lang="en">
<head>
{GA}<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(c['title'])}</title>
<meta name="description" content="{E(c['description'])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{n} Market Update &amp; Living Guide">
<meta property="og:description" content="{E(c['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://shaunabanning.com/assets/img/{c['hero']['src'] if c.get('hero') else 'shauna-banning-realtor.jpg'}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/style.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js" defer></script>
{LOADER}
<script type="application/ld+json">
{{"@context":"https://schema.org","@graph":[
{{"@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"https://shaunabanning.com/"}},{{"@type":"ListItem","position":2,"name":"{n}","item":"{url}"}}]}},
{{"@type":"Place","name":"{n}","address":{{"@type":"PostalAddress","addressLocality":"{E(c['city'])}","addressRegion":"FL","postalCode":"{E(c['zip'])}"}}}},
{{"@type":"FAQPage","mainEntity":[
{faq_ld}
]}}]}}
</script>
</head>
<body>

<nav class="nav"><div class="wrap">
  <a class="brand" href="../"><strong>Shauna Banning</strong><span>Your Tampa Suburbs Realtor</span></a>
  <ul>
    <li class="hide-sm"><a href="#market-update">Market Update</a></li>
    <li class="hide-sm"><a href="#living">Living Here</a></li>
    <li class="hide-sm"><a href="#faq">FAQ</a></li>
    <li><a class="btn btn-dark btn-sm" href="../home-value/?source={slug}">Home Value</a></li>
  </ul>
</div></nav>

<header class="{hero_cls}">
  {hero_img}
  <div class="wrap">
    <span class="eyebrow">{E(c.get('eyebrow') or (c['name'] + ' · ' + c['city'] + ', FL ' + c['zip']))}</span>
    <h1>{E(c['h1'])}</h1>
    <p>{c['intro']}</p>
    <div class="btns">
      <a class="btn btn-caramel" href="../home-value/?source={slug}">What's My Home Worth?</a>
      <a class="btn btn-light" href="{E(c['search_url'])}" rel="noopener">See Homes for Sale</a>
    </div>
  </div>
</header>

<div class="wrap crumbs"><a href="../">Home</a> / {n}</div>

<!-- ===== MONTHLY MARKET UPDATE — refresh by the 15th ===== -->
<section id="market-update">
  <div class="wrap">
    <span class="eyebrow">Monthly Market Update</span>
    <h2>The {n} Market, Every Month</h2>
    <p class="lead">What sold, what's sitting and what it means for your home's value. New video by the 15th.</p>
    <div class="update-grid">
      <div class="video">
        <!-- When the video is live, delete .video-soon and use:
        <iframe src="https://www.youtube.com/embed/videoseries?list=PLAYLIST_ID" title="{n} market update" loading="lazy" allowfullscreen></iframe> -->
        <div class="video-soon" style="background:linear-gradient(135deg,#111 0%,#3a2a1e 55%,#7f5536 100%)">
          <span class="eyebrow" style="color:#e9c9a8">Video coming {E(c['first_update'])}</span>
          <h3>The First {n} Market Update</h3>
          <p>Get it in your inbox the day it drops.</p>
          <a class="btn btn-caramel btn-sm" href="#monthly">Send It to Me</a>
        </div>
      </div>
      <div>
        <div class="stats">
          <!-- STATS: update monthly from the Stellar MLS export (90-day window) -->
{stat_html}
        </div>
        <p class="stat-note">{note} Deemed reliable but not guaranteed.</p>
      </div>
    </div>
  </div>
</section>

<!-- ===== HOME VALUE BAND (CTA #2) ===== -->
<section class="hv-band">
  <div class="wrap">
    <div>
      <span class="eyebrow" style="color:#f3dcc4">Free · No Obligation</span>
      <h2>What's Your {n} Home Worth?</h2>
      <p>Get a free home value report from a local Realtor. Real comps from your street, not a bot estimate.</p>
    </div>
    <a class="btn btn-light" href="../home-value/?source={slug}-band">Get My Free Report</a>
  </div>
</section>

<!-- ===== AT A GLANCE ===== -->
<section class="alt">
  <div class="wrap">
    <span class="eyebrow">At a Glance</span>
    <h2>{E(c['glance_h2'])}</h2>
    <div class="facts-map">
      <ul class="facts-list">
{glance}
      </ul>
      <div id="cmap" role="region" aria-label="Map of {n} with MacDill AFB, downtown Tampa, Tampa General Hospital and Tampa International Airport"></div>
    </div>
    <p class="fine">Drive times are without traffic. Weekday rush hour typically adds 15 to 30 minutes.</p>
  </div>
</section>

<!-- ===== LIFE HERE ===== -->
<section id="living">
  <div class="wrap">
    <span class="eyebrow">Living Here</span>
    <h2>{E(c['life_h2'])}</h2>
    <p class="lead">{c['life_lead']}</p>
    <div class="grid-3" style="margin-top:34px">
{life}
    </div>
  </div>
</section>

{hoods(c)}
{band(c)}
<!-- ===== COSTS ===== -->
<section class="alt">
  <div class="wrap">
    <span class="eyebrow">What It Really Costs</span>
    <h2>HOA, CDD &amp; Insurance</h2>
    <p class="lead">Your monthly cost is more than the mortgage. Here's everything else to plan for in {n}.</p>
    <div class="table-wrap"><table>
      <thead><tr><th>Cost</th><th>Rough range</th><th>What to know</th></tr></thead>
      <tbody>
{costs}
      </tbody>
    </table></div>
    <p class="fine">Ranges come from recent listings and community documents and vary by section and lot. Ask for the exact amounts on any home you're serious about. Homestead by March 1 with the <a href="https://hcpafl.org/E-Filing/Homestead-E-File" rel="noopener">Hillsborough County Property Appraiser</a>.</p>
  </div>
</section>

<!-- ===== SCHOOLS ===== -->
<section>
  <div class="wrap">
    <span class="eyebrow">Schools</span>
    <h2>{n} Schools</h2>
    {school_img(c)}
    <p class="lead">{n} is in Hillsborough County Public Schools. Your zone depends on the exact address.</p>
    <div class="table-wrap"><table>
      <thead><tr><th>School</th><th>Grades</th><th>2025-26</th><th>2024-25</th></tr></thead>
      <tbody>
{schools}
      </tbody>
    </table></div>
    <p class="fine">{E(c.get('schools_note') or ('Schools most often listed for ' + c['name'] + ' addresses'))}, with Florida Department of Education grades released July 2026. Boundaries change, so confirm with the <a href="https://www.hillsboroughschools.org/" rel="noopener">district</a> before you go under contract. Not set on your zoned school? Hillsborough also offers school choice, magnet and charter options, and I can help you sort through them.</p>
  </div>
</section>

<!-- ===== TIPS ===== -->
<section class="alt">
  <div class="wrap">
    <span class="eyebrow">The Stuff Nobody Tells You</span>
    <h2>What People Learn After They Move In</h2>
    <div class="tips">
{tips}
    </div>
  </div>
</section>

<!-- ===== MONTHLY SIGNUP ===== -->
<section id="monthly" class="dark">
  <div class="wrap capture">
    <div>
      <span class="eyebrow">Free · Monthly</span>
      <h2>Get the {n} Update in Your Inbox</h2>
      <p>One email a month: what sold, what it sold for and what it means for your home.</p>
      <p style="color:#a9a39b;font-size:.9rem">No spam, unsubscribe anytime.</p>
    </div>
    {form(c)}
  </div>
</section>

{downloads(slug)}
<!-- ===== FAQ ===== -->
<section id="faq">
  <div class="wrap">
    <span class="eyebrow">{n} FAQ</span>
    <h2>Common Questions</h2>
    <div class="faq">
{faqs}
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap about">
    <img src="../assets/img/shauna-banning-realtor.jpg" alt="Shauna Banning, Realtor with Coldwell Banker Realty" loading="lazy">
    <div>
      <span class="eyebrow">Your Tampa Suburbs Realtor</span>
      <h2>Hi, I'm Shauna.</h2>
      <p>I moved here from Seattle about six years ago, so I know what it's like to pick a neighborhood from 2,000 miles away. I help families buy and sell across Riverview, Brandon, Valrico, FishHawk and Apollo Beach, and I'll always give you the straight answer, even if it's "not this house."</p>
      <ul class="contact-lines">
        <li>Call or text: <a href="tel:+14254954577">(425) 495-4577</a></li>
        <li>Email: <a href="mailto:shaunasellstampa@gmail.com">shaunasellstampa@gmail.com</a></li>
        <li>Coldwell Banker Realty</li>
      </ul>
      <div class="btns">
        <a class="btn btn-dark" href="sms:+14254954577">Text Me</a>
        <a class="btn btn-light" href="../home-value/?source={slug}">Get My Home Value</a>
      </div>
    </div>
  </div>
</section>

<footer>
  <div class="wrap f4">
    <div>
      <h4>Shauna Banning</h4>
      <p>REALTOR® · Coldwell Banker Realty<br>Your Tampa Suburbs Realtor<br><a href="tel:+14254954577">(425) 495-4577</a> · <a href="mailto:shaunasellstampa@gmail.com">shaunasellstampa@gmail.com</a></p>
    </div>
    <div>
      <h4>Areas</h4>
      <ul><li><a href="../brandon/">Brandon</a></li><li><a href="../valrico/">Valrico</a></li><li><a href="../riverview/">Riverview</a></li><li><a href="../fishhawk-ranch/">FishHawk</a></li></ul>
    </div>
    <div>
      <h4>Neighborhoods</h4>
      <ul><li><a href="../south-fork/">South Fork</a></li><li><a href="../triple-creek/">Triple Creek</a></li><li><a href="../river-hills/">River Hills</a></li><li><a href="../waterset/">Waterset</a></li><li><a href="../mirabay/">MiraBay</a></li></ul>
    </div>
    <div>
      <h4>Quick Links</h4>
      <ul><li><a href="../home-value/?source={slug}">Home Value</a></li><li><a href="../where-to-live-near-macdill/">Where to Live Near MacDill</a></li><li><a href="../macdill-bah-calculator/">MacDill BAH Calculator</a></li><li><a href="../">Home</a></li></ul>
    </div>
  </div>
  <div class="legal">© 2026 Shauna Banning. Coldwell Banker Realty. Equal Housing Opportunity. Information is deemed reliable but not guaranteed. Costs, fees, school zones and boundaries change, so verify them for your specific address. Nothing here is legal, tax or insurance advice.</div>
</footer>
<script>
window.addEventListener('load',function(){{
  if(!window.L)return;
  var here=[{lat},{lon}],gate=[27.8935,-82.5055],dt=[27.9506,-82.4572],tpa=[27.9755,-82.5332],tgh=[27.9376,-82.4590];
  var m=L.map('cmap',{{scrollWheelZoom:false,dragging:!L.Browser.mobile,tap:false,zoomControl:false}});
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}',{{maxZoom:16,attribution:'Tiles &copy; Esri &copy; OpenStreetMap contributors'}}).addTo(m);
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{{z}}/{{y}}/{{x}}',{{maxZoom:16,opacity:.7}}).addTo(m);
  function ic(t,c){{return L.divIcon({{className:'',html:'<div class="mk '+c+'"><i></i><span>'+t+'</span></div>',iconSize:null,iconAnchor:[9,9]}})}}
  L.marker(here,{{icon:ic('{n}','here'),zIndexOffset:1000}}).addTo(m);
  L.marker(gate,{{icon:ic('MacDill AFB','base')}}).addTo(m);
  L.marker(dt,{{icon:ic('Downtown Tampa','dt')}}).addTo(m);
  L.marker(tpa,{{icon:ic('TPA Airport','dt')}}).addTo(m);
  L.marker(tgh,{{icon:ic('Tampa General','dt')}}).addTo(m);
  var fit=function(){{m.invalidateSize();m.fitBounds(L.latLngBounds([here,gate,dt,tpa,tgh]),{{padding:[40,40]}});}};
  fit();setTimeout(fit,300);
}});
</script>
</body>
</html>
"""

slugs = sys.argv[1:] or list(DATA)
for s in slugs:
    os.makedirs(os.path.join(ROOT, s), exist_ok=True)
    open(os.path.join(ROOT, s, "index.html"), "w").write(page(s, DATA[s]))
    print("built", s)
