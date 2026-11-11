"""Home page sections (hero v2, announcement bar, problem/solution, 4 pillars, Labour Codes timeline,
coverage cards, process, simplified contact form). Idempotent: each block is replaced between markers.
Run after build_nav.py / build_pages.py:  python3 tools/build_home.py
"""
import math, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
s = open("index.html", encoding="utf-8").read()
CEIL = "/blog/epf-wage-ceiling-raised-to-25000-what-employers-must-do/"
WA = "918683852482"

def region(start, end, new, keep_end=True):
    """Replace everything from `start` up to (not including) `end` with `new`."""
    global s
    i = s.index(start); j = s.index(end, i)
    s = s[:i] + new + s[j:]

def block(name, html, before):
    """Insert or replace <!-- NAME -->...<!-- /NAME --> right before the `before` marker."""
    global s
    s = re.sub(rf"<!-- {name} -->.*?<!-- /{name} -->\s*", "", s, flags=re.S)
    s = s.replace(before, f"<!-- {name} -->\n  {html}\n  <!-- /{name} -->\n\n  " + before, 1)

# ---------- static sample gauge for the hero card ----------
def pt(r, deg): a = math.radians(deg); return (150 + r * math.cos(a), 150 - r * math.sin(a))
COL = ["#D64533", "#F08A24", "#F5C518", "#8BC34A", "#2E9E3F"]
paths = ""
for i, c in enumerate(COL):
    a0, a1 = 180 - 36 * i - 1.2, 180 - 36 * (i + 1) + 1.2
    o0, o1, i1, i0 = pt(130, a0), pt(130, a1), pt(86, a1), pt(86, a0)
    paths += f'<path d="M{o0[0]:.1f},{o0[1]:.1f} A130 130 0 0 1 {o1[0]:.1f},{o1[1]:.1f} L{i1[0]:.1f},{i1[1]:.1f} A86 86 0 0 0 {i0[0]:.1f},{i0[1]:.1f}Z" fill="{c}"/>'
rot = -90 + 180 * 2.26 / 5   # sample score 72 -> Satisfactory
GAUGE = (f'<svg viewBox="0 0 300 178" aria-hidden="true">{paths}<g style="transform-origin:150px 150px;transform:rotate({rot:.1f}deg)">'
         '<path d="M144 150 L150 38 L156 150Z" fill="#0A2463"/></g><circle cx="150" cy="150" r="17" fill="#0A2463"/><circle cx="150" cy="150" r="7" fill="#fff"/></svg>')

# ---------- 1. announcement bar (home only) ----------
s = re.sub(r"<!-- ANNC -->.*?<!-- /ANNC -->\s*", "", s, flags=re.S)
s = s.replace("<!-- NAV -->", f'''<!-- ANNC -->
  <div class="annc"><a href="{CEIL}" data-cta="annc-ceiling"><b>New:</b> the PF wage ceiling is now ₹25,000 (from 17 September 2026). See what changes for your payroll →</a></div>
  <!-- /ANNC -->

  <!-- NAV -->''', 1)

# ---------- 2. hero v2 ----------
HERO = f'''<!-- HERO -->
  <section class="hero" id="home">
    <div class="container hero-grid">
      <div>
        <span class="tag-pill">Trusted by 500+ Businesses Across India</span>
        <h1>End-to-End Labour Law &amp; HR Compliance, <span class="accent">Simplified.</span></h1>
        <p class="lead">From EPF &amp; ESIC registrations to payroll, factory licenses, and government liaisoning — TeamIndia Compliance handles every regulatory requirement so you can focus on growing your business. Headquartered in Gurugram, we serve Delhi NCR, Haryana and businesses across India.</p>
        <div class="hero-ctas">
          <a href="#contact" class="btn btn-primary" data-cta="hero-consult">Request Free Consultation →</a>
          <a href="/compliance-score/" class="btn btn-secondary" data-cta="hero-score">Check Your Compliance Score</a>
        </div>
        <div class="trust-row">
          <span>✓ Pan-India Coverage</span>
          <span>✓ 30+ Years Experience</span>
          <span>✓ Free 3-minute Compliance Check</span>
        </div>
      </div>
      <a class="tci-card" href="/compliance-score/" data-cta="hero-tci-card" aria-label="Take the free compliance self-assessment">
        <span class="tci-label">Sample TCI report</span>
        <div class="tci-gauge">{GAUGE}</div>
        <div class="tci-score"><b>72</b><small>out of 100</small></div>
        <span class="tci-band">Satisfactory</span>
        <div class="tci-bars">
          <div><span>Wages &amp; payroll</span><i style="--w:80%"></i></div>
          <div><span>EPF &amp; ESIC</span><i style="--w:60%"></i></div>
          <div><span>Contractor compliance</span><i style="--w:50%"></i></div>
        </div>
        <span class="tci-cta">Get your own score in 3 minutes →</span>
      </a>
    </div>
  </section>

  '''
region("<!-- HERO -->", "<!-- STATS -->", HERO)

# ---------- 3. problem -> solution (before SERVICES) ----------
block("PROBLEM", '''<section class="section" id="problem">
    <div class="container">
      <div class="section-head">
        <span class="eyebrow">The Compliance Juggling Act</span>
        <h2>Compliance Shouldn't Need Five Different Consultants</h2>
        <p>Registrations, monthly filings, payroll and audits are connected. Handling them separately is how deadlines get missed.</p>
      </div>
      <div class="problem-grid">
        <div class="problem-card">
          <h3>What most employers deal with</h3>
          <ul class="x-list">
            <li>One consultant for PF and ESIC, another for licences, another for payroll</li>
            <li>Deadlines tracked in spreadsheets, and missed when staff change</li>
            <li>Notices and inspections handled by people who don't know your records</li>
            <li>Rules that keep changing, from the Labour Codes to the new ₹25,000 PF ceiling</li>
          </ul>
        </div>
        <div class="problem-card solution">
          <h3>With TeamIndia Compliance</h3>
          <ul class="check-list">
            <li>One team for registrations, filings, payroll and audits</li>
            <li>A compliance calendar with owners and due dates</li>
            <li>Representation in notices and inspections</li>
            <li>Law changes explained in plain language, as they happen</li>
          </ul>
          <a class="btn btn-primary" href="#contact" data-cta="problem-consult">Talk to a specialist →</a>
        </div>
      </div>
    </div>
  </section>''', "<!-- SERVICES -->")

# ---------- 4. four pillars (replaces the 9-card grid) ----------
def li(items): return "".join(f'<li><a href="{u}">{t}</a></li>' if u else f"<li>{t}</li>" for t, u in items)
PILLARS = [
  ("📋", "Registrations &amp; Licences", "Every registration your business needs to operate legally.", "/services/epf-registration/",
   [("EPF registration", "/services/epf-registration/"), ("ESIC registration", "/services/esic-registration/"), ("Shops &amp; Establishments", "/services/shops-establishment-registration/"),
    ("Factory licence", "/services/factory-license/"), ("Labour licence (CLRA)", "/services/labour-license-clra/"), ("Multi-state setup", "/services/multi-state-setup/")]),
  ("💰", "Payroll &amp; Contributions", "Accurate payroll and on-time statutory filings, every month.", "/services/payroll-processing/",
   [("Payroll processing", "/services/payroll-processing/"), ("EPF monthly filing", "/services/epf-registration/"), ("ESIC monthly filing", "/services/esic-registration/"),
    ("Payroll audit", "/services/payroll-audit/"), ("PF wage ceiling review", CEIL)]),
  ("🔍", "Audits &amp; Advisory", "Know where you stand, and fix it before an inspection.", "/services/hr-compliance-audit/",
   [("HR compliance audit", "/services/hr-compliance-audit/"), ("Contractor compliance audit", "/services/contractor-compliance-audit/"), ("Statutory audits", "/services/statutory-audit/"),
    ("HR consultancy", "/services/hr-consultancy/"), ("Check your compliance score", "/compliance-score/")]),
  ("🏛", "Liaisoning &amp; Inspections", "Representation when the authorities come calling.", "/services/government-liaisoning/",
   [("EPFO and ESIC notices and hearings", None), ("Labour department inspections", None), ("Factory inspectorate liaison", None), ("Appeals and tribunals", None)]),
]
cards = "".join(f'''<article class="pillar"><div class="service-icon">{ic}</div><h3>{t}</h3><p>{d}</p><ul>{li(items)}</ul><a class="learn-more" href="{u}" data-cta="pillar-{i+1}">Explore {t.split(" &amp;")[0].lower()} →</a></article>''' for i, (ic, t, d, u, items) in enumerate(PILLARS))
SERVICES = f'''<!-- SERVICES -->
  <section class="section services" id="services">
    <div class="container">
      <div class="section-head">
        <span class="eyebrow">Our Services</span>
        <h2>One Partner. Four Pillars. Complete Compliance.</h2>
        <p>We manage your compliance lifecycle, from the day you set up to the monthly filings that follow.</p>
      </div>
      <div class="pillars">{cards}</div>
    </div>
  </section>

  '''
region("<!-- SERVICES -->", "<!-- AUDITS -->", SERVICES)

# ---------- 5. Labour Codes timeline (before LOCATIONS) ----------
block("CODES", f'''<section class="section" id="labour-codes">
    <div class="container">
      <div class="section-head">
        <span class="eyebrow">Labour Codes &amp; Law Changes</span>
        <h2>What Changed in 2025–26, and What It Means for You</h2>
        <p>Three changes every employer should check against their payroll today.</p>
      </div>
      <ol class="tl">
        <li><time>21 Nov 2025</time><h3>Four Labour Codes come into force</h3><p>The Wages, Industrial Relations, Social Security and OSH Codes replace 29 central labour laws.</p><a href="/blog/payroll-ready-for-new-labour-codes-50-percent-wage-rule/" data-cta="codes-50">The 50% wage rule explained →</a></li>
        <li><time>17 Sep 2026</time><h3>PF wage ceiling raised to ₹25,000</h3><p>More employees now fall under PF, pension and EDLI cover, and contributions rise.</p><a href="{CEIL}" data-cta="codes-ceiling">What employers must do →</a></li>
        <li><time>Ongoing</time><h3>Rules are still being finalised</h3><p>Central and state rules are being notified in stages. Check the position in your state.</p><a href="/resources/labour-codes-guide-for-employers/" data-cta="codes-guide">Employer guide →</a></li>
      </ol>
      <div class="lead-band">
        <div><h3>Not sure how this affects your business?</h3><p>Get a free Labour Codes impact check from our team.</p></div>
        <a data-wa="codes-impact" data-wa-msg="Hi TeamIndia Compliance, I would like a free Labour Codes impact check for my business." href="https://wa.me/{WA}" class="btn btn-primary">💬 Get my free impact check</a>
      </div>
    </div>
  </section>''', "<!-- LOCATIONS -->")

# ---------- 6. coverage cards ----------
LOCS = [("delhi", "Delhi", "Offices, showrooms and factories across the capital: EPF, ESIC, payroll and Shops &amp; Establishments."),
        ("gurugram", "Gurugram", "Our head office. Corporate offices to Manesar manufacturers, with Haryana compliance covered."),
        ("noida", "Noida", "IT, electronics and industrial units under Uttar Pradesh law, including contract-labour compliance."),
        ("faridabad", "Faridabad", "EPF, ESIC and payroll for engineering and manufacturing MSMEs."),
        ("manesar", "Manesar", "Factory licence, contract labour and inspection support for IMT Manesar units."),
        ("haryana", "Haryana", "State-wide support, including Sonipat, Bawal, Bahadurgarh, Jhajjar and Rohtak.")]
loc_cards = "".join(f'<a class="service-card" href="/locations/{sl}/"><div class="service-icon">📍</div><h3>{n}</h3><p>{d}</p><span class="learn-more">Learn more →</span></a>' for sl, n, d in LOCS)
LOCATIONS = f'''<!-- LOCATIONS -->
  <section class="section" id="locations">
    <div class="container">
      <div class="section-head">
        <span class="eyebrow">Where We Work</span>
        <h2>Labour Law Compliance in Delhi NCR &amp; Across India</h2>
        <p>Headquartered in Gurugram, we support employers across Delhi, Haryana and Uttar Pradesh, and pan-India through our state-wise network.</p>
      </div>
      <div class="service-grid">{loc_cards}</div>
      <p style="text-align:center;margin-top:28px;font-size:15px"><a href="/locations/" style="color:var(--saffron);font-weight:600">All locations →</a> · <a href="/locations/delhi-ncr/" style="color:var(--saffron);font-weight:600">Delhi NCR</a> · <a href="/services/shops-establishment-registration/" style="color:var(--saffron);font-weight:600">Shops &amp; Establishments</a> · <a href="/resources/" style="color:var(--saffron);font-weight:600">Employer guides</a></p>
    </div>
  </section>

  '''
region("<!-- LOCATIONS -->", "<!-- INDUSTRIES -->", LOCATIONS)

# ---------- 7. process (before WHY US) ----------
steps = [("Free discovery call", "30 minutes to understand your business, locations and workforce."),
         ("Compliance review", "We check your registrations, filings and payroll, and show you the gaps."),
         ("Clear proposal", "Every registration and filing you need, with scope and pricing."),
         ("We do the work", "Registrations, filings and payroll, with regular status updates."),
         ("Ongoing compliance", "Calendar, monthly returns, notices and law-change updates.")]
block("PROCESS", '<section class="section" id="process">\n    <div class="container">\n      <div class="section-head">\n        <span class="eyebrow">How We Work</span>\n        <h2>A Simple 5-Step Process</h2>\n        <p>From first call to ongoing compliance, you always know what is happening.</p>\n      </div>\n      <ol class="steps">' +
      "".join(f"<li><span class=\"step-n\">{i+1}</span><h3>{t}</h3><p>{d}</p></li>" for i, (t, d) in enumerate(steps)) +
      '</ol>\n    </div>\n  </section>', "<!-- WHY US -->")

# ---------- 8. simplified contact form ----------
SERVICES_OPT = ["EPF Compliance", "ESIC Compliance", "Payroll Processing", "Factory Licence", "Labour Licence (CLRA)", "Shops &amp; Establishments", "HR Compliance Audit", "Payroll Audit", "Contractor Compliance Audit", "Government Liaisoning", "HR Consultancy", "Multi-State Setup", "Other / Need to discuss"]
CITIES = ["Delhi", "Gurugram", "Noida", "Faridabad", "Manesar", "Other Haryana", "Other Delhi NCR", "Other state"]
FORM = f'''<form id="inquiry-form" class="form-card" action="https://api.web3forms.com/submit" method="POST">
        <input type="hidden" name="access_key" value="6a21b648-57e9-4ea3-840d-1ac461467d14">
        <input type="hidden" name="from_name" value="TeamIndia Compliance Website">
        <input type="hidden" name="subject" value="New inquiry from TeamIndia Compliance website">
        <input type="checkbox" name="botcheck" style="display:none" tabindex="-1" autocomplete="off">

        <h3>Request Free Consultation</h3>
        <p class="sub">Tell us what you need and we'll respond within 4 working hours.</p>
        <div class="form-row">
          <div class="field"><label for="f-name">Full name / business name *</label><input id="f-name" type="text" name="name" placeholder="Rajesh Kumar" autocomplete="name" required></div>
          <div class="field"><label for="f-phone">WhatsApp number *</label><input id="f-phone" type="tel" name="phone" placeholder="+91 98765 43210" autocomplete="tel" required></div>
        </div>
        <div class="form-row">
          <div class="field"><label for="f-service">Service needed *</label><select id="f-service" name="service" required><option value="">Choose a service</option>{"".join(f"<option>{o}</option>" for o in SERVICES_OPT)}</select></div>
          <div class="field"><label for="f-city">City *</label><select id="f-city" name="city" required><option value="">Choose your city</option>{"".join(f"<option>{o}</option>" for o in CITIES)}</select></div>
        </div>
        <div class="checkbox-row">
          <input type="checkbox" id="consent" required>
          <label for="consent">I agree to TeamIndia Compliance's <a href="/privacy-policy/" target="_blank" rel="noopener" style="color:var(--saffron);font-weight:600">privacy policy</a> and consent to being contacted.</label>
        </div>
        <button type="submit" class="btn btn-primary" id="inquiry-submit" data-cta="form-submit">Submit Inquiry →</button>
        <p id="inquiry-error" class="form-error" hidden>Something went wrong. Please email us directly at <a href="mailto:support@teamindiacompliance.com">support@teamindiacompliance.com</a>.</p>
      </form>'''
s = re.sub(r'<form id="inquiry-form".*?</form>', lambda m: FORM, s, count=1, flags=re.S)

open("index.html", "w", encoding="utf-8").write(s)
print("home rebuilt")
