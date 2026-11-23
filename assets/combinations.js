(() => {
    const select = document.getElementById("combo-topic");
    const groups = Array.from(document.querySelectorAll("[data-pairtag]"));
    const initial = new URLSearchParams(location.search).get("tag");
    if (initial && Array.from(select.options).some(option => option.value === initial)) select.value = initial;
    function show() {
      let visible = false;
      for (const group of groups) {
        group.hidden = group.dataset.pairtag !== select.value;
        if (!group.hidden) visible = true;
      }
      document.getElementById("pair-status").textContent = visible ? "" : "No 2000–3000 tag pairs in this snapshot.";
    }
    show();
    select.addEventListener("change", () => {
      show();
      try { history.replaceState(null,"","?"+new URLSearchParams({tag:select.value})); } catch (_) {}
    });
})();