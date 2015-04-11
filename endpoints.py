import webapp2
import json
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import taskqueue
from RecipeParser import parseRecipeUrlToJson
from BlogParser import fetch_recipe_feed_entries, get_latest_recipes, find_image, add_feed, get_feeds, fetch_all_recipe_feed_entries, add_recipe_feed_set, fetch_recipe_feed_entries_new, get_latest_recipes_new

class RecipeParser(webapp2.RequestHandler):
    def get(self):
    	if self.request.get('url') == '':
    		self.response.write(json.dumps({"Error" : "Missing url parameter.  Example: http://recipe-api.appspot.com/?url=http://allrecipes.com/Recipe/Easy-Chicken-Pasta-Alfredo/"}))
    	else:
	        self.response.headers['Content-Type'] = 'application/json'
	        self.response.write(parseRecipeUrlToJson(self.request.get('url')))

class FetchRecipeFeedEntries(webapp2.RequestHandler):
	def get(self):
		url = self.request.get('url')
		if url == '':
			self.response.write(json.dumps({"Error" : "Missing 'url' parameter."}))
		else:
			self.response.headers['Content-Type'] = 'application/json'
			response = fetch_recipe_feed_entries_new(url)
			self.response.write(response)

class LatestRecipes(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'application/json'
		curs = Cursor(urlsafe=self.request.get('cursor'))
		response = get_latest_recipes_new(curs)
		self.response.write(response)

class Thumbnailer(webapp2.RequestHandler):
	def get(self):
		if self.request.get('url') == '':
			self.response.write(json.dumps({"Error" : "Missing 'url' parameter."}))
		else:
			self.response.headers['Content-Type'] = 'application/json'
			response = json.dumps({"image_url" : find_image(self.request.get('url'))})
			self.response.write(response)

class AddRecipeFeed(webapp2.RequestHandler):
	def get(self):
		url = self.request.get('url')
		if url == '':
			self.response.write(json.dumps({"Error" : "Missing 'url' parameter."}))
		else:
			self.response.headers['Content-Type'] = 'application/json'
			response = add_feed(url)
			self.response.write(response)

class AddRecipeFeedSet(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'application/json'
		response = add_recipe_feed_set()
		self.response.write(response)

class GetRecipeFeeds(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'application/json'
		response = get_feeds()
		self.response.write(response)

class FetchAllRecipeFeedEntries(webapp2.RequestHandler):
	def get(self):
		taskqueue.add(url='/recipe_feeds/create_fetch_all_task/', method='GET')
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps({"response" : "started fetching all recipe feed entries"}))

class CreateFetchAllRecipeFeedEntriesTask(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(fetch_all_recipe_feed_entries())

application = webapp2.WSGIApplication([
    ('/recipe_parser/', RecipeParser),
    ('/recipe_feeds/add/', AddRecipeFeed),
    ('/recipe_feeds/add_set/', AddRecipeFeedSet),
    ('/recipe_feeds/', GetRecipeFeeds),
    ('/recipe_feeds/fetch_all/', FetchAllRecipeFeedEntries),
    ('/recipe_feeds/create_fetch_all_task/', CreateFetchAllRecipeFeedEntriesTask),
    ('/thumbnailer/', Thumbnailer),
    ('/recipe_feed/fetch/', FetchRecipeFeedEntries),
    ('/latest_recipes/', LatestRecipes),
    ('/', RecipeParser),
], debug=True)