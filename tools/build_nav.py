"""Replace the site header with the v2 nav (dropdowns + mobile menu) on every page. Idempotent. Stdlib only.
build_blog.py / build_pages.py read the nav from services/epf-registration/index.html, so run this first when changing the nav."""
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
SERVICES = {
  "Registrations & Licences": [("epf-registration", "EPF Registration"), ("esic-registration", "ESIC Registration"), ("shops-establishment-registration", "Shops & Establishments"), ("factory-license", "Factory Licence"), ("labour-license-clra", "Labour Licence (CLRA)"), ("multi-state-setup", "Multi-State Setup")],
  "Payroll & Advisory": [("payroll-processing", "Payroll Processing"), ("hr-consultancy", "HR Consultancy"), ("government-liaisoning", "Government Liaisoning")],
  "Audits": [("hr-compliance-audit", "HR Compliance Audit"), ("payroll-audit", "Payroll Audit"), ("contractor-compliance-audit", "Contractor Compliance Audit"), ("statutory-audit", "Statutory Audits")],
}
LOCS = [("delhi-ncr", "Delhi NCR"), ("delhi", "Delhi"), ("gurugram", "Gurugram"), ("noida", "Noida"), ("faridabad", "Faridabad"), ("manesar", "Manesar"), ("haryana", "Haryana")]
def dd(label, inner, wide=False):
    return f'<li class="has-dd"><button type="button" class="dd-btn" aria-expanded="false" aria-haspopup="true">{label}</button><div class="dd{" wide" if wide else ""}">{inner}</div></li>'
svc = "".join(f'<div><h5>{g}</h5>' + "".join(f'<a href="/services/{s}/">{n}</a>' for s, n in items) + "</div>" for g, items in SERVICES.items())
loc = "".join(f'<a href="/locations/{s}/">{n}</a>' for s, n in LOCS) + '<a href="/locations/"><b>All locations →</b></a>'
res = '<a href="/blog/">Blog</a><a href="/compliance-score/">Check Your Compliance Score</a><a href="/resources/">Guides</a>'
NAV = f'''<nav class="top nav-v2" aria-label="Main">
    <div class="nav-inner">
      <a class="logo" href="/" aria-label="TeamIndia Compliance, go to homepage">
        <div class="logo-mark">
          <img src="/tic-logo.jpeg" alt="TeamIndia Compliance logo" onerror="this.style.display='none'">
        </div>
        <div class="logo-text">TeamIndia Compliance</div>
      </a>
      <ul class="nav-links" id="nav-menu">
        <li><a href="/#about">About</a></li>
        {dd("Services", svc, True)}
        {dd("Locations", loc)}
        {dd("Resources", res)}
        <li class="nav-mobile-only"><a href="tel:+918683852482">📞 +91 86838 52482</a></li>
      </ul>
      <div class="nav-cta">
        <a class="nav-phone" href="tel:+918683852482">📞 +91 86838 52482</a>
        <a href="/#contact" class="btn btn-primary" data-cta="nav-consult" style="padding: 12px 20px; font-size: 14px;">Free Consultation</a>
      </div>
      <button type="button" class="nav-burger" aria-label="Open menu" aria-expanded="false" aria-controls="nav-menu"><span></span><span></span><span></span></button>
    </div>
  </nav>'''
pat = re.compile(r'<nav class="top">.*?</nav>', re.S)
n = 0
for f in glob.glob("**/*.html", recursive=True):
    if f.startswith(("tic-logo", "tools/")): continue
    s = open(f, encoding="utf-8").read()
    if "nav-v2" in s or '<nav class="top">' not in s: continue
    open(f, "w", encoding="utf-8").write(pat.sub(lambda m: NAV, s, count=1)); n += 1
print("nav updated on", n, "pages")
