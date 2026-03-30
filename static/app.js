// Minimal JS: mobile nav toggle (keeps frontend dependencies at zero).
(function () {
  const toggle = document.querySelector("[data-nav-toggle]");
  const menu = document.querySelector("[data-nav-menu]");
  if (!toggle || !menu) return;

  const setExpanded = (open) => {
    toggle.setAttribute("aria-expanded", String(open));
    menu.dataset.open = String(open);
  };

  setExpanded(false);

  toggle.addEventListener("click", () => {
    const isOpen = toggle.getAttribute("aria-expanded") === "true";
    setExpanded(!isOpen);
  });

  // Close nav on link click (mobile).
  menu.addEventListener("click", (e) => {
    const target = e.target;
    if (target && target.closest && target.closest("a")) setExpanded(false);
  });
})();

