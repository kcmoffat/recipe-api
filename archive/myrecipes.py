
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
		for ingredient in soup.findAll("div", {"itemprop" : "ingredient"}):
			ingredients.append({"ingredient" : " ".join(ingredient.get_text().split())})
		directions = []
		for direction in soup.findAll("div", {"class" : "field-item even"})[0].findAll("p"):
			directions.append({"direction" : direction.get_text()[3:]})
		response = {"recipe" : {"ingredients" : ingredients, "directions" : directions}}
		return json.dumps(response)
	except urllib2.URLError, e:
		return json.dumps({"Error": "Error parsing recipe from URL"})

url = "http://www.myrecipes.com/recipe/pork-chops-balsamic-roasted-vegetables"
recipeToJSON(url)