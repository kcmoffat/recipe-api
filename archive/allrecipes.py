
import sys
sys.path.insert(0, 'lib')

#Not inluded in Google App Engine
from bs4 import BeautifulSoup
from urlparse import urlparse

#Included in Google App Engine
import urllib2
import json
from utils import trim

def recipeToJSON(url):
	try:
		result = urllib2.urlopen(url)
		html = result.read()
		soup = BeautifulSoup(html)
		o = urlparse(url)
		host = o.hostname

		name = trim(soup.findAll("h1")[0].get_text())

		imageUrl = soup.findAll("meta", {"property" : "og:image"})[0].get("content")

		ingredients = []
		directions = []
		#mobile html is different than regular site
		if host == "m.allrecipes.com":
			for ingredient in soup.findAll("span", {"itemprop" : "ingredients"}):
				ingredients.append({"ingredient" : trim(ingredient.get_text())})
			for direction in soup.findAll("ol", {"itemprop" : "recipeInstructions"})[0].findAll("li"):
				directions.append({"direction": trim(direction.get_text())})
		else:
			for ingredient in soup.findAll("p", {"class" : "fl-ing"}):
				ingredients.append({"ingredient" : trim(ingredient.get_text())})
			for direction in soup.findAll("div", {"itemprop" : "recipeInstructions"})[0].ol.findAll("li"):
				directions.append({"direction": trim(direction.get_text())})

		response = {"recipe" : {"name" : name, "image_url" : imageUrl, "ingredients" : ingredients, "directions" : directions}}
		return json.dumps(response)
	except urllib2.URLError, e:
		return json.dumps({"Error": "Error parsing recipe from URL"})

# url = "http://allrecipes.com/Recipe/Easy-Chicken-Pasta-Alfredo/"
url = "http://m.allrecipes.com/recipe/213469/sweetheart-cupcakes/?page=0"
recipeToJSON(url)