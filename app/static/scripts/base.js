document.addEventListener("DOMContentLoaded", function () {
  const wrapper = document.querySelector(".app-wrapper");
  const collapseBtn = document.getElementById("collapse-toggle");
  const STORAGE_KEY = "sidebar-collapsed";

  // Restore previous state
  if (localStorage.getItem(STORAGE_KEY) === "1") {
    wrapper.classList.add("collapsed");
  }

  // Get current route
  const currentRoute = window.location.pathname;
  console.log("Current route:", currentRoute);

  // Toggle collapse
  collapseBtn.addEventListener("click", function (e) {
    e.preventDefault();
    wrapper.classList.toggle("collapsed");
    localStorage.setItem(
      STORAGE_KEY,
      wrapper.classList.contains("collapsed") ? "1" : "0"
    );
    setupTooltips(); // re-init tooltips when state changes
  });

  // Make rows clickable (your existing code)
  document.querySelectorAll(".clickable-row").forEach((row) => {
    row.addEventListener("click", function () {
      const href = this.dataset.href;
      if (href) window.location = href;
    });
  });

  // Enable tooltips only when collapsed
  function setupTooltips() {
    const collapsed = wrapper.classList.contains("collapsed");
    document
      .querySelectorAll('.sidebar [data-bs-toggle="tooltip"]')
      .forEach((el) => {
        const inst = bootstrap.Tooltip.getInstance(el);
        if (inst) inst.dispose();
        if (collapsed) new bootstrap.Tooltip(el);
      });
  }
  setupTooltips();
});
