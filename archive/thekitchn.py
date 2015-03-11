
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
		for ingredient in soup.findAll("span", {"itemprop" : "ingredients"}):
			ingredients.append({"ingredient" : ingredient.get_text().strip()})
		directions = []
		for direction in soup.findAll("div", {"id" : "recipe"})[0].findAll("p")[1:-1]:
			if direction.findAll("span", {"itemprop" : "ingredients"}) == []:
				directions.append({"direction": direction.get_text().strip()})
		response = {"recipe" : {"ingredients" : ingredients, "directions" : directions}}
		return json.dumps(response)
	except urllib2.URLError, e:
		return json.dumps({"Error": "Error parsing recipe from URL"})

# url = "http://www.thekitchn.com/recipe-ginger-cilantro-sesame-baked-tilapia-fish-weeknigh-dinner-recipes-from-the-kitchn-24737"
# recipeToJSON(url)