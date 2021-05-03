import requests

MOVIE_DB_API = "6aad8338c40d320050e9c17f7f2963c9"
MOVIE_DB_SEARCH = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_REQUEST = "https://api.themoviedb.org/3/movie/"


def get_candidates(query):
    parameters = {
        "api_key": MOVIE_DB_API,
        "query": query
    }
    response = requests.get(url=MOVIE_DB_SEARCH, params=parameters)
    response.raise_for_status()
    return response.json()['results']


def get_movie_data(movie_api_id):
    movie_api_url = f"{MOVIE_DB_REQUEST}/{movie_api_id}"
    response = requests.get(movie_api_url, params={"api_key": MOVIE_DB_API, "language": "en-US"})
    return response.json()



