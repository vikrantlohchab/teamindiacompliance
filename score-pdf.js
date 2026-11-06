/* Builds the TCI report as a vector PDF (jsPDF). Loaded on demand by score.js.
   window.TCIPDF.build(data, jsPDF) -> jsPDF document.  Standard PDF fonts have no ₹, so text is sanitised. */
(function () {
  var NAVY = [10, 36, 99], SAFFRON = [232, 119, 34], GREEN = [19, 104, 30], MUTED = [107, 114, 128], LINE = [229, 231, 235], LIGHT = [248, 249, 250];
  var SEGCOL = [[214, 69, 51], [240, 138, 36], [245, 197, 24], [139, 195, 74], [46, 158, 63]];
  var STATUS = [{ t: "Implemented", c: [19, 104, 30] }, { t: "Partial", c: [138, 97, 0] }, { t: "Not implemented", c: [180, 35, 24] }, { t: "Not sure", c: [75, 85, 99] }];

  function clean(s) {
    return String(s == null ? "" : s).replace(/₹/g, "Rs. ").replace(/→/g, "->").replace(/[“”]/g, '"').replace(/[‘’]/g, "'")
      .replace(/[^\x20-\x7E -ÿ–—]/g, "").replace(/\s+/g, " ").trim();
  }
  function build(d, JsPDF) {
    var doc = new JsPDF({ unit: "mm", format: "a4", compress: true });
    var W = 210, H = 297, M = 15, CW = W - 2 * M, y = 0;
    var T = function (s, x, yy, o) { doc.text(clean(s), x, yy, o || {}); };
    function color(c, kind) { (kind === "fill" ? doc.setFillColor : kind === "draw" ? doc.setDrawColor : doc.setTextColor).apply(doc, c); }
    function font(size, bold, c) { doc.setFont("helvetica", bold ? "bold" : "normal"); doc.setFontSize(size); color(c || [26, 26, 26]); }
    function ensure(h) { if (y + h > H - 20) { doc.addPage(); y = M; } }
    function wrap(s, w) { return doc.splitTextToSize(clean(s), w); }

    // header
    color(NAVY, "fill"); doc.rect(0, 0, W, 28, "F");
    font(18, true, [255, 255, 255]); T("TeamIndia Compliance", M, 13);
    font(9.5, false, [214, 222, 245]); T("TeamIndia Compliance Index (TCI)  |  Preliminary Self-Assessment Report", M, 20);
    color(SAFFRON, "fill"); doc.rect(0, 28, W / 3, 1.6, "F"); color([229, 231, 235], "fill"); doc.rect(W / 3, 28, W / 3, 1.6, "F"); color(GREEN, "fill"); doc.rect(2 * W / 3, 28, W / 3, 1.6, "F");
    y = 38;

    // meta
    var i = d.info, meta = [["COMPANY", i.company], ["PREPARED FOR", i.name], ["CITY / STATE", i.city]];
    if (i.industry) meta.push(["INDUSTRY", i.industry]); if (i.size) meta.push(["EMPLOYEES", i.size]); meta.push(["DATE", d.date]);
    meta.forEach(function (m, k) {
      var cx = M + (k % 3) * (CW / 3), cy = y + Math.floor(k / 3) * 13;
      font(7, true, MUTED); T(m[0], cx, cy); font(10, false); var l = wrap(m[1], CW / 3 - 4); T(l[0] || "", cx, cy + 5);
    });
    y += Math.ceil(meta.length / 3) * 13 + 4;

    // score card
    color(LIGHT, "fill"); doc.roundedRect(M, y, CW, 86, 4, 4, "F");
    var cx = W / 2, cy = y + 48, R = 40, r = 26, seg = 36;
    for (var s = 0; s < 5; s++) {
      var a0 = 180 - seg * s - 0.8, a1 = 180 - seg * (s + 1) + 0.8, pts = [], n = 14, k;
      for (k = 0; k <= n; k++) { var a = (a0 + (a1 - a0) * k / n) * Math.PI / 180; pts.push([cx + R * Math.cos(a), cy - R * Math.sin(a)]); }
      for (k = n; k >= 0; k--) { var b = (a0 + (a1 - a0) * k / n) * Math.PI / 180; pts.push([cx + r * Math.cos(b), cy - r * Math.sin(b)]); }
      var rel = []; for (k = 1; k < pts.length; k++) rel.push([pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]]);
      color(SEGCOL[s], "fill"); doc.lines(rel, pts[0][0], pts[0][1], [1, 1], "F", true);
    }
    var ang = (180 - 180 * d.pos / 5) * Math.PI / 180, tip = [cx + (R - 4) * Math.cos(ang), cy - (R - 4) * Math.sin(ang)], pa = ang + Math.PI / 2;
    color(NAVY, "fill"); doc.triangle(tip[0], tip[1], cx + 1.8 * Math.cos(pa), cy - 1.8 * Math.sin(pa), cx - 1.8 * Math.cos(pa), cy + 1.8 * Math.sin(pa), "F");
    doc.circle(cx, cy, 3.4, "F"); color([255, 255, 255], "fill"); doc.circle(cx, cy, 1.4, "F");
    font(26, true, NAVY); T(String(d.score), cx, cy + 14, { align: "center" });
    font(7.5, true, MUTED); T("OUT OF 100", cx, cy + 18.5, { align: "center" });
    var bc = SEGCOL[d.bandIdx]; color(bc, "fill"); var bw = doc.getTextWidth(clean(d.band.name)) + 10; doc.roundedRect(cx - bw / 2, cy + 21, bw, 6, 3, 3, "F");
    font(9, true, [255, 255, 255]); T(d.band.name, cx, cy + 25.3, { align: "center" });
    font(8.5, false, MUTED); var bl = wrap(d.band.text, CW - 30); T(bl[0] || "", cx, cy + 31.5, { align: "center" });
    y += 86 + 8;

    // areas
    font(13, true, NAVY); T("Score by area", M, y); y += 6;
    d.areas.forEach(function (a, k) {
      var col = k % 2, cx2 = M + col * (CW / 2 + 3), w = CW / 2 - 3;
      if (col === 0 && k > 0) y += 10;
      font(9, false); T(a.name, cx2, y); font(9, true); T(a.pct + "%", cx2 + w, y, { align: "right" });
      color([236, 239, 242], "fill"); doc.roundedRect(cx2, y + 1.8, w, 2.6, 1.3, 1.3, "F");
      color(a.pct >= 80 ? [19, 104, 30] : a.pct >= 50 ? [232, 163, 23] : [198, 40, 40], "fill"); if (a.pct > 0) doc.roundedRect(cx2, y + 1.8, Math.max(2.6, w * a.pct / 100), 2.6, 1.3, 1.3, "F");
    });
    y += 16;

    // answers
    ensure(30); font(13, true, NAVY); T("Your answers", M, y); y += 5;
    d.questions.forEach(function (q, k) {
      var lines = wrap(q.q, CW - 52), h = lines.length * 4.2 + 5;
      ensure(h); color(LINE, "draw"); doc.setLineWidth(0.2); doc.line(M, y + h - 1.5, M + CW, y + h - 1.5);
      font(9, true, GREEN); T(String(k + 1).padStart(2, "0"), M, y + 3.5);
      font(8.8, false); doc.text(lines, M + 9, y + 3.5);
      var st = STATUS[d.answers[k]]; font(8.5, true, st.c); T(st.t, M + CW, y + 3.5, { align: "right" });
      y += h;
    });
    y += 6;

    // actions
    ensure(30); font(13, true, NAVY); T("Priority actions", M, y); y += 6;
    if (!d.gaps.length) { font(9.5, false); T("No gaps flagged in this self-assessment. Keep your records and calendar current.", M, y); y += 8; }
    d.gaps.forEach(function (g, k) {
      var fix = (g.a === 3 ? "Verify your current position first. " : "") + g.fix, lines = wrap(fix, CW - 10), h = lines.length * 4.2 + 12;
      ensure(h); color(SAFFRON, "fill"); doc.rect(M, y, 1.2, h - 3, "F");
      font(9.5, true, NAVY); T((k + 1) + ". " + g.area, M + 4, y + 4); var st2 = STATUS[g.a]; font(8.5, true, st2.c); T(st2.t, M + CW, y + 4, { align: "right" });
      font(8.8, false, [60, 66, 75]); doc.text(lines, M + 4, y + 9); y += h;
    });

    // note + CTA
    y += 2; var note = wrap("About this report. This is a preliminary, indicative score based only on your own answers. It is not a legal opinion or an audit. \"Not sure\" is scored as 0. For a verified, in-depth analysis, contact TeamIndia Compliance.", CW - 8);
    ensure(note.length * 4 + 30); color(LIGHT, "fill"); doc.roundedRect(M, y, CW, note.length * 4 + 6, 2, 2, "F"); font(8.3, false, MUTED); doc.text(note, M + 4, y + 5.5); y += note.length * 4 + 10;
    color(NAVY, "fill"); doc.roundedRect(M, y, CW, 20, 3, 3, "F");
    font(11.5, true, [255, 255, 255]); T("Want a detailed, in-depth report?", M + 6, y + 8); font(9, false, [214, 222, 245]);
    T("Talk to TeamIndia Compliance: +91 86838 52482  |  support@teamindiacompliance.com", M + 6, y + 14.5);

    // footer on every page
    var n = doc.internal.getNumberOfPages();
    for (var p = 1; p <= n; p++) {
      doc.setPage(p); color(LINE, "draw"); doc.line(M, H - 13, W - M, H - 13);
      font(7.5, false, MUTED); T("TeamIndia Compliance  |  teamindiacompliance.com  |  Preliminary self-assessment, not a legal opinion", M, H - 8.5); T("Page " + p + " of " + n, W - M, H - 8.5, { align: "right" });
    }
    return doc;
  }
  window.TCIPDF = { build: build };
})();
