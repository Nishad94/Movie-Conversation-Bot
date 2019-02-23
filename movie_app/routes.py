from flask import request, jsonify, render_template
import os
import dialogflow
import pprint
import requests
import json
from movie_app import tmdb
import numpy as np
import json
from movie_app import app


DIALOGFLOW_PROJECT_ID="helloworld-597d8"
GOOGLE_APP_CREDENTIALS="HelloWorld-bb6a78d1c91d.json"

# def extract_actor_anomaly(imdb_title_id):
# 	cnx = mysql.connector.connect(user='root', host='127.0.0.1',database='movies')
# 	cursor = cnx.cursor()
# 	actors_stmt = "Select actors from movie_info where tconst = '{}'".format(imdb_title_id)
# 	print "trying query for " + imdb_title_id
# 	try:
# 		cursor.execute(actors_stmt)
# 		print "checking actors"
# 		actors = []
# 		for actor_id in cursor:
# 			actors.append(actor_id)
# 		print actors
# 		if len(actors) > 0:
# 			actors = actors[0][0].split(",")
# 		print "Actors in {} = {}".format(imdb_title_id, actors)
# 		actor_titles_stmt = "select titles,name from name_info where nconst='{}'"
# 		actor_title_map = {}
# 		actor_name_map = {}
# 		for actor in actors:
# 			cursor.execute(actor_titles_stmt.format(actor))
# 			titles = []
# 			names = []
# 			for t in cursor:
# 				print t
# 				print "heyyyyyy"
# 				titles.append(t[0])
# 				names.append(t[1])
# 			titles = titles[0].split(",")
# 			actor_title_map[actor] = titles
# 			names = names[0]
# 			actor_name_map[actor] = names
# 		print "Actor and Titles: \n" + str(actor_title_map)
# 		print "Actor and Name: \n" + str(actor_name_map)

# 		# get most popular actor according to titles count
# 		max_actor_nconst = None
# 		maxTitles = float("-inf")
# 		for actor_nconst in actor_title_map:
# 			titles = actor_title_map[actor_nconst]
# 			print "Titles for {} : {}".format(actor_nconst,titles)
# 			if len(titles) > maxTitles:
# 				maxTitles = len(titles)
# 				max_actor_nconst = actor_nconst
# 		get_titles_stmt = "Select rating,primary_title,tconst from movie_info where tconst='{}'"
# 		title_detailed_list = []
# 		current_movie_rating = -1
# 		current_movie_title = "BLANK"
# 		for t in actor_title_map[max_actor_nconst]:
# 			print "Getting rating for title {}".format(t)
# 			cursor.execute(get_titles_stmt.format(t))
# 			for m in cursor:
# 				if m is not None:
# 					rating = m[0]
# 					title = m[1]
# 					tconst = m[2]
# 					movie_json = {}
# 					movie_json["rating"] = rating
# 					movie_json["title"] = title
# 					if tconst == imdb_title_id:
# 						current_movie_rating = rating
# 						current_movie_title = title
# 					title_detailed_list.append(movie_json)
# 		print title_detailed_list
# 		avg = getAverageRating(title_detailed_list)
# 		percent_of_avg = current_movie_rating/avg
# 		if percent_of_avg > 0.75:
# 			comment = "Compared to other movies {} has acted in, users seem to love this movie! Average Rating: {}, {} : {}"
# 		elif percent_of_avg > 0.5:
# 			comment = "This movie is as good as the other movies {} has acted in. Average Rating: {}, {} : {}"
# 		elif percent_of_avg > 0.25:
# 			comment = "This movie is worse than other movies {} has acted in. Average Rating: {}, {} : {}"
# 		else:
# 			comment = "This movie is one of {}'s worst movies. Average Rating: {}, {} : {}"
# 		cursor.close()
# 		cnx.close()
# 		return comment.format(actor_name_map[max_actor_nconst],avg,current_movie_title,current_movie_rating)
# 	except Exception as e:
# 		print e 

@app.route('/')
def index():
	return 'hi'

@app.route('/get_movie_detail', methods=['POST'])
def get_movie_detail():
	data = request.get_json(silent=True)
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(data)
	if data['queryResult']['intent']['displayName'] == "MovieBasic":
		print("aaa")
		reply = movie_basic(data)
		print("aaa")
	elif data['queryResult']['intent']['displayName'] == "MovieRating":
		print("bbb")
		reply = movie_details(data,"vote")
		print("bbb")
	elif data['queryResult']['intent']['displayName'] == "MovieBudget":
		print("ccc")
		reply = movie_details(data,"budget")
		print("ccc")
	elif data['queryResult']['intent']['displayName'] == "MovieRevenue":
		print("ddd")
		reply = movie_details(data,"revenue")
		print("ddd")
	elif data['queryResult']['intent']['displayName'] == "MovieAnomaly":
		print("eee")
		reply = movie_anomaly(data)
	return jsonify(reply)

def movie_anomaly(data):
	comment = "Sorry, could you try again with the movie name?"
	if "outputContexts" in data['queryResult']:
		output_contexts = data['queryResult']['outputContexts']
		for context in output_contexts:
			if context["name"].find("movie-actor-details") != -1:
				stats = context["parameters"]["stats"]
				if stats["votes"]["avg"] < context["parameters"]["vote"] :
					comment = "You should definitely watch this movie! It has done better than most other movies {} has acted in! The rating for {} is {} while his average rating for the others is {}.".format(context["parameters"]["actor"],context["parameters"]["title"],context["parameters"]["vote"],stats["votes"]["avg"])
				else:
					comment = "Its an avoidable film. The movie has done worse than most other movies {} has acted in! The rating for {} is {} while his average rating for the others is {}.".format(context["parameters"]["actor"],context["parameters"]["title"],context["parameters"]["vote"],stats["votes"]["avg"])
	reply = {
		"fulfillmentText": comment,
		"outputContexts": data['queryResult']['outputContexts'],
		"payload": {
			"google": {
				"expectUserResponse": 'true',
				"richResponse": {
					"items": [
						{
							"simpleResponse": {
								"textToSpeech": comment
							}
						}
					]
				}
			}
		}
	}
	return reply

def movie_details(data,param):
	rating = "Sorry, could you try again with the movie name?"
	if "outputContexts" in data['queryResult']:
		output_contexts = data['queryResult']['outputContexts']
		for context in output_contexts:
			if context["name"].find("movie-details") != -1:
				rating = "The {} for the movie \"{}\" is {}".format(param, context["parameters"]["title"], context["parameters"][param])

	reply = {
		"fulfillmentText": rating,
		"outputContexts": data['queryResult']['outputContexts'],
		"payload": {
			"google": {
				"expectUserResponse": 'true',
				"richResponse": {
					"items": [
						{
							"simpleResponse": {
								"textToSpeech": rating
							}
						}
					]
				}
			}
		}
	}
	return reply


def movie_basic(data):
	movie_name = data['queryResult']['parameters']['movie']
	movie = tmdb.searchForMovie(movie_name)
	crew = tmdb.getActorsAndDirectors(movie["id"])
	top_movies = tmdb.getActorTopMovies(crew[0]["id"])
	if "outputContexts" in data['queryResult']:
		output_contexts = data['queryResult']['outputContexts']
		for context in output_contexts:
			if context["name"].find("movie-actor-details") != -1:
				context["parameters"]["actor"] = crew[0]["name"]
				context["parameters"]["stats"] = tmdb.getMoviesStats(top_movies)
				context["parameters"]["title"] = movie["title"]
				context["parameters"]["vote"] = movie["vote_average"]
				context["parameters"]["id"] = movie["id"]
				context["parameters"]["budget"] = movie["budget"]
				context["parameters"]["revenue"] = movie["revenue"]
			if context["name"].find("movie-details") != -1:
				context["parameters"]["title"] = movie["title"]
				context["parameters"]["vote"] = movie["vote_average"]
				context["parameters"]["id"] = movie["id"]
				context["parameters"]["budget"] = movie["budget"]
				context["parameters"]["revenue"] = movie["revenue"]
	reply = {
		"fulfillmentText": "'Release Date': {},\n 'Overview': {}".format(movie["release_date"], movie["overview"]),
		# "fulfillmentMessages" : [
		# 	{
		# 		"text" :  {
		# 			"text" : [ 
		# 			"'Release Date': {},\n 'Overview': {}".format(movie["release_date"], movie["overview"]), "Liked that?"
		# 			]
		# 		}
		# 	}
		# ],
		"outputContexts": data['queryResult']['outputContexts'],
		"payload": {
			"google": {
				"expectUserResponse": 'true',
				"richResponse": {
					"items": [
						{
							"simpleResponse": {
								"textToSpeech": "'Release Date': {},\n 'Overview': {}".format(movie["release_date"], movie["overview"])
							}
						},
						{
							"simpleResponse": {
								"textToSpeech": "\n\nWant more information?"
							}
						}
					]
				}
			}
		}
	}
	pprint.pprint(reply)
	return reply