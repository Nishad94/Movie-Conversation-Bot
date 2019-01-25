import requests
import pprint

TMDB_API_KEY = "b468692645623d8d1a926f516015f1c1"
SEARCH_MOVIE_URL = "https://api.themoviedb.org/3/search/movie"
CREW_URL = "https://api.themoviedb.org/3/movie/{}/credits"

def getParams():
    params = {
        'api_key':TMDB_API_KEY,
        'language': 'en-US'
    }
    return params

def searchForMovie(movName):
    queryParams = getParams()
    queryParams['query'] = movName
    response = requests.request("GET", SEARCH_MOVIE_URL, params=queryParams).json()
    movie = response["results"][0]
    title = movie['original_title']
    plot = movie['overview']
    release_date = movie['release_date']
    rating = movie['vote_average']
    movie_id = movie['id']
    actors,dirs = getActorsAndDirectors(movie_id)
    result = "{} : '{}', 'Release Date' : {} , 'Directors': {}, 'Actors': {}, 'Rating': {}".format(title,plot,release_date,dirs,actors,rating)
    print "hiii\n" + result
    return result


def getActorsAndDirectors(movieId):
    queryParams = getParams()
    response = requests.request("GET", CREW_URL.format(movieId), params=queryParams).json()
    cast = response['cast']
    actors = "{} {} {}".format(cast[0]['name'], cast[1]['name'], cast[2]['name'])
    crew = response['crew']
    directors = [c['name'] for c in crew if c['job'] == 'Director']
    dirs = ""
    for d in directors:
        dirs += d + " "
    return actors,dirs
    
