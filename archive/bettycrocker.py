
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
		for ingredient in soup.findAll("dl", {"class" : "recipePartIngredient"}):
			ingredients.append({"ingredient" : " ".join(ingredient.get_text().split())})
		directions = []
		for direction in soup.findAll("span", {"class" : "recipePartStepDescription"}):
			directions.append({"direction" : " ".join(direction.get_text().split())})
		response = {"recipe" : {"ingredients" : ingredients, "directions" : directions}}
		print json.dumps(response)
		return json.dumps(response)
	except urllib2.URLError, e:
		return json.dumps({"Error": "Error parsing recipe from URL"})

url = "http://www.bettycrocker.com/recipes/peanut-butter-lovers-swirl-cakes/44c82940-d35d-40d8-a104-060f604e655e"
recipeToJSON(url)