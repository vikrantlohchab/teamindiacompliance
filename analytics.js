/* Google Analytics 4. Set GA_ID in tools/build_pages.py and rebuild. Empty ID = off. */
(function () {
  var ID = "";
  if (!ID) return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag("js", new Date());
  window.gtag("config", ID, { anonymize_ip: true });
  var s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(ID); document.head.appendChild(s);
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]"); if (!a) return;
    var h = a.getAttribute("href") || "";
    if (h.indexOf("tel:") === 0) window.gtag("event", "phone_click", { link_url: h });
    else if (h.indexOf("mailto:") === 0) window.gtag("event", "email_click", { link_url: h });
  }, true);
})();
