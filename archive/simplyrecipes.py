
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
			ingredients.append({"ingredient" : ingredient.get_text()})
		directions = []
		for direction in soup.findAll("div", {"itemprop" : "recipeInstructions"})[0].findAll("p"):
			[b.extract() for b in direction("b")]
			[strong.extract() for strong in direction("strong")]
			directions.append({"direction" : direction.get_text().strip()})
		response = {"recipe" : {"ingredients" : ingredients, "directions" : directions}}
		print json.dumps(response)
		return json.dumps(response)
	except urllib2.URLError, e:
		return json.dumps({"Error": "Error parsing recipe from URL"})

url = "http://www.simplyrecipes.com/recipes/irish_beef_stew/"
recipeToJSON(url)