
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
			ingredients.append({"ingredient" : ingredient.get_text()})
		directions = []
		for direction in soup.findAll("div", {"id" : "instructions"})[0].ol.findAll("li"):
			[span.extract() for span in direction("span")]
			directions.append({"direction": direction.get_text()})
		response = {"recipe" : {"ingredients" : ingredients, "directions" : directions}}
		return json.dumps(response)
	except urllib2.URLError, e:
		return json.dumps({"Error": "Error parsing recipe from URL"})

# url = "http://www.chow.com/recipes/31253-parmesan-breaded-pork-chops"
# recipeToJSON(url)