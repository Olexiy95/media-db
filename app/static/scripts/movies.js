(function () {
  const input = document.querySelector('input[type="search"][name="q"]');
  if (!input) return;

  const table =
    input.closest(".card")?.querySelector("table") ||
    document.querySelector("table");
  const tbody = table.querySelector("tbody");
  const rows = Array.from(tbody.querySelectorAll("tr"));
  const movieRows = rows.filter(
    (r) => !r.classList.contains("table-secondary")
  ); // your group headers use .table-secondary
  const groupHeaders = rows.filter((r) =>
    r.classList.contains("table-secondary")
  );

  const countBadge = document.querySelector(".caption-top .badge");

  const normalize = (s) =>
    (s || "")
      .toString()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, ""); // strip accents

  function applyFilter() {
    const q = normalize(input.value.trim());
    let visible = 0;

    // filter movie rows
    movieRows.forEach((tr) => {
      const hay = normalize(tr.textContent);
      const ok = !q || hay.includes(q);
      tr.style.display = ok ? "" : "none";
      if (ok) visible++;
    });

    // show group headers only if they have at least one visible movie row until the next header
    groupHeaders.forEach((hdr, i) => {
      let any = false;
      let next = groupHeaders[i + 1] || null;
      let p = hdr.nextElementSibling;
      while (p && p !== next) {
        if (p.style.display !== "none") {
          any = true;
          break;
        }
        p = p.nextElementSibling;
      }
      hdr.style.display = any ? "" : "none";
    });

    // update badge count if present
    if (countBadge) countBadge.textContent = String(visible);
  }

  // small debounce
  let t;
  input.addEventListener("input", () => {
    clearTimeout(t);
    t = setTimeout(applyFilter, 120);
  });

  // clear on Escape, focus via Ctrl/Cmd+/
  input.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      input.value = "";
      applyFilter();
    }
  });
  window.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "/") {
      e.preventDefault();
      input.focus();
    }
  });

  // initial
  applyFilter();
})();
