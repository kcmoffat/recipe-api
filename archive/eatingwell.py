
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
			if (ingredient.get_text() != ""):
				ingredients.append({"ingredient" : " ".join(ingredient.get_text().split())})
		directions = []
		for direction in soup.findAll("ol", {"itemprop" : "recipeinstructions"})[0].findAll("li"):
			directions.append({"direction" : direction.get_text()})
		response = {"recipe" : {"ingredients" : ingredients, "directions" : directions}}
		return json.dumps(response)
	except urllib2.URLError, e:
		return json.dumps({"Error": "Error parsing recipe from URL"})

url = "http://www.eatingwell.com/recipes/poached_cod_green_beans_pesto.html"
recipeToJSON(url)