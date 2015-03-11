
import sys
sys.path.insert(0, 'lib')
import string

#Not inluded in Google App Engine
from bs4 import BeautifulSoup

#Included in Google App Engine
import urllib2
import json

def recipeToJSON(url):
	try:
		result = urllib2.urlopen(url)
		html = result.read()
		soup = BeautifulSoup(html)
		ingredients = []
		for ingredient in soup.findAll("li", {"itemprop" : "ingredients"}):
			ingredients.append({"ingredient" : " ".join(ingredient.get_text().split())})
		directions = []
		for direction in soup.findAll("div", {"itemprop" : "recipeInstructions"})[0].findAll("p")[:-3]:
			directions.append({"direction" : " ".join(direction.get_text().split())})
		response = {"recipe" : {"ingredients" : ingredients, "directions" : directions}}
		print json.dumps(response)
		return json.dumps(response)
	except urllib2.URLError, e:
		return json.dumps({"Error": "Error parsing recipe from URL"})

url = "http://www.foodnetwork.com/recipes/food-network-kitchens/roast-chicken-with-spring-vegetables-recipe.html"
recipeToJSON(url)