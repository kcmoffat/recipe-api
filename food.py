
import sys
sys.path.insert(0, 'lib')

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
			ingredients.append({"ingredient_amount": ' '.join(ingredient.get_text().split()[0:2]), "ingredient_name": ' '.join(ingredient.get_text().split()[3:])})
		directions = []
		for direction in soup.findAll("ol", {"itemprop" : "recipeInstructions"})[0].findAll("li"):
			directions.append({"direction": direction.contents[0]})
		response = {"recipe" : {"ingredients" : ingredients, "directions" : directions}}
		print json.dumps(response)
		return json.dumps(response)
	except urllib2.URLError, e:
		return json.dumps({"Error": "Error parsing recipe from URL"})

# url = "http://www.food.com/recipe/crock-pot-chicken-taco-meat-4957"
# recipeToJSON(url)