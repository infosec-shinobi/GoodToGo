(() => {
  const root = document.documentElement;
  const validModes = new Set(["system", "light", "dark"]);
  const validSchemes = new Set(["ocean", "forest", "ember", "plum", "slate"]);
  const mode = localStorage.getItem("fr-theme-mode") || "system";
  const scheme = localStorage.getItem("fr-color-scheme") || "ocean";
  root.dataset.theme = validModes.has(mode) ? mode : "system";
  root.dataset.scheme = validSchemes.has(scheme) ? scheme : "ocean";
})();

