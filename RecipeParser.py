import sys
sys.path.insert(0, 'lib')

#Not inluded in Google App Engine
from bs4 import BeautifulSoup
from bs4.dammit import EntitySubstitution

#Included in Google App Engine
import urllib2
import json
import logging
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
		print e
		return json.dumps({"error" : "Oops!  We had trouble connecting to that site.  Try another URL."})

def isSchemaOrgStandard(soup):
	try:
		# soup.findAll(True, {"itemtype" : re.compile("http://schema.org/Recipe", re.IGNORECASE)})[0]
		soup.findAll(text="http://schema.org/Recipe")
		return True
	except Exception, e:
		logging.debug(e)
		return False

def isHRecipeStandard(soup):
	try:
		soup.findAll(text="hrecipe")
		return True
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
		"site_name" : EntitySubstitution.substitute_html(site_name),
		"url" : EntitySubstitution.substitute_html(url),
		"name" : EntitySubstitution.substitute_html(name),
		"ingredients" : [{"ingredient" : EntitySubstitution.substitute_html(ingredient)} for ingredient in ingredients],
		"image" : EntitySubstitution.substitute_html(image),
		"description" : EntitySubstitution.substitute_html(description),
		"instructions" : EntitySubstitution.substitute_html(instructions)
		}})
		logging.info(result)
		return result

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
			return trim(self.soup.findAll("meta", {"property" : "og:site_name"})[0].get("content"))
		except:
			return ""

	def parseRecipeUrl(self):
		try:
			return trim(self.soup.findAll("link", {"rel" : "canonical"})[0].get("href"))
		except:
			return ""

	def parseRecipeName(self):
		try:
			return trim(self.soup.findAll("meta", {"property" : "og:title"})[0].get("content"))
		except:
			return ""

	def parseRecipeIngredients(self):
		try:
			return [trim(ingredient.get_text()) for ingredient in self.soup.findAll(True, {"itemprop" : "ingredients"})]
		except:
			return []

	def parseRecipeImage(self):
		try:
			return trim(self.soup.findAll("meta", {"property" : "og:image"})[0].get("content"))
		except:
			return ""

	def parseRecipeDescription(self):
		try:
			return trim(self.soup.findAll(True, {"itemprop" : "description"})[0].get_text())
		except:
			return ""

	def parseRecipeInstructions(self):
		try:
			return trim(self.soup.findAll(True, {"itemprop" : "recipeInstructions"})[0].get_text())
		except:
			return ""

class HRecipeParser(RecipeParser):
	def parseRecipeSiteName(self):
		try:
			return trim(self.soup.findAll("meta", {"property" : "og:site_name"})[0].get("content"))
		except:
			return ""

	def parseRecipeUrl(self):
		try:
			return trim(self.soup.findAll("link", {"rel" : "canonical"})[0].get("href"))
		except:
			return ""

	def parseRecipeName(self):
		try:
			return trim(self.soup.findAll(True, {"class" : "fn"})[0].get_text())
		except:
			return ""

	def parseRecipeIngredients(self):
		try:
			return [trim(ingredient.get_text()) for ingredient in self.soup.findAll(True, {"class" : "ingredient"})]
		except:
			return []

	def parseRecipeImage(self):
		try:
			return trim(self.soup.findAll(True, {"img" : "og:image"})[0].get("content"))
		except:
			return ""

	def parseRecipeDescription(self):
		try:
			return trim(self.soup.findAll(True, {"class" : "summary"})[0].get_text())
		except:
			return ""

	def parseRecipeInstructions(self):
		try:
			return trim(self.soup.findAll(True, {"class" : "instructions"})[0].get_text())
		except:
			return ""