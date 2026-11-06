"""Extra local-SEO pages, audit service pages, WhatsApp CTA and home audit section. Stdlib only.

Run:  python3 tools/build_pages.py     (idempotent)
Reads nav + footer from services/epf-registration/index.html and rewrites the footer everywhere.
Run tools/build_blog.py afterwards only if blog content changed; both scripts keep the footer in sync.
"""
import glob, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
from pages_content import LOCS, AUDITS

BASE = "https://teamindiacompliance.com"
LASTMOD = "2026-11-06"
PHONE_DISPLAY, PHONE_TEL, WA = "+91 86838 52482", "+918683852482", "918683852482"
SVC_NAMES = {"epf-registration": "EPF Registration & Compliance", "esic-registration": "ESIC Registration & Filings",
             "payroll-processing": "Payroll Processing", "factory-license": "Factory License",
             "labour-license-clra": "Labour License (CLRA)", "hr-consultancy": "HR Consultancy",
             "government-liaisoning": "Government Liaisoning", "statutory-audit": "Statutory Audits",
             "multi-state-setup": "Multi-State Setup", "shops-establishment-registration": "Shops & Establishments Registration"}
for a in AUDITS: SVC_NAMES[a["slug"]] = a["name"]
ALL_SVC = list(SVC_NAMES)

def read(p): return open(p, encoding="utf-8").read()
def write(p, s):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    open(p, "w", encoding="utf-8").write(s)
def esc(s): return html.escape(s, quote=True)
def li(items): return "".join(f"<li>{i}</li>" for i in items)
def svc_link(s): return f'<a href="/services/{s}/">{SVC_NAMES[s]}</a>'
WA_BTN = lambda src, cls="btn btn-secondary", style="", label="💬 Free health check on WhatsApp", msg="": (
    f'<a data-wa="{src}"' + (f' data-wa-msg="{esc(msg)}"' if msg else "") +
    f' href="https://wa.me/{WA}" class="{cls}"' + (f' style="{style}"' if style else "") + f">{label}</a>")

# ---------- chrome ----------
tpl = read("services/epf-registration/index.html")
NAV = tpl[tpl.index('<nav class="top">'):tpl.index("</nav>") + 6]
FOOTER = tpl[tpl.index("<!-- FOOTER -->"):tpl.index("</footer>") + 9]
AUD_LI = "".join(f'<li><a href="/services/{a["slug"]}/">{a["name"]}</a></li>' for a in AUDITS)
if "/services/hr-compliance-audit/" not in FOOTER:
    k = '<li><a href="/services/shops-establishment-registration/">Shops & Establishments Registration</a></li>'
    assert k in FOOTER; FOOTER = FOOTER.replace(k, k + AUD_LI, 1)
if 'href="/locations/"' not in FOOTER:
    k = '<li><a href="/locations/delhi-ncr/">Delhi NCR</a></li>'
    assert k in FOOTER; FOOTER = FOOTER.replace(k, k + '<li><a href="/locations/">All locations →</a></li>', 1)

def head(title, desc, path, lds):
    return f"""<meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <link rel="canonical" href="{BASE}{path}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#0A2463">
  <link rel="icon" href="/tic-logo.jpeg">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="TeamIndia Compliance">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{BASE}{path}">
  <meta property="og:image" content="{BASE}/tic-logo.jpeg">
  <meta property="og:locale" content="en_IN">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/style.css">
  {chr(10).join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in lds)}"""

def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}
def service_ld(name, desc, path, area=None):
    return {"@context": "https://schema.org", "@type": "Service", "name": name, "description": desc, "url": BASE + path,
            "serviceType": name, "provider": {"@id": BASE + "/#org"}, "areaServed": area or {"@type": "Country", "name": "India"}}
def faq_html(faqs):
    return "".join(f'<details class="faq-item"{" open" if i == 0 else ""}><summary>{esc(q)}</summary><div class="ans">{esc(a)}</div></details>' for i, (q, a) in enumerate(faqs))

def side(links, title):
    return f"""<aside class="side">
        <div class="side-card">
          <h4>Talk to a specialist</h4>
          <p>Free 30-minute consultation. Response within 4 working hours.</p>
          <a href="/#contact" class="btn btn-primary" style="width:100%;justify-content:center">Free Consultation →</a>
          {WA_BTN("sidebar", style="width:100%;justify-content:center;margin-top:10px")}
          <p style="margin:14px 0 0"><a href="tel:{PHONE_TEL}" style="color:var(--navy);font-weight:600">📞 {PHONE_DISPLAY}</a></p>
        </div>
        <div class="side-card"><h4>{title}</h4><ul>{li(links)}</ul></div>
      </aside>"""

CTA = f"""<section class="section" style="padding-top:0"><div class="container"><div class="side-card" style="text-align:center;padding:40px">
      <h3>Ready to get compliant?</h3><p style="margin:12px 0 22px">Tell us about your business and get a tailored proposal within 4 working hours.</p>
      <a href="/#contact" class="btn btn-primary">Request Free Consultation →</a> {WA_BTN("cta-band")}</div></div></section>"""

def page(title, desc, path, crumbs, h1, lead, main, side_html, lds):
    crumb_html = " › ".join(f'<a href="{u}">{n}</a>' for n, u in crumbs[:-1]) + f" › <span>{crumbs[-1][0]}</span>"
    return f"""<!DOCTYPE html>
<html lang="en-IN">

<head>
  {head(title, desc, path, list(lds) + [crumbs_ld(crumbs)])}
</head>

<body>

  {NAV}

  <section class="hero sub">
    <div class="container">
      <div class="crumbs" aria-label="Breadcrumb">{crumb_html}</div>
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>
      <div class="hero-ctas"><a href="/#contact" class="btn btn-primary">Request Free Consultation →</a><a href="tel:{PHONE_TEL}" class="btn btn-secondary">📞 {PHONE_DISPLAY}</a></div>
    </div>
  </section>

  <section class="section">
    <div class="container page-grid">
      <div class="prose">
{main}
      </div>
      {side_html}
    </div>
  </section>

  {CTA}

  {FOOTER}

</body>

</html>
"""

URLS = []

# ---------- audit service pages ----------
BLOG_EPF = "/blog/epf-wage-ceiling-raised-to-25000-what-employers-must-do/"
for a in AUDITS:
    path = f"/services/{a['slug']}/"
    tci = ""
    if a["slug"] == "hr-compliance-audit":
        tci = f"""<h2 id="tci">TeamIndia Compliance Index (TCI)</h2>
        <p>The TeamIndia Compliance Index (TCI) gives your compliance position a clear, trackable rating, so you can see where you stand today and measure progress after each audit.</p>
        <p>{WA_BTN("sample-report", msg="Hi TeamIndia Compliance, I would like to see a sample HR compliance audit report and know more about the TeamIndia Compliance Index (TCI).", label="💬 Request a sample audit report")}</p>"""
    main = f"""<h2>Why a {a['name'].lower()}?</h2>
        {''.join(f'<p>{esc(p)}</p>' for p in a['who'])}
        <h2>What we review</h2>
        <ul>{li(esc(x) for x in a['scope'])}</ul>
        {tci}
        <h2>Documents you will need</h2>
        <ul>{li(esc(x) for x in a['docs'])}</ul>
        <h2>How it works</h2>
        <ol>{li(esc(x) for x in a['steps'])}</ol>
        <h2>Where we serve</h2>
        <p>Headquartered in Gurugram, we run {esc(a['name'].lower())}s in <a href="/locations/gurugram/">Gurugram</a>, <a href="/locations/delhi/">Delhi</a>, <a href="/locations/noida/">Noida</a>, <a href="/locations/haryana/">Haryana</a> and across <a href="/locations/delhi-ncr/">Delhi NCR</a>, and pan-India.</p>
        <p>Related reading: <a href="{BLOG_EPF}">EPF wage ceiling raised to ₹25,000</a> and <a href="/blog/hidden-risk-in-your-salary-structure/">the hidden risk in your salary structure</a>.</p>
        <h2>Frequently asked questions</h2>
        <div class="faq-list">{faq_html(a['faqs'])}</div>"""
    write(f"services/{a['slug']}/index.html", page(a["title"], a["desc"], path,
          [("Home", "/"), ("Services", "/#services"), (a["name"], path)], a["h1"], a["lead"], main,
          side([svc_link(r) for r in a["related"]], "Related services"),
          [service_ld(a["name"], a["desc"], path), faq_ld(a["faqs"])]))
    URLS.append((path, "0.9"))

# ---------- location pages ----------
ALL_LOC_LINKS = [("Delhi", "delhi"), ("Gurugram", "gurugram"), ("Noida", "noida"), ("Haryana", "haryana"), ("Delhi NCR", "delhi-ncr")] + [(l["name"], l["slug"]) for l in LOCS]
for l in LOCS:
    path = f"/locations/{l['slug']}/"
    main = f"""<h2>Compliance support in {l['name']}</h2>
        {''.join(f'<p>{esc(p)}</p>' for p in l['intro'])}
        <h2>What {l['name']} employers typically need</h2>
        <ul>{li(esc(x) for x in l['needs'])}</ul>
        <h2>Local legal snapshot</h2>
        <ul><li>State: Haryana. Shops and offices fall under the Haryana Shops and Commercial Establishments Act, 1958.</li><li>Factory licensing: Haryana Department of Industrial Safety and Health.</li><li>Professional Tax: not levied in Haryana.</li><li>Central registrations: EPF and ESIC apply as per headcount thresholds. The PF wage ceiling is ₹25,000 a month from 17 September 2026 (<a href="{BLOG_EPF}">summary</a>).</li></ul>
        <h2>Areas we support</h2>
        <ul>{li(esc(x) for x in l['areas'])}</ul>
        <h2>Our services in {l['name']}</h2>
        <ul class="link-grid">{li(svc_link(s) for s in ALL_SVC)}</ul>
        <h2>Frequently asked questions</h2>
        <div class="faq-list">{faq_html(l['faqs'])}</div>"""
    others = [f'<a href="/locations/{s}/">{n}</a>' for n, s in ALL_LOC_LINKS if s != l["slug"]]
    lds = [service_ld(f"Labour law and HR compliance services in {l['name']}", l["desc"], path, {"@type": "City", "name": l["name"]}), faq_ld(l["faqs"])]
    write(f"locations/{l['slug']}/index.html", page(l["title"], l["desc"], path,
          [("Home", "/"), ("Locations", "/locations/"), (l["name"], path)], l["h1"], l["lead"], main, side(others, "Other locations"), lds))
    URLS.append((path, "0.8"))

# locations hub
cards = "".join(f'<a class="service-card" href="/locations/{s}/"><div class="service-icon">📍</div><h3>{n}</h3><p>Labour law, EPF, ESIC and HR compliance services in {n}.</p><span class="learn-more">Learn more →</span></a>' for n, s in ALL_LOC_LINKS)
hub_main = f'<div class="service-grid" style="grid-column:1/-1">{cards}</div>'
hub = page("Labour Law Compliance Locations: Delhi NCR & Haryana | TeamIndia Compliance",
           "Labour law, EPF, ESIC and HR compliance services across Delhi, Gurugram, Noida, Faridabad, Manesar, Sonipat, Bawal, Jhajjar, Rohtak and Bahadurgarh.",
           "/locations/", [("Home", "/"), ("Locations", "/locations/")], "Compliance Services Across Delhi NCR & Haryana",
           "Headquartered in Gurugram, serving employers across Delhi NCR, Haryana and India.", "", "", [])
# the hub uses a single full-width grid, not the 2-column layout
hub = hub.replace('<div class="container page-grid">\n      <div class="prose">\n\n      </div>\n      ', f'<div class="container">\n      {hub_main}\n      ', 1)
write("locations/index.html", hub)
URLS.append(("/locations/", "0.7"))

# ---------- site-wide edits ----------
FOOT_RE = re.compile(r"<!-- FOOTER -->.*?</footer>", re.S)
SIDE_OLD = '<a href="/#contact" class="btn btn-primary" style="width:100%;justify-content:center">Free Consultation →</a>'
for f in glob.glob("**/*.html", recursive=True):
    if f.startswith("tic-logo") or f.startswith("tools/"): continue
    s = read(f)
    if "<!-- FOOTER -->" in s: s = FOOT_RE.sub(lambda m: FOOTER, s, count=1)
    if 'data-wa="sidebar"' not in s and SIDE_OLD in s:
        s = s.replace(SIDE_OLD, SIDE_OLD + "\n          " + WA_BTN("sidebar", style="width:100%;justify-content:center;margin-top:10px"), 1)
    if "/wa.js" not in s and "</body>" in s:
        s = s.replace("</body>", '<script src="/wa.js" defer></script>\n</body>', 1)
    write(f, s)

# EPF service page wording: statute reference now Code on Social Security
f = "services/epf-registration/index.html"; s = read(f)
old = "The Employees&#x27; Provident Funds &amp; Miscellaneous Provisions Act, 1952 applies to establishments employing 20 or more persons."
if old in s:
    s = s.replace(old, "Provident fund coverage is governed by Chapter III of the Code on Social Security, 2020, which replaced the Employees&#x27; Provident Funds &amp; Miscellaneous Provisions Act, 1952. It applies to establishments employing 20 or more persons.")
    write(f, s)
f = "resources/epf-esic-applicability-rates-due-dates/index.html"; s = read(f)
old = "EPFO can also levy damages under Section 14B of the EPF Act on a graded scale — from 5% per annum for delays under two months up to 25% per annum beyond six months — capped at 100% of the arrears."
if old in s:
    s = s.replace(old, "EPFO can also levy damages for delayed deposits on a graded scale (historically 5% a year for delays under two months, up to 25% a year beyond six months, under Section 14B of the earlier EPF Act). Confirm the current rates under the Code on Social Security before relying on them.")
    write(f, s)

# Haryana + statutory-audit cross links
f = "locations/haryana/index.html"; s = read(f)
s = re.sub(r"<!-- city-pages -->.*?<!-- /city-pages -->\s*", "", s, flags=re.S)
city = '<!-- city-pages --><h2>City pages across Haryana</h2><ul class="link-grid">' + li(f'<a href="/locations/{x["slug"]}/">{x["name"]}</a>' for x in LOCS) + '<li><a href="/locations/gurugram/">Gurugram</a></li></ul><!-- /city-pages -->\n        '
k = "<h2>Our services in Haryana</h2>"; assert k in s
write(f, s.replace(k, city + k, 1))
f = "services/statutory-audit/index.html"; s = read(f)
s = re.sub(r"<!-- audits -->.*?<!-- /audits -->\s*", "", s, flags=re.S)
blk = '<!-- audits --><h2>Specialised audits</h2><ul>' + li(f'<a href="/services/{a["slug"]}/">{a["name"]}</a>' for a in AUDITS) + '</ul><!-- /audits -->\n        '
k = "<h2>Frequently asked questions</h2>"; assert k in s
write(f, s.replace(k, blk + k, 1))

# ---------- home: audit section + WhatsApp in contact + schema ----------
s = read("index.html")
s = re.sub(r"<!-- AUDITS -->.*?<!-- /AUDITS -->\s*", "", s, flags=re.S)
acards = "".join(f'<a class="service-card" href="{u}"><div class="service-icon">{i}</div><h3>{n}</h3><p>{esc(d)}</p><span class="learn-more">Learn more →</span></a>' for i, n, d, u in [
    ("🔍", "HR Compliance Audit", "Registrations, records, policies, POSH and Labour Codes readiness, with a ranked remediation plan.", "/services/hr-compliance-audit/"),
    ("💰", "Payroll Audit", "Salary structure, PF and ESIC wage base, TDS and the new ₹25,000 PF ceiling, reconciled line by line.", "/services/payroll-audit/"),
    ("👷", "Contractor Compliance Audit", "Verify contractor licences, wage payment and PF/ESIC remittance for contract workers.", "/services/contractor-compliance-audit/"),
    ("📊", "TeamIndia Compliance Index (TCI)", "A clear, trackable rating of your compliance position, so you can measure progress audit by audit.", "/services/hr-compliance-audit/#tci")])
audits = f"""<!-- AUDITS -->
  <section class="section" id="audits">
    <div class="container">
      <div class="section-head">
        <span class="eyebrow">Compliance Audits</span>
        <h2>Know Exactly Where You Stand</h2>
        <p>Independent audits that show your risks, quantify the exposure and give you a fix plan.</p>
      </div>
      <div class="service-grid" style="grid-template-columns:repeat(4,1fr)">{acards}</div>
      <p style="text-align:center;margin-top:32px">{WA_BTN("audit-health-check", "btn btn-primary", label="💬 Free Compliance Health Check on WhatsApp", msg="Hi TeamIndia Compliance, I would like a free compliance health check for my business.")} {WA_BTN("audit-sample-report", label="Request a sample audit report", msg="Hi TeamIndia Compliance, please share a sample audit report.")}</p>
    </div>
  </section>
  <!-- /AUDITS -->

  """
assert "<!-- LOCATIONS -->" in s
s = s.replace("<!-- LOCATIONS -->", audits + "<!-- LOCATIONS -->", 1)
if 'data-wa="contact"' not in s:
    m = re.search(r"(Mon – Sat, 9:30 AM – 7:00 PM IST</div>\s*</div>\s*</div>\s*</div>)", s)
    assert m
    s = s.replace(m.group(1), m.group(1) + "\n        " + WA_BTN("contact", "btn btn-secondary", "margin-top:20px"), 1)
# schema: drop unverified legal name, widen area served
def fix_ld(m):
    d = json.loads(m.group(1))
    if isinstance(d, dict) and d.get("@id") == BASE + "/#org":
        d.pop("legalName", None)
        d["areaServed"] = [{"@type": "Country", "name": "India"}] + [{"@type": "City", "name": n} for n in ("Delhi", "Gurugram", "Noida", "Faridabad", "Manesar", "Sonipat", "Bawal", "Jhajjar", "Rohtak", "Bahadurgarh")] + [{"@type": "AdministrativeArea", "name": "Haryana"}]
    return 'ld+json">' + json.dumps(d, ensure_ascii=False) + "</script>"
s = re.sub(r'ld\+json">(.*?)</script>', fix_ld, s, flags=re.S)
write("index.html", s)

# ---------- CSS + wa.js ----------
css = read("style.css")
if "/* === WHATSAPP === */" not in css:
    css += """
/* === WHATSAPP === */
.wa-float { position: fixed; right: 20px; bottom: 20px; z-index: 300; display: inline-flex; align-items: center; gap: 8px; background: #25D366; color: #fff; padding: 12px 18px; border-radius: 100px; font-weight: 700; font-size: 15px; box-shadow: 0 8px 24px rgba(37, 211, 102, .45); transition: transform .15s ease; }
.wa-float:hover { transform: translateY(-2px); }
.wa-float svg { width: 24px; height: 24px; fill: #fff; }
@media (max-width: 520px) { .wa-float span { display: none; } .wa-float { padding: 14px; } }
#audits .service-grid { grid-template-columns: repeat(4, 1fr); }
@media (max-width: 1100px) { #audits .service-grid { grid-template-columns: repeat(2, 1fr) !important; } }
@media (max-width: 700px) { #audits .service-grid { grid-template-columns: 1fr !important; } }
"""
    write("style.css", css)
write("wa.js", f"""(function () {{
  var N = "{WA}";
  function text() {{
    var h = document.querySelector("h1");
    var t = h ? h.textContent.replace(/\\s+/g, " ").trim() : document.title;
    return 'Hi TeamIndia Compliance, I was reading "' + t + '" (' + location.href.split("#")[0] + ") and would like a free compliance health check.";
  }}
  function url(m) {{ return "https://wa.me/" + N + "?text=" + encodeURIComponent(m || text()); }}
  function track(src) {{
    try {{
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({{ event: "whatsapp_click", wa_source: src, page_path: location.pathname }});
      if (window.gtag) window.gtag("event", "whatsapp_click", {{ wa_source: src, page_path: location.pathname }});
    }} catch (e) {{}}
  }}
  document.querySelectorAll("[data-wa]").forEach(function (a) {{
    a.href = url(a.getAttribute("data-wa-msg"));
    a.target = "_blank"; a.rel = "noopener";
    a.addEventListener("click", function () {{ track(a.getAttribute("data-wa")); }});
  }});
  var f = document.createElement("a");
  f.className = "wa-float"; f.href = url(); f.target = "_blank"; f.rel = "noopener";
  f.setAttribute("aria-label", "Chat on WhatsApp");
  f.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38a9.9 9.9 0 0 0 4.74 1.21c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2zm0 18.15a8.2 8.2 0 0 1-4.19-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.2 8.2 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.25-8.24 2.2 0 4.27.86 5.82 2.42a8.18 8.18 0 0 1 2.41 5.83c0 4.54-3.7 8.23-8.24 8.23zm4.52-6.16c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.12-.17.25-.64.81-.78.97-.14.17-.29.19-.54.06-.25-.12-1.05-.39-2-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.02-.38.11-.5.11-.11.25-.29.37-.43.12-.14.17-.25.25-.41.08-.17.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.43.06-.66.31-.23.25-.87.85-.87 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.14-1.18-.06-.1-.23-.16-.48-.29z"/></svg><span>WhatsApp</span>';
  f.addEventListener("click", function () {{ track("float"); }});
  document.body.appendChild(f);
}})();
""")

# ---------- sitemap ----------
sm = read("sitemap.xml")
for p, _ in URLS:
    sm = re.sub(r"  <url><loc>" + re.escape(BASE + p) + r"</loc>.*?</url>\n", "", sm)
sm = sm.replace("</urlset>", "".join(f"  <url><loc>{BASE}{p}</loc><lastmod>{LASTMOD}</lastmod></url>\n" for p, _ in URLS) + "</urlset>")
write("sitemap.xml", sm)
print("pages:", len(URLS))
