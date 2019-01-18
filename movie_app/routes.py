from flask import request, jsonify, render_template
import os
import dialogflow
import pprint
import requests
import json
import mysql.connector
from movie_app import app

OMDB_API_KEY=""
DIALOGFLOW_PROJECT_ID=""
GOOGLE_APP_CREDENTIALS="HelloWorld-bb6a78d1c91d.json"

def getAverageRating(titles_list):
	print "Geting avg: "
	total = 0
	count = 0
	for t in titles_list:
		if t["rating"] is not None:
			total += t["rating"]
			count += 1
	return total/float(count)

def extract_actor_anomaly(imdb_title_id):
	cnx = mysql.connector.connect(user='root', host='127.0.0.1',database='movies')
	cursor = cnx.cursor()
	actors_stmt = "Select actors from movie_info where tconst = '{}'".format(imdb_title_id)
	print "trying query for " + imdb_title_id
	try:
		cursor.execute(actors_stmt)
		print "checking actors"
		actors = []
		for actor_id in cursor:
			actors.append(actor_id)
		print actors
		if len(actors) > 0:
			actors = actors[0][0].split(",")
		print "Actors in {} = {}".format(imdb_title_id, actors)
		actor_titles_stmt = "select titles,name from name_info where nconst='{}'"
		actor_title_map = {}
		actor_name_map = {}
		for actor in actors:
			cursor.execute(actor_titles_stmt.format(actor))
			titles = []
			names = []
			for t in cursor:
				print t
				print "heyyyyyy"
				titles.append(t[0])
				names.append(t[1])
			titles = titles[0].split(",")
			actor_title_map[actor] = titles
			names = names[0]
			actor_name_map[actor] = names
		print "Actor and Titles: \n" + str(actor_title_map)
		print "Actor and Name: \n" + str(actor_name_map)

		# get most popular actor according to titles count
		max_actor_nconst = None
		maxTitles = float("-inf")
		for actor_nconst in actor_title_map:
			titles = actor_title_map[actor_nconst]
			print "Titles for {} : {}".format(actor_nconst,titles)
			if len(titles) > maxTitles:
				maxTitles = len(titles)
				max_actor_nconst = actor_nconst
		get_titles_stmt = "Select rating,primary_title,tconst from movie_info where tconst='{}'"
		title_detailed_list = []
		current_movie_rating = -1
		current_movie_title = "BLANK"
		for t in actor_title_map[max_actor_nconst]:
			print "Getting rating for title {}".format(t)
			cursor.execute(get_titles_stmt.format(t))
			for m in cursor:
				if m is not None:
					rating = m[0]
					title = m[1]
					tconst = m[2]
					movie_json = {}
					movie_json["rating"] = rating
					movie_json["title"] = title
					if tconst == imdb_title_id:
						current_movie_rating = rating
						current_movie_title = title
					title_detailed_list.append(movie_json)
		print title_detailed_list
		avg = getAverageRating(title_detailed_list)
		percent_of_avg = current_movie_rating/avg
		if percent_of_avg > 0.75:
			comment = "Compared to other movies {} has acted in, users seem to love this movie! Average Rating: {}, {} : {}"
		elif percent_of_avg > 0.5:
			comment = "This movie is as good as the other movies {} has acted in. Average Rating: {}, {} : {}"
		elif percent_of_avg > 0.25:
			comment = "This movie is worse than other movies {} has acted in. Average Rating: {}, {} : {}"
		else:
			comment = "This movie is one of {}'s worst movies. Average Rating: {}, {} : {}"
		cursor.close()
		cnx.close()
		return comment.format(actor_name_map[max_actor_nconst],avg,current_movie_title,current_movie_rating)
	except Exception as e:
		print e 

@app.route('/')
def index():
	return 'hi'

@app.route('/get_movie_detail', methods=['POST'])
def get_movie_detail():
	data = request.get_json(silent=True)
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(data)
	movie = data['queryResult']['parameters']['movie']
	print(movie)
	api_key = OMDB_API_KEY

	movie_detail = requests.get('http://www.omdbapi.com/?t={0}&apikey={1}'.format(movie, api_key)).content
	movie_detail = json.loads(movie_detail)

	imdb_id = movie_detail['imdbID']
	print "IMDB = " + imdb_id
	final_statement = extract_actor_anomaly(imdb_id)
	
	pp.pprint(movie_detail)
	response = """
		Title: {0}\n
		Released: {1}\n
		Actors: {2}\n
		Plot: {3}
	""".format(movie_detail['Title'], movie_detail['Released'], movie_detail['Actors'], movie_detail['Plot'])
	response = """ *Anomaly comment* : {7} *-----* '{0}' is a {5} language movie that was released in {6} on {1}. It was directed by '{3}', starring '{2}'
	 and the plot is as follows: '{4}'.""".format(movie_detail['Title'], movie_detail['Released'], movie_detail['Actors'], movie_detail['Director'],movie_detail['Plot'],movie_detail['Language'],movie_detail['Country'],final_statement)
	reply = {
		"fulfillmentText": response,
	}

	return jsonify(reply)