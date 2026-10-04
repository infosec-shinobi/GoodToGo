(() => {
  const root = document.documentElement;
  const status = document.getElementById("settings-status");
  const mode = root.dataset.theme || "system";
  const scheme = root.dataset.scheme || "ocean";

  const selectedMode = document.querySelector(`input[name="theme-mode"][value="${mode}"]`);
  const selectedScheme = document.querySelector(`input[name="color-scheme"][value="${scheme}"]`);
  if (selectedMode) selectedMode.checked = true;
  if (selectedScheme) selectedScheme.checked = true;

  document.querySelectorAll('input[name="theme-mode"]').forEach((input) => {
    input.addEventListener("change", () => {
      root.dataset.theme = input.value;
      localStorage.setItem("fr-theme-mode", input.value);
      status.textContent = `Display mode saved: ${input.value}.`;
    });
  });

  document.querySelectorAll('input[name="color-scheme"]').forEach((input) => {
    input.addEventListener("change", () => {
      root.dataset.scheme = input.value;
      localStorage.setItem("fr-color-scheme", input.value);
      status.textContent = `Color scheme saved: ${input.value}.`;
    });
  });
})();
