import sys
sys.path.insert(0, 'lib')

#Not inluded in Google App Engine
from bs4 import BeautifulSoup
from bs4.dammit import EntitySubstitution

#Included in Google App Engine
import urllib2
import json
import logging
import re
from utils import trim

def parseRecipeUrlToJson(url):
	try:	
		response = urllib2.urlopen(url)
		html = response.read()
		soup = BeautifulSoup(html)
		if (isSchemaOrgStandard(soup)):
			logging.info("html conforms to schema.org standard")
			parser = SchemaOrgParser(soup)
			return parser.parseRecipe()
		elif (isHRecipeStandard(soup)):
			logging.info("html conforms to hrecipe standard")
			parser = HRecipeParser(soup)
			return parser.parseRecipe()
		else:
			logging.info("html does not conform to a recipe standard")
			return json.dumps({"error" : "Oops!  We had trouble finding a recipe on this page.  Try another URL."})
	except Exception, e:
		logging.debug(e)
		return json.dumps({"error" : "Oops!  We had trouble connecting to that site.  Try another URL."})

def isSchemaOrgStandard(soup):
	try:
		return soup.findAll(True, {"itemtype" : re.compile("http://schema.org/Recipe", re.IGNORECASE)}) != []
	except Exception, e:
		logging.debug(e)
		return False

def isHRecipeStandard(soup):
	try:
		return soup.findAll(True, {"class" : re.compile("hrecipe", re.IGNORECASE)}) != []
	except Exception, e:
		logging.debug(e)
		return False

# Abstract super class
class RecipeParser:
	def __init__(self, soup):
		self.soup = soup

	def parseRecipe(self):

		site_name = self.parseRecipeSiteName()
		url = self.parseRecipeUrl()
		name = self.parseRecipeName()
		ingredients = self.parseRecipeIngredients()
		image = self.parseRecipeImage()
		description = self.parseRecipeDescription()
		instructions = self.parseRecipeInstructions()

		result = json.dumps({"recipe" : {
		"site_name" : trim(site_name),
		"url" : trim(url),
		"name" : trim(name),
		"ingredients" : [{"ingredient" : trim(ingredient)} for ingredient in ingredients],
		"image" : trim(image),
		"description" : trim(description),
		"instructions" : [{"instruction" : trim(instruction)} for instruction in instructions]
		}})
		logging.info(result)
		return result

	# parseRecipe takes care of trimming whitespace 
	# and converting unicode to html entities,
	# no need to worry about that
	# when implementing these methods.
	def parseRecipeSiteName(self):
		"""abstract method"""
	
	def parseRecipeUrl(self):
		"""abstract method"""

	def parseRecipeName(self):
		"""abstract method"""

	def parseRecipeIngredients(self):
		"""abstract method"""

	def parseRecipeImage(self):
		"""abstract method"""

	def parseRecipeDescription(self):
		"""abstract method"""

	def parseRecipeInstructions(self):
		"""abstract method"""

class SchemaOrgParser(RecipeParser):
	def parseRecipeSiteName(self):
		try:
			return self.soup.findAll("meta", {"property" : re.compile("og:site_name", re.IGNORECASE)})[0].get("content")
		except:
			return ""

	def parseRecipeUrl(self):
		try:
			return self.soup.findAll("link", {"rel" : re.compile("canonical", re.IGNORECASE)})[0].get("href")
		except:
			return ""

	def parseRecipeName(self):
		try:
			return self.soup.findAll("meta", {"property" : re.compile("og:title", re.IGNORECASE)})[0].get("content")
		except:
			return ""

	def parseRecipeIngredients(self):
		try:
			return [ingredient.get_text() for ingredient in self.soup.findAll(True, {"itemprop" : re.compile("ingredients", re.IGNORECASE)})]
		except:
			return []

	def parseRecipeImage(self):
		try:
			return self.soup.findAll("meta", {"property" : re.compile("og:image", re.IGNORECASE)})[0].get("content")
		except:
			return ""

	def parseRecipeDescription(self):
		try:
			return self.soup.findAll(True, {"itemprop" : re.compile("description", re.IGNORECASE)})[0].get_text()
		except:
			return ""

	def parseRecipeInstructions(self):
		try:
			return self.soup.findAll(True, {"itemprop" : re.compile("recipeInstructions", re.IGNORECASE)})[0].stripped_strings
		except:
			return ""

class HRecipeParser(RecipeParser):
	def parseRecipeSiteName(self):
		try:
			return self.soup.findAll("meta", {"property" : re.compile("og:site_name", re.IGNORECASE)})[0].get("content")
		except:
			return ""

	def parseRecipeUrl(self):
		try:
			return self.soup.findAll("link", {"rel" : re.compile("canonical", re.IGNORECASE)})[0].get("href")
		except:
			return ""

	def parseRecipeName(self):
		try:
			return self.soup.findAll(True, {"class" : re.compile("fn", re.IGNORECASE)})[0].get_text()
		except:
			return ""

	def parseRecipeIngredients(self):
		try:
			return [ingredient.get_text() for ingredient in self.soup.findAll(True, {"class" : re.compile("ingredient", re.IGNORECASE)})]
		except:
			return []

	def parseRecipeImage(self):
		try:
			return self.soup.findAll(True, {"class" : re.compile("photo", re.IGNORECASE)})[0].get("src")
		except:
			return ""

	def parseRecipeDescription(self):
		try:
			return self.soup.findAll(True, {"class" : re.compile("summary", re.IGNORECASE)})[0].get_text()
		except:
			return ""

	def parseRecipeInstructions(self):
		try:
			return self.soup.findAll(True, {"class" : re.compile("instructions", re.IGNORECASE)})[0].stripped_strings
		except:
			return ""