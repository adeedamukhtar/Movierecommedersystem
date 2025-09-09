import streamlit as st
import pandas as pd
import pickle
import requests


st.set_page_config(page_title="Movie Recommender", layout="wide")

TMDB_API_KEY = "162f03c188742665eae5f4f512b1ebad"  # Replace with your actual TMDB API key



@st.cache_data
def load_movies():
    """Load movies dataframe from pickle file"""
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    return pd.DataFrame(movies_dict)


def fetch_poster(movie_title):
    """Fetch movie poster using TMDB API"""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={'162f03c188742665eae5f4f512b1ebad'}&query={movie_title}"
    response = requests.get(url).json()
    if response.get('results') and len(response['results']) > 0:
        poster_path = response['results'][0]['poster_path']
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return "https://via.placeholder.com/500x750?text=No+Image"


@st.cache_data
def recommend_movies(movie_title, movies_df, similarity_matrix):
    """Recommend movies based on similarity matrix"""
    if movie_title not in movies_df['title'].values:
        return []
    index = movies_df[movies_df['title'] == movie_title].index[0]
    distances = similarity_matrix[index]
    recommended_indices = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = []
    for i in recommended_indices:
        title = movies_df.iloc[i[0]].title
        recommended_movies.append({
            "title": title,
            "poster_url": fetch_poster(title)
        })
    return recommended_movies



movies = load_movies()


similarity = pickle.load(open('similarity.pkl', 'rb'))


st.sidebar.header("🎛 Filters")
genre = st.sidebar.selectbox("Choose Genre", ["All", "Action", "Comedy", "Drama", "Sci-Fi"])
st.sidebar.markdown("---")
st.sidebar.write("Built with using Streamlit")



st.title("Movie Recommendation System")

# Movie selection dropdown
selected_movie = st.selectbox(
    'Search for a movie to get recommendations:',
    movies['title'].values  # <-- FIXED: Use .values not .value
)

# Recommendation button
if st.button("Show Recommendations"):
    st.subheader(f"Recommended Movies for: **{selected_movie}**")

    recommendations = recommend_movies(selected_movie, movies, similarity)

    if recommendations:
        cols = st.columns(5)
        for idx, movie in enumerate(recommendations):
            with cols[idx % 5]:
                st.image(movie['poster_url'], use_container_width=True)
                st.caption(movie['title'])
    else:
        st.warning("No recommendations found for this movie.")


st.subheader("Filtered Movies")
filtered_movies = movies.copy()

# Apply genre filter
if genre != "All" and 'genres' in filtered_movies.columns:
    filtered_movies = filtered_movies[filtered_movies['genres'].str.contains(genre, na=False)]


# Display filtered movies in grid layout
if not filtered_movies.empty:
    cols = st.columns(5)
    for idx, row in filtered_movies.head(20).iterrows():
        with cols[idx % 5]:
            st.image(fetch_poster(row['title']), use_container_width=True)
            st.caption(f"{row['title']} ({row.get('release_year', 'N/A')})")
else:
    st.info("No movies match the selected filters.")
