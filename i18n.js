const translations = {
  en: { watch: "Watch Now" },
  fr: { watch: "Regarder" },
  ar: { watch: "شاهد الآن" }
};

let currentLang = "en";

function t(key) {
  return translations[currentLang][key] || key;
}

document.getElementById("languageSwitcher").addEventListener("change", e => {
  currentLang = e.target.value;
  renderMovies(window.currentMovies || []);
});
