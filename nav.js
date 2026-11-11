/* Header: dropdowns (click/keyboard) + mobile menu. Hover is handled in CSS on desktop. */
(function () {
  var nav = document.querySelector("nav.top"); if (!nav) return;
  var burger = nav.querySelector(".nav-burger"), menu = nav.querySelector(".nav-links");
  function closeDD() { nav.querySelectorAll(".has-dd.open").forEach(function (li) { li.classList.remove("open"); li.firstElementChild.setAttribute("aria-expanded", "false"); }); }
  function closeAll() { closeDD(); menu.classList.remove("open"); burger.setAttribute("aria-expanded", "false"); burger.setAttribute("aria-label", "Open menu"); }
  burger.addEventListener("click", function (e) {
    var o = menu.classList.toggle("open"); burger.setAttribute("aria-expanded", String(o)); burger.setAttribute("aria-label", o ? "Close menu" : "Open menu"); e.stopPropagation();
  });
  nav.querySelectorAll(".dd-btn").forEach(function (b) {
    b.addEventListener("click", function (e) {
      var li = b.parentNode, wasOpen = li.classList.contains("open"); closeDD();
      if (!wasOpen) { li.classList.add("open"); b.setAttribute("aria-expanded", "true"); }
      e.stopPropagation();
    });
  });
  menu.addEventListener("click", function (e) { if (e.target.closest("a")) closeAll(); });
  document.addEventListener("click", function (e) { if (!nav.contains(e.target)) closeAll(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeAll(); });
})();
