import streamlit as st
import pandas as pd
import pickle
import requests

# ============================
# Configuration
# ============================
st.set_page_config(
    page_title="Movie Recommender",
    layout="wide"
)

TMDB_API_KEY = "69fbbdd7fcf888e53f5563584d69f5b6"
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
FALLBACK_POSTER = "https://via.placeholder.com/300x450?text=No+Poster"


# ============================
# TMDB Poster Fetcher
# ============================
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id: int) -> str:
    """
    Fetch movie poster from TMDB.
    Returns a fallback image if API fails or poster is missing.
    """
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/{movie_id}",
            params={
                "api_key": TMDB_API_KEY,
                "language": "en-US"
            },
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")
        if poster_path:
            return POSTER_BASE_URL + poster_path

        return FALLBACK_POSTER

    except requests.exceptions.RequestException:
        return FALLBACK_POSTER


# ============================
# Recommendation Logic 
# ============================
def recommend(movie: str):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for idx, _ in movies_list:
        movie_id = movies.iloc[idx].movie_id
        recommended_movies.append(movies.iloc[idx].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


# ============================
# Load Data
# ============================
@st.cache_data(show_spinner=False)
def load_data():
    similarity_matrix = pickle.load(open("similarity.pkl", "rb"))
    movies_df = pd.DataFrame(
        pickle.load(open("movies.pkl", "rb"))
    )
    return similarity_matrix, movies_df


similarity, movies = load_data()


# ============================
# UI
# ============================
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox(
    "Select a movie",
    movies["title"].values
)

if st.button("Recommend"):
    movie_names, movie_posters = recommend(selected_movie)

    columns = st.columns(5)
    for col, name, poster in zip(columns, movie_names, movie_posters):
        with col:
            st.subheader(name)
            st.image(poster, use_container_width=True)
