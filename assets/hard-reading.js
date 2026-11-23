(() => {
  function openSubject() {
    const section = document.getElementById(location.hash.slice(1));
    const details = section && section.querySelector("details");
    if (details) details.open = true;
  }
  window.addEventListener("hashchange", openSubject);
  openSubject();
})();
