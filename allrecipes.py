
import sys
sys.path.insert(0, 'lib')

#Not inluded in Google App Engine
from bs4 import BeautifulSoup

#Included in Google App Engine
import urllib2
import json

def recipeToJSON(url):
	try:
		print url
		result = urllib2.urlopen(url)
		html = result.read()
		soup = BeautifulSoup(html)
		ingredients = []
		for ingredient in soup.findAll("p", {"class" : "fl-ing"}):
			ingredients.append({"ingredient_amount": ingredient.contents[1].contents[0], "ingredient_name": ingredient.contents[3].contents[0]})
		directions = []
		for direction in soup.findAll("div", {"itemprop" : "recipeInstructions"})[0].ol.findAll("li"):
			directions.append({"direction": direction.span.contents[0]})
		response = {"recipe" : {"ingredients" : ingredients, "directions" : directions}}
		return json.dumps(response)
	except urllib2.URLError, e:
		return json.dumps({"Error": "Error parsing recipe from URL"})