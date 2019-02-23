import requests
import pprint
import numpy as np

TMDB_API_KEY = "b468692645623d8d1a926f516015f1c1"
SEARCH_MOVIE_URL = "https://api.themoviedb.org/3/search/movie"
CREW_URL = "https://api.themoviedb.org/3/movie/{}/credits"
PERSON_MOVIE_CREDITS_URL = "https://api.themoviedb.org/3/person/{}/movie_credits"
GET_MOVIE_BY_ID_URL = "https://api.themoviedb.org/3/movie/{}"


def getParams():
    params = {
        'api_key':TMDB_API_KEY,
        'language': 'en-US'
    }
    return params

# def compareCurrentMovieWithOthers(current_movie, overall_stats):


'''
{
    'adult': False,
    'backdrop_path': '/icmmSD4vTTDKOq2vvdulafOGw93.jpg',
    'genre_ids': [28, 878],
    'id': 603,
    'original_language': 'en',
    'original_title': 'The Matrix',
    'overview': 'Set in the 22nd century, The Matrix tells the story of a '
                'computer hacker who joins a group of underground insurgents '
                'fighting the vast and powerful computers who now rule the earth.',
    'popularity': 31.893,
    'poster_path': '/hEpWvX6Bp79eLxY1kX5ZZJcme5U.jpg',
    'release_date': '1999-03-30',
    'title': 'The Matrix',
    'video': False,
    'vote_average': 8.1,
    'vote_count': 13548
}
'''
def searchForMovie(movName):
    queryParams = getParams()
    queryParams['query'] = movName
    response = requests.request("GET", SEARCH_MOVIE_URL, params=queryParams).json()
    movie = response["results"][0]
    response2 = requests.request("GET", GET_MOVIE_BY_ID_URL.format(movie["id"]), params=queryParams).json()
    movie["budget"] = response2["budget"]
    movie["revenue"] = response2["revenue"]
    return movie


'''
{  
    'cast_id': 34,
    'character': 'Thomas A. Anderson / Neo',
    'credit_id': '52fe425bc3a36847f80181c1',
    'gender': 2,
    'id': 6384,
    'name': 'Keanu Reeves',
    'order': 0,
    'profile_path': '/bOlYWhVuOiU6azC4Bw6zlXZ5QTC.jpg'
}
'''
def getActorsAndDirectors(movieId):
    queryParams = getParams()
    response = requests.request("GET", CREW_URL.format(movieId), params=queryParams).json()
    cast = response['cast']
    return cast

'''
[{movie1},{movie2}...]
'''
def getActorTopMovies(actorId):
    queryParams = getParams()
    # print("wogooooo")
    response = requests.request("GET", PERSON_MOVIE_CREDITS_URL.format(actorId), params=queryParams).json()
    cast = response["cast"]
    id_popularity_map = {}
    for movie in cast:
        id_popularity_map[movie['id']] = movie['popularity']
    from collections import OrderedDict
    sorted_popularity_dict = OrderedDict(sorted(id_popularity_map.items(), key=lambda x: x[1], reverse=True))
    movies_data_list = []
    # print("damn")
    for idx,movie_id in enumerate(sorted_popularity_dict):
        queryParams = getParams()
        response = requests.request("GET", GET_MOVIE_BY_ID_URL.format(movie_id), params=queryParams).json()
        movies_data_list.append(response)
        # print("okay {}".format(idx))
        if(idx == 5):
            break
    return movies_data_list

'''
{
    "votes" : {
        "avg" : x,
        "min" : x,
        "max" : x
    },
    "revenue" : {
        "avg" : x,
        "min" : x,
        "max" : x
    },
    "budget" : {
        "avg" : x,
        "min" : x,
        "max" : x
    }
}
'''
def getMoviesStats(movie_list):
    votes, revenue, budget = [],[],[] 
    for movie in movie_list:
        if movie["vote_count"] < 50:
            pass
        if movie["vote_average"] != 0:
            votes.append(movie["vote_average"])
        if movie["revenue"] != 0:
            revenue.append(movie["revenue"])
        if movie["budget"] != 0:
            budget.append(movie["budget"])
    votes = np.array(votes)
    revenue = np.array(revenue)
    budget = np.array(budget)
    avg_vote = np.mean(votes).item()
    avg_revenue = np.mean(revenue).item()
    avg_budget = np.mean(budget).item()
    max_vote, max_revenue, max_budget = np.max(votes).item(), np.max(revenue).item(), np.max(budget).item()
    min_vote, min_revenue, min_budget = np.min(votes).item(), np.min(revenue).item(), np.min(budget).item()
    result = {
        "votes" : {
            "avg" : avg_vote,
            "min" : min_vote,
            "max" : max_vote
        },
        "revenue" : {
            "avg" : avg_revenue,
            "min" : min_revenue,
            "max" : max_revenue
        },
        "budget" : {
            "avg" : avg_budget,
            "min" : min_budget,
            "max" : max_budget
        }
    }
    return result