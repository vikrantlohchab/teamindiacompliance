/* Click events for Google Tag Manager (the GTM container itself is inlined in each page head). */
(function () {
  window.dataLayer = window.dataLayer || [];
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]"); if (!a) return;
    var h = a.getAttribute("href") || "";
    if (h.indexOf("tel:") === 0) window.dataLayer.push({ event: "phone_click", link_url: h });
    else if (h.indexOf("mailto:") === 0) window.dataLayer.push({ event: "email_click", link_url: h });
  }, true);
})();
