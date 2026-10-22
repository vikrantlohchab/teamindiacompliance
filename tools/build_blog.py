"""Generate the /blog/ pages and wire them into the site. Stdlib only.

Run from anywhere:  python3 tools/build_blog.py
Idempotent: safe to re-run after editing tools/blog_content.py.
Reads nav + footer from an existing generated page, so site chrome stays in sync.
"""
import glob, html, json, os, re, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
from blog_content import POSTS

BASE = "https://teamindiacompliance.com"
PHONE_DISPLAY, PHONE_TEL = "+91 86838 52482", "+918683852482"
SVC_NAMES = {"epf-registration": "EPF Registration & Compliance", "payroll-processing": "Payroll Processing",
             "statutory-audit": "Statutory Audits", "government-liaisoning": "Government Liaisoning",
             "hr-consultancy": "HR Consultancy", "multi-state-setup": "Multi-State Setup"}

def read(p): return open(p, encoding="utf-8").read()
def write(p, s):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    open(p, "w", encoding="utf-8").write(s)
def esc(s): return html.escape(s, quote=True)
def fmt_date(d): return date.fromisoformat(d).strftime("%-d %b %Y")

# ---------- markdown (just what the posts use) ----------
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(((?:[^()]|\([^()]*\))+)\)", lambda m: f'<a href="{m.group(2)}"' + ("" if m.group(2).startswith(("/", "#")) else ' target="_blank" rel="noopener"') + f">{m.group(1)}</a>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*(?!\s)([^*]+?)\*(?!\w)", r"<em>\1</em>", t)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", t)

def md(src):
    out, lines, i = [], src.strip().split("\n"), 0
    while i < len(lines):
        l = lines[i]
        if not l.strip(): i += 1; continue
        if l.startswith("### "): out.append(f"<h2>{inline(l[4:])}</h2>"); i += 1
        elif l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], rows[2:]
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tr = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>')
        elif re.match(r"(- |\d+\. )", l):
            tag = "ul" if l.startswith("- ") else "ol"
            items = []
            while i < len(lines) and re.match(r"(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i])); i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
        else:
            out.append(f"<p>{inline(l)}</p>"); i += 1
    return "\n        ".join(out)

# ---------- chrome from an existing page ----------
tpl = read("services/epf-registration/index.html")
NAV = tpl[tpl.index("<nav class=\"top\">"):tpl.index("</nav>") + 6]
FOOTER = tpl[tpl.index("<!-- FOOTER -->"):tpl.index("</footer>") + 9]
BLOG_LINKS = '<li><a href="/blog/">Blog</a></li>'
FOOTER = FOOTER if BLOG_LINKS in FOOTER else FOOTER.replace('<li><a href="/resources/">Guides</a></li>', BLOG_LINKS + '<li><a href="/resources/">Guides</a></li>', 1)

def head(title, desc, path, lds, image=None, og_type="website"):
    img = f"{BASE}{image}" if image else f"{BASE}/tic-logo.jpeg"
    card = "summary_large_image" if image else "summary"
    return f"""<meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <link rel="canonical" href="{BASE}{path}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#0A2463">
  <link rel="icon" href="/tic-logo.jpeg">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="TeamIndia Compliance">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{BASE}{path}">
  <meta property="og:image" content="{img}">
  <meta property="og:locale" content="en_IN">
  <meta name="twitter:card" content="{card}">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{img}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/style.css">
  {chr(10).join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in lds)}"""

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}

def card_html(p):
    return f"""<a class="post-card" href="/blog/{p['slug']}/">
          <img src="/blog/images/{p['image']}.svg" alt="{esc(p['alt'])}" width="1200" height="630" loading="lazy">
          <div class="post-card-body"><span class="service-tag popular">{esc(p['cat'])}</span>
          <h3>{esc(p['h1'])}</h3><p>{esc(p['desc'])}</p>
          <span class="post-card-meta">{fmt_date(p['date'])} · {p['mins']} min read</span></div></a>"""

def shell(title, desc, path, lds, hero_h1, hero_lead, crumbs, main_html, image=None, og_type="website", pre=""):
    crumb_html = " › ".join(f'<a href="{u}">{n}</a>' for n, u in crumbs[:-1]) + f" › <span>{crumbs[-1][0]}</span>"
    return f"""<!DOCTYPE html>
<html lang="en-IN">

<head>
  {head(title, desc, path, lds + [crumbs_ld(crumbs)], image, og_type)}
</head>

<body>

  {NAV}

  <section class="hero sub">
    <div class="container">
      <div class="crumbs" aria-label="Breadcrumb">{crumb_html}</div>
      <h1>{hero_h1}</h1>
      <p class="lead">{hero_lead}</p>
      {pre}
    </div>
  </section>

{main_html}

  {FOOTER}

</body>

</html>
"""

ORG = {"@id": BASE + "/#org"}
PUBLISHED = []

# ---------- posts ----------
for n, p in enumerate(POSTS):
    path = f"/blog/{p['slug']}/"
    others = [q for q in POSTS if q is not p]
    side_posts = "".join(f'<li><a href="/blog/{q["slug"]}/">{esc(q["h1"])}</a></li>' for q in others[:4])
    side_svc = "".join(f'<li><a href="/services/{s}/">{SVC_NAMES[s]}</a></li>' for s in p["related"])
    meta = f'<div class="post-meta"><span class="service-tag popular">{esc(p["cat"])}</span><span>{fmt_date(p["date"])}</span><span>{p["mins"]} min read</span><span>By TeamIndia Compliance Team</span></div>'
    main = f"""  <section class="section">
    <div class="container">
      <img class="post-hero" src="/blog/images/{p['image']}.svg" alt="{esc(p['alt'])}" width="1200" height="630">
      <div class="page-grid">
        <article class="prose">
        {md(p['body'])}
        </article>
        <aside class="side">
          <div class="side-card">
            <h4>Talk to a specialist</h4>
            <p>Free 30-minute consultation. Response within 4 working hours.</p>
            <a href="/#contact" class="btn btn-primary" style="width:100%;justify-content:center">Free Consultation →</a>
            <p style="margin:14px 0 0"><a href="tel:{PHONE_TEL}" style="color:var(--navy);font-weight:600">📞 {PHONE_DISPLAY}</a></p>
          </div>
          <div class="side-card"><h4>Related services</h4><ul>{side_svc}</ul></div>
          <div class="side-card"><h4>More from the blog</h4><ul>{side_posts}</ul></div>
        </aside>
      </div>
    </div>
  </section>

  <section class="section" style="padding-top:0"><div class="container"><div class="side-card" style="text-align:center;padding:40px">
      <h3>Not sure how your salary structure is classified?</h3><p style="margin:12px 0 22px">Our team can review your pay components and PF position and give a tailored proposal within 4 working hours.</p>
      <a href="/#contact" class="btn btn-primary">Request Free Consultation →</a></div></div></section>"""
    post_ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["h1"], "description": p["desc"],
               "image": f"{BASE}/blog/images/{p['image']}.png", "datePublished": p["date"], "dateModified": p["date"],
               "mainEntityOfPage": BASE + path, "inLanguage": "en-IN", "author": ORG, "publisher": ORG,
               "articleSection": p["cat"]}
    write(f"blog/{p['slug']}/index.html", shell(p["title"], p["desc"], path, [post_ld], p["h1"], esc(p["desc"]),
          [("Home", "/"), ("Blog", "/blog/"), (p["h1"], path)], main, f"/blog/images/{p['image']}.png", "article", meta))
    PUBLISHED.append(path)

# ---------- index ----------
cards = "\n        ".join(card_html(p) for p in POSTS)
index_main = f"""  <section class="section">
    <div class="container">
      <div class="blog-grid">
        {cards}
      </div>
    </div>
  </section>"""
blog_ld = {"@context": "https://schema.org", "@type": "Blog", "name": "TeamIndia Compliance Blog", "url": BASE + "/blog/",
           "publisher": ORG, "inLanguage": "en-IN",
           "blogPost": [{"@type": "BlogPosting", "headline": p["h1"], "url": f"{BASE}/blog/{p['slug']}/", "datePublished": p["date"]} for p in POSTS]}
write("blog/index.html", shell("Compliance Blog: EPF, Payroll & Labour Law Updates | TeamIndia Compliance",
      "Practical blog posts on EPF, payroll, wages and India's Labour Codes for employers, from the TeamIndia Compliance team.",
      "/blog/", [blog_ld], "Compliance Blog for Employers",
      "Practical, sourced posts on EPF, payroll, wages and India's Labour Codes.", [("Home", "/"), ("Blog", "/blog/")], index_main))

# ---------- CSS ----------
css = read("style.css")
if "/* === BLOG === */" not in css:
    css += """
/* === BLOG === */
.blog-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }
.post-card { display: flex; flex-direction: column; background: #fff; border: 1px solid var(--border); border-radius: 18px; overflow: hidden; box-shadow: var(--shadow-sm); transition: transform .15s ease, box-shadow .15s ease; }
.post-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); }
.post-card img { width: 100%; height: auto; aspect-ratio: 1200 / 630; display: block; }
.post-card-body { padding: 24px; display: flex; flex-direction: column; gap: 10px; flex: 1; }
.post-card h3 { font-size: 20px; line-height: 1.25; }
.post-card p { font-size: 14px; line-height: 1.6; }
.post-card-meta { margin-top: auto; font-size: 13px; color: var(--muted); font-weight: 500; }
.post-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 18px; margin-top: 20px; font-size: 14px; color: var(--muted); }
.post-hero { width: 100%; height: auto; aspect-ratio: 1200 / 630; border-radius: 18px; box-shadow: var(--shadow-md); margin-bottom: 48px; display: block; }
.tbl { overflow-x: auto; margin: 0 0 20px; border: 1px solid var(--border); border-radius: 12px; }
.tbl table { width: 100%; border-collapse: collapse; font-size: 15px; }
.tbl th { background: var(--bg-light); color: var(--navy); text-align: left; }
.tbl th, .tbl td { padding: 12px 16px; border-bottom: 1px solid var(--border); vertical-align: top; }
.tbl tr:last-child td { border-bottom: none; }
.related-reading { margin-top: 8px; }
@media (max-width: 980px) { .blog-grid { grid-template-columns: 1fr; } }
"""
    write("style.css", css)

# ---------- footer + blog links on every existing page ----------
FOOT_RE = re.compile(r"<!-- FOOTER -->.*?</footer>", re.S)
for f in glob.glob("**/index.html", recursive=True) + ["index.html", "404.html"]:
    if f.startswith("blog/") or not os.path.exists(f): continue
    s = read(f)
    if "<!-- FOOTER -->" in s:
        s = FOOT_RE.sub(lambda m: FOOTER, s, count=1)
    write(f, s)

# ---------- related reading on service pages ----------
RELATED = {"epf-registration": [0, 4], "payroll-processing": [1, 2], "statutory-audit": [3, 0], "hr-consultancy": [2, 3], "government-liaisoning": [0, 3]}
for svc, idx in RELATED.items():
    f = f"services/{svc}/index.html"
    s = read(f)
    s = re.sub(r"<!-- related-reading -->.*?<!-- /related-reading -->\s*", "", s, flags=re.S)
    items = "".join(f'<li><a href="/blog/{POSTS[i]["slug"]}/">{esc(POSTS[i]["h1"])}</a></li>' for i in idx)
    block = f'<!-- related-reading --><h2>Related reading</h2>\n        <ul class="related-reading">{items}</ul>\n        <!-- /related-reading -->'
    marker = "<h2>Frequently asked questions</h2>"
    assert marker in s, f
    write(f, s.replace(marker, block + marker, 1))

# ---------- home page: Insights section ----------
s = read("index.html")
s = re.sub(r"<!-- INSIGHTS -->.*?<!-- /INSIGHTS -->\s*", "", s, flags=re.S)
home_cards = "\n        ".join(card_html(p) for p in POSTS[:3])
ins = f"""<!-- INSIGHTS -->
  <section class="section services" id="blog">
    <div class="container">
      <div class="section-head">
        <span class="eyebrow">Our Blog</span>
        <h2>Compliance Blog for Employers</h2>
        <p>Practical, sourced posts on EPF, payroll, wages and India's Labour Codes.</p>
      </div>
      <div class="blog-grid">
        {home_cards}
      </div>
      <p style="text-align:center;margin-top:32px"><a href="/blog/" class="btn btn-secondary">View all blog posts →</a></p>
    </div>
  </section>
  <!-- /INSIGHTS -->

  """
assert "<!-- INQUIRY -->" in s
write("index.html", s.replace("<!-- INQUIRY -->", ins + "<!-- INQUIRY -->", 1))

# ---------- sitemap ----------
sm = read("sitemap.xml")
sm = re.sub(r"  <url><loc>[^<]*/blog/[^<]*</loc>.*?</url>\n", "", sm)
newest = max(p["date"] for p in POSTS)
entries = "".join(f"  <url><loc>{BASE}/blog/</loc><lastmod>{newest}</lastmod></url>\n" for _ in [0])
entries += "".join(f"  <url><loc>{BASE}/blog/{p['slug']}/</loc><lastmod>{p['date']}</lastmod></url>\n" for p in POSTS)
write("sitemap.xml", sm.replace("</urlset>", entries + "</urlset>"))
print("posts:", len(POSTS))
