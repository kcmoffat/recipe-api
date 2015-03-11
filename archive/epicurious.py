
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
		for direction in soup.findAll("div", {"id" : "preparation"})[0].findAll("p"):
			directions.append({"direction" : direction.get_text().strip().replace("\r", " ").replace("\t", " ").replace("\n", " ")})
		response = {"recipe" : {"ingredients" : ingredients, "directions" : directions}}
		return json.dumps(response)
	except urllib2.URLError, e:
		return json.dumps({"Error": "Error parsing recipe from URL"})

# url = "http://www.epicurious.com/recipes/food/views/bucatini-with-butter-roasted-tomato-sauce-51198650"
# recipeToJSON(url)