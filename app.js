const moviesContainer = document.getElementById("movies");
const ratingInput = document.getElementById("rating");
const ratingValue = document.getElementById("ratingValue");

ratingInput.oninput = () => {
  ratingValue.textContent = ratingInput.value;
  loadMovies();
};

function loadMovies() {
  const minRating = ratingInput.value;

  // Dummy data (سيُستبدل بالـ Backend)
  const movies = [
    { id: 1, title: "Inception", rating: 8.8, poster: "https://via.placeholder.com/300x450" },
    { id: 2, title: "Interstellar", rating: 8.6, poster: "https://via.placeholder.com/300x450" }
  ].filter(m => m.rating >= minRating);

  window.currentMovies = movies;
  renderMovies(movies);
}

function renderMovies(movies) {
  moviesContainer.innerHTML = "";

  movies.forEach(movie => {
    const div = document.createElement("div");
    div.className = "movie";

    div.innerHTML = `
      <img src="${movie.poster}">
      <div class="info">
        <h4>${movie.title}</h4>
        <p>⭐ ${movie.rating}</p>
        <button onclick="watch(${movie.id})">${t("watch")}</button>
      </div>
    `;

    moviesContainer.appendChild(div);
  });
}

function watch(id) {
  // لاحقًا → Backend Monetag Redirect
  alert("Redirect to Monetag for movie " + id);
}

loadMovies();
