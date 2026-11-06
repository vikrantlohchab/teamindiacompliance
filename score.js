/* TeamIndia Compliance Index (TCI) self-assessment. Runs entirely in the browser; nothing is sent anywhere. */
(function () {
  var root = document.getElementById("sa");
  if (!root) return;
  var WA = "918683852482";
  var OPTS = [
    { k: "yes", label: "Yes – Fully implemented", pts: 10 },
    { k: "partial", label: "Partially implemented", pts: 5 },
    { k: "no", label: "No – Not implemented", pts: 0 },
    { k: "unsure", label: "Not sure", pts: 0 }
  ];
  var Q = [
    { area: "Wages & payroll", q: "Is your salary structure aligned with applicable minimum wage requirements and statutory wage definitions?",
      fix: "Review every pay component against minimum wages and the Code on Wages definition. Excluded allowances above 50% of total pay are added back to wages.", link: ["/blog/payroll-ready-for-new-labour-codes-50-percent-wage-rule/", "Read: the 50% wage rule"] },
    { area: "Wages & payroll", q: "Are employee-wise payroll calculations, attendance, overtime and statutory deductions properly verified every month?",
      fix: "Add a monthly pre-payout checklist: attendance and overtime sign-off, deduction reconciliation, and a second-person review." },
    { area: "EPF & ESIC", q: "Are all eligible employees correctly covered under EPF, with accurate wage calculations and timely monthly contributions?",
      fix: "Check coverage of every eligible employee, including those earning up to the new ₹25,000 PF wage ceiling (from 17 September 2026), the PF wage base, and deposits by the 15th.", link: ["/blog/epf-wage-ceiling-raised-to-25000-what-employers-must-do/", "Read: the ₹25,000 PF ceiling"] },
    { area: "EPF & ESIC", q: "Are ESIC applicability, employee registrations, contribution calculations and monthly payments properly monitored?",
      fix: "Confirm applicability (10 or more employees in most states, wages up to ₹21,000), register all insured persons, and pay contributions by the 15th of the following month." },
    { area: "Registrations & licences", q: "Are all applicable labour law registrations, licences, statutory registers and returns up to date?",
      fix: "List every registration and licence (EPF, ESIC, Shops & Establishments, factory, contract labour) with expiry dates, and confirm registers and returns are current." },
    { area: "Employee benefits", q: "Are statutory employee benefits such as bonus, gratuity, maternity benefits and leave entitlements properly evaluated and administered?",
      fix: "Review bonus, gratuity, maternity and leave policies against current law. The revised wage definition now feeds gratuity calculations." },
    { area: "Contractor compliance", q: "Do you regularly verify the statutory compliance of contractors and outsourced manpower, including applicable PF and ESIC obligations?",
      fix: "Verify contractor licences, wage payment and PF/ESIC remittance every month. A principal employer can be held responsible for contractor defaults.", link: ["/services/contractor-compliance-audit/", "See: contractor compliance audit"] },
    { area: "HR records", q: "Are appointment letters, employee records, HR policies and other mandatory employment documents properly maintained?",
      fix: "Issue appointment letters to everyone, keep complete employee files, and maintain an HR policy set updated for the Labour Codes." },
    { area: "Governance & monitoring", q: "Do you conduct periodic internal HR or labour law compliance audits to identify gaps before regulatory inspections?",
      fix: "Schedule an internal or independent compliance audit at least once a year, ahead of inspections.", link: ["/services/hr-compliance-audit/", "See: HR compliance audit"] },
    { area: "Governance & monitoring", q: "Do you maintain a compliance calendar and a documented process to track statutory deadlines, changes in applicable laws and corrective actions?",
      fix: "Build a compliance calendar with owners and due dates, and a simple log for law changes and corrective actions." }
  ];
  var BANDS = [
    { min: 90, name: "Excellent", cls: "b-excellent", text: "Your compliance practices look strong. Keep records and your calendar current, and review them regularly." },
    { min: 80, name: "Good", cls: "b-good", text: "Most areas are in good shape, with a few gaps to close." },
    { min: 70, name: "Satisfactory", cls: "b-sat", text: "A reasonable base, but several areas need attention before they turn into notices." },
    { min: 60, name: "Needs Improvement", cls: "b-needs", text: "There are significant gaps. Prioritise the actions below." },
    { min: 0, name: "Critical Attention", cls: "b-critical", text: "Serious gaps are likely. We recommend an independent audit soon." }
  ];
  var INDUSTRIES = ["Manufacturing", "IT & Software", "Healthcare", "Retail & FMCG", "Logistics", "Construction", "Hospitality", "Education", "Professional services", "Other"];
  var SIZES = ["1–25 employees", "26–100 employees", "101–500 employees", "501–1000 employees", "1000+ employees"];

  var ans = [], idx = 0, info = {};
  var el = function (id) { return root.querySelector(id); };
  function push(ev, data) {
    try {
      window.dataLayer = window.dataLayer || [];
      var d = { event: ev }; for (var k in data) d[k] = data[k];
      window.dataLayer.push(d);
      if (window.gtag) window.gtag("event", ev, data || {});
    } catch (e) {}
  }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function show(id) {
    ["sa-intro", "sa-q", "sa-form", "sa-report"].forEach(function (s) { el("#" + s).hidden = s !== id; });
    var h = el("#" + id + " [data-focus]"); if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
    root.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderQ() {
    var q = Q[idx];
    el("#sa-count").textContent = "Question " + (idx + 1) + " of " + Q.length;
    el("#sa-area").textContent = q.area;
    el("#sa-bar").style.width = (idx / Q.length * 100) + "%";
    el("#sa-bar").parentNode.setAttribute("aria-valuenow", idx);
    el("#sa-qtext").textContent = q.q;
    el("#sa-opts").innerHTML = OPTS.map(function (o, i) {
      return '<button type="button" role="radio" aria-checked="' + (ans[idx] === i) + '" class="sa-opt' + (ans[idx] === i ? " on" : "") + '" data-i="' + i + '"><span class="sa-key">' + (i + 1) + "</span><span>" + o.label + "</span></button>";
    }).join("");
    el("#sa-back").style.visibility = idx === 0 ? "hidden" : "visible";
  }
  function pick(i) {
    ans[idx] = i; renderQ();
    setTimeout(function () {
      if (idx < Q.length - 1) { idx++; renderQ(); el("#sa-qtext").focus({ preventScroll: true }); } else { fillForm(); show("sa-form"); }
    }, 280);
  }
  function fillForm() {
    el("#sa-industry").innerHTML = '<option value="">Select industry</option>' + INDUSTRIES.map(function (x) { return "<option>" + x + "</option>"; }).join("");
    el("#sa-size").innerHTML = '<option value="">Select employee strength</option>' + SIZES.map(function (x) { return "<option>" + x + "</option>"; }).join("");
  }

  var SEG = [
    { name: "Critical Attention", range: "Below 60", color: "#D64533" },
    { name: "Needs Improvement", range: "60–69", color: "#F08A24" },
    { name: "Satisfactory", range: "70–79", color: "#F5C518" },
    { name: "Good", range: "80–89", color: "#8BC34A" },
    { name: "Excellent", range: "90–100", color: "#2E9E3F" }
  ];
  function gaugePos(s) {
    var idx, f;
    if (s < 60) { idx = 0; f = s / 60; }
    else if (s < 70) { idx = 1; f = (s - 60) / 10; }
    else if (s < 80) { idx = 2; f = (s - 70) / 10; }
    else if (s < 90) { idx = 3; f = (s - 80) / 10; }
    else { idx = 4; f = Math.min(1, (s - 90) / 10); }
    return idx + 0.1 + 0.8 * f; // keep the needle inside its colour band
  }
  function pt(r, deg) { var a = deg * Math.PI / 180; return [150 + r * Math.cos(a), 150 - r * Math.sin(a)]; }
  function gauge(score) {
    var R = 130, r = 86, gap = 1.2, paths = "";
    SEG.forEach(function (g, i) {
      var a0 = 180 - 36 * i - gap, a1 = 180 - 36 * (i + 1) + gap;
      var o0 = pt(R, a0), o1 = pt(R, a1), i1 = pt(r, a1), i0 = pt(r, a0);
      paths += '<path d="M' + o0 + " A" + R + " " + R + " 0 0 1 " + o1 + " L" + i1 + " A" + r + " " + r + " 0 0 0 " + i0 + ' Z" fill="' + g.color + '"/>';
    });
    var rot = -90 + 180 * gaugePos(score) / 5;
    return '<svg class="gauge" viewBox="0 0 300 178" role="img" aria-label="Score ' + score + ' out of 100">' + paths +
      '<g class="needle" style="transform-origin:150px 150px;transform:rotate(-90deg)" data-rot="' + rot.toFixed(1) + '"><path d="M144 150 L150 38 L156 150 Z" fill="#0A2463"/></g>' +
      '<circle cx="150" cy="150" r="17" fill="#0A2463"/><circle cx="150" cy="150" r="7" fill="#fff"/></svg>';
  }
  function band(score) { for (var i = 0; i < BANDS.length; i++) if (score >= BANDS[i].min) return BANDS[i]; }
  function renderReport() {
    var score = 0; ans.forEach(function (a) { score += OPTS[a].pts; });
    var b = band(score);
    var areas = {}, order = [];
    Q.forEach(function (q, i) { if (!areas[q.area]) { areas[q.area] = { p: 0, n: 0 }; order.push(q.area); } areas[q.area].p += OPTS[ans[i]].pts; areas[q.area].n += 10; });
    var gaps = Q.map(function (q, i) { return { q: q, i: i, pts: OPTS[ans[i]].pts, a: ans[i] }; }).filter(function (g) { return g.pts < 10; })
      .sort(function (x, y) { return x.pts - y.pts || x.i - y.i; });
    var d = new Date().toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" });
    var chip = function (a) { return '<span class="sa-chip c-' + OPTS[a].k + '">' + (a === 0 ? "Implemented" : a === 1 ? "Partial" : a === 2 ? "Not implemented" : "Not sure") + "</span>"; };

    el("#sa-report").innerHTML =
      '<div class="rp-head"><img src="/tic-logo.jpeg" alt="" width="44" height="44"><div><div class="rp-brand">TeamIndia Compliance</div><div class="rp-sub">TeamIndia Compliance Index (TCI) · Preliminary Self-Assessment Report</div></div></div>' +
      '<div class="rp-meta"><div><b>Company</b>' + esc(info.company) + '</div><div><b>Prepared for</b>' + esc(info.name) + '</div><div><b>City / State</b>' + esc(info.city) + '</div>' +
      (info.industry ? "<div><b>Industry</b>" + esc(info.industry) + "</div>" : "") + (info.size ? "<div><b>Employees</b>" + esc(info.size) + "</div>" : "") + "<div><b>Date</b>" + d + "</div></div>" +
      '<div class="rp-score"><div class="gauge-wrap">' + gauge(score) + '<div class="g-num"><span>' + score + '</span><small>out of 100</small></div></div>' +
      '<span class="band ' + b.cls + '">' + b.name + '</span><h3 class="rp-h">Your preliminary compliance score</h3><p>' + b.text + "</p>" +
      '<div class="g-legend">' + SEG.map(function (g) { return '<span><i style="background:' + g.color + '"></i>' + g.name + " <em>" + g.range + "</em></span>"; }).join("") + "</div></div>" +
      '<h3 class="rp-sec">Score by area</h3><div class="areas">' + order.map(function (n) { var p = Math.round(areas[n].p / areas[n].n * 100); return '<div class="area"><div class="area-top"><span>' + n + "</span><b>" + p + '%</b></div><div class="area-bar"><i class="' + (p >= 80 ? "g" : p >= 50 ? "a" : "r") + '" style="width:' + p + '%"></i></div></div>'; }).join("") + "</div>" +
      '<h3 class="rp-sec">Your answers</h3><div class="rp-table">' + Q.map(function (q, i) { return '<div class="rp-row"><span class="rp-n">' + String(i + 1).padStart(2, "0") + "</span><span>" + esc(q.q) + "</span>" + chip(ans[i]) + "</div>"; }).join("") + "</div>" +
      '<h3 class="rp-sec">Priority actions</h3>' + (gaps.length ? '<ol class="rp-actions">' + gaps.map(function (g) {
        return "<li><div class='ra-top'><b>" + g.q.area + "</b>" + chip(g.a) + "</div><p>" + (g.a === 3 ? "Verify your current position first. " : "") + g.q.fix + "</p>" + (g.q.link ? '<a href="' + g.q.link[0] + '">' + g.q.link[1] + " →</a>" : "") + "</li>"; }).join("") + "</ol>"
        : "<p>No gaps flagged in this self-assessment. Keep your records and calendar current.</p>") +
      '<div class="rp-note"><b>About this report.</b> This is a preliminary, indicative score based only on your own answers. It is not a legal opinion or an audit. “Not sure” is scored as 0. For a verified, in-depth analysis, contact TeamIndia Compliance.</div>' +
      '<div class="rp-foot">TeamIndia Compliance · teamindiacompliance.com · +91 86838 52482 · support@teamindiacompliance.com</div>' +
      '<div class="rp-cta sa-noprint"><h3>Want a detailed, in-depth report?</h3><p>A self-assessment shows the direction. Our team reviews your actual registrations, filings, payroll and contractor records and gives you a verified report with a prioritised fix plan.</p>' +
      '<div class="rp-btns"><a id="sa-wa" class="btn btn-primary" target="_blank" rel="noopener">💬 Get a detailed report on WhatsApp</a><a class="btn btn-secondary" href="/#contact">Request free consultation</a><a class="btn btn-secondary" href="tel:+918683852482">📞 +91 86838 52482</a></div>' +
      '<div class="rp-btns2"><button type="button" class="sa-link" id="sa-print">🖨 Print / Save as PDF</button><button type="button" class="sa-link" id="sa-retake">↻ Retake assessment</button></div></div>';

    var msg = "Hi TeamIndia Compliance, I scored " + score + "/100 (" + b.name + ") on the TCI self-assessment for " + info.company + " (" + info.city + "). I would like a detailed compliance report.";
    el("#sa-wa").href = "https://wa.me/" + WA + "?text=" + encodeURIComponent(msg);
    el("#sa-wa").addEventListener("click", function () { push("tci_cta_click", { channel: "whatsapp", score: score, band: b.name }); });
    el("#sa-print").addEventListener("click", function () { push("tci_print", { score: score }); window.print(); });
    el("#sa-retake").addEventListener("click", reset);
    push("tci_complete", { score: score, band: b.name, industry: info.industry || "", size: info.size || "" });
    show("sa-report");
    requestAnimationFrame(function () { setTimeout(function () { var n = el(".needle"); if (n) n.style.transform = "rotate(" + n.getAttribute("data-rot") + "deg)"; }, 80); });
  }
  function reset() { ans = []; idx = 0; info = {}; el("#sa-form form").reset(); show("sa-intro"); }

  el("#sa-start").addEventListener("click", function () { idx = 0; ans = []; renderQ(); show("sa-q"); push("tci_start", {}); });
  el("#sa-opts").addEventListener("click", function (e) { var b = e.target.closest(".sa-opt"); if (b) pick(+b.getAttribute("data-i")); });
  el("#sa-back").addEventListener("click", function () { if (idx > 0) { idx--; renderQ(); } });
  document.addEventListener("keydown", function (e) {
    if (el("#sa-q").hidden || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key >= "1" && e.key <= "4") pick(+e.key - 1);
    else if (e.key === "ArrowLeft" && idx > 0) { idx--; renderQ(); }
  });
  el("#sa-form form").addEventListener("submit", function (e) {
    e.preventDefault();
    info = { name: el("#sa-name").value.trim(), company: el("#sa-company").value.trim(), city: el("#sa-city").value.trim(), industry: el("#sa-industry").value, size: el("#sa-size").value };
    renderReport();
  });
  el("#sa-formback").addEventListener("click", function () { idx = Q.length - 1; renderQ(); show("sa-q"); });
})();
