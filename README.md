# Movie Conversation Bot

## Broad Goal
The goal of this project is to build an intelligent conversational agent capable of having free flowing conversations with a user about any topic relating to movies. The bot must be able to answer specific user queries about movies, and then extend conversations in different directions as it gets to know more about the user's tastes and choices. Ultimately it must engage users for as long as possible and appear as natural as possible with respect to its style of conversations. 

## Current capabilities
As of now, the bot is capable of answering the most basic questions about particular movies that involve the actors, directors, storyline and other basic details. 

## On going work
Partial implementation of anomaly-based conversation strategy. The strategy involves finding anomalies in statistics related to the actors/directors of a movie queried by the user and commenting on the same. The statistics are currently related to the imdb ratings of all movies involving a particular actor (or a set of them). Anomalies open up interesting pathways for starting conversations. 

### Technology/Data
Data: The dataset used is the IMDb dataset which has been scraped and arranged into MySQL database tables. 
NLP Interface: Dialogflow API + Frontend hosted on the Dialogflow 
Webhook: Flask