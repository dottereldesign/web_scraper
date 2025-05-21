// static/scripts/theme-toggle.js
(function () {
  const btn = document.getElementById("theme-toggle-btn");
  const body = document.body;
  const THEME_KEY = "scrapegoat_theme";

  function setTheme(light) {
    if (light) {
      body.classList.add("light-mode");
      btn.textContent = "☀️";
    } else {
      body.classList.remove("light-mode");
      btn.textContent = "🌙";
    }
  }

  // Initial: check localStorage, else default to dark
  const saved = localStorage.getItem(THEME_KEY);
  setTheme(saved === "light");

  btn.onclick = function () {
    const isLight = body.classList.toggle("light-mode");
    localStorage.setItem(THEME_KEY, isLight ? "light" : "dark");
    btn.textContent = isLight ? "☀️" : "🌙";
  };
})();
