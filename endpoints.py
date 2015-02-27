import webapp2
import json
from allrecipes import recipeToJSON

class RecipeParser(webapp2.RequestHandler):
    def get(self):
    	if self.request.get('url') == '':
    		self.response.write(json.dumps({"Error" : "Missing url parameter.  Example: http://recipe-api.appspot.com/?url=http://allrecipes.com/Recipe/Easy-Chicken-Pasta-Alfredo/"}))
    	else:		
	        self.response.headers['Content-Type'] = 'application/json'
	        self.response.write(recipeToJSON(self.request.get('url')))

application = webapp2.WSGIApplication([
    ('/', RecipeParser),
], debug=True)