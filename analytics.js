/* Google Analytics 4 (loaded directly) + click events. GA_ID is set in tools/build_pages.py. */
(function () {
  var ID = "G-JQ8XQKVY7J";
  window.dataLayer = window.dataLayer || [];
  if (ID) {
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", ID);
    var s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(ID); document.head.appendChild(s);
  }
  function ev(name, data) { if (window.gtag) window.gtag("event", name, data || {}); }
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]"); if (!a) return;
    var h = a.getAttribute("href") || "";
    if (h.indexOf("tel:") === 0) ev("phone_click", { link_url: h });
    else if (h.indexOf("mailto:") === 0) ev("email_click", { link_url: h });
  }, true);
})();
