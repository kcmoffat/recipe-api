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
from utils import trim, find_image, find_title

def parseRecipeUrlToJsonOld(url):
	try:	
		response = urllib2.urlopen(url)
		html = response.read()
		soup = BeautifulSoup(html)
		return SchemaOrgParser(soup).parseRecipe()

		# if (isSchemaOrgStandard(soup)):
		# 	logging.info("html conforms to schema.org standard")
		# 	parser = SchemaOrgParser(soup)
		# 	return parser.parseRecipe()
		# elif (isHRecipeStandard(soup)):
		# 	logging.info("html conforms to hrecipe standard")
		# 	parser = HRecipeParser(soup)
		# 	return parser.parseRecipe()
		# else:
		# 	logging.info("html does not conform to a recipe standard")
		# 	return json.dumps({"error" : "We had trouble finding a recipe on this page.  Try another URL."})
	except Exception, e:
		logging.debug(e)
		return json.dumps({"error" : "We had trouble connecting to that site.  Try another URL."})



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
			logging.info("html does not conform to a recipe standard.  parsing what we can")
			parser = RecipeParser(soup)
			return parser.parseRecipe()
	except Exception, e:
		logging.debug(e)
		return json.dumps({"error" : "We had trouble connecting to that site.  Try again later or try another URL."})

def getRecipeIngredientsFromSoup(soup):
	if (isSchemaOrgStandard(soup)):
		logging.info("html conforms to schema.org standard")
		return [{"ingredient" : ingredient} for ingredient in SchemaOrgParser(soup).parseRecipeIngredients()]
	elif (isHRecipeStandard(soup)):
		logging.info("html conforms to hrecipe standard")
		return [{"ingredient" : ingredient} for ingredient in HRecipeParser(soup).parseRecipeIngredients()]
	else:
		logging.info("html does not conform to a recipe standard")
		return []

def getRecipeInstructionsFromSoup(soup):
	if (isSchemaOrgStandard(soup)):
		logging.info("html conforms to schema.org standard")
		return [{"instruction" : instruction} for instruction in SchemaOrgParser(soup).parseRecipeInstructions()]
	elif (isHRecipeStandard(soup)):
		logging.info("html conforms to hrecipe standard")
		return [{"instruction" : instruction} for instruction in HRecipeParser(soup).parseRecipeInstructions()]
	else:
		logging.info("html does not conform to a recipe standard")
		return []

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

# Parent class of recipe parsers.  Only used if we can't match a more specific schema
class RecipeParser(object):
	def __init__(self, soup):
		self.soup = soup

	def parseRecipe(self):

		self.site_feed_url = ""
		self.site_name = self.parseRecipeSiteName()
		self.page_url = self.parseRecipeUrl()
		self.page_title = self.parseRecipeName()
		self.page_description = self.parseRecipeDescription()
		self.page_image_url = self.parseRecipeImage()
		self.page_date_published = ""
		self.page_recipe_ingredients = self.parseRecipeIngredients()
		self.page_recipe_instructions = self.parseRecipeInstructions()

		result = json.dumps({"recipe" : {
		"site_feed_url" : self.site_feed_url,
		"site_name" : self.site_name,
		"page_url" : self.page_url,
		"page_title" : self.page_title,
		"page_description" : self.page_description,
		"page_image_url" : self.page_image_url,
		"page_date_published" : self.page_date_published,
		"page_recipe_ingredients" : [{"ingredient" : ingredient} for ingredient in self.page_recipe_ingredients],
		"page_recipe_instructions" : [{"instruction" : instruction} for instruction in self.page_recipe_instructions]
		}})
		logging.info(result)
		return result

	def parseRecipeSiteName(self):
		try:
			return trim(self.soup.findAll("meta", {"property" : re.compile("og:site_name", re.IGNORECASE)})[0].get("content"))
		except:
			return ""
	
	def parseRecipeUrl(self):
		try:
			url = trim(self.soup.findAll("link", {"rel" : re.compile("canonical", re.IGNORECASE)})[0].get("href"))
			logging.info("found canonical url: %s", url)
			return url
		except:
			logging.info("couldn't find canonical url")
			return ""

	def parseRecipeName(self):
		try:
			title = find_title(self.page_url, self.soup)
			if not title:
				return ""
			else:
				return title
		except:
			return ""

	def parseRecipeImage(self):
		try:
			image_url = find_image(self.page_url, self.soup)
			if not image_url:
				return ""
			else:
				return image_url
		except:
			return ""

	def parseRecipeDescription(self):
		try:
			return trim(self.soup.findAll("meta", {"property" : re.compile("og:description", re.IGNORECASE)})[0].get("content"))
		except:
			return ""

	def parseRecipeIngredients(self):
		return []

	def parseRecipeInstructions(self):
		return []

class SchemaOrgParser(RecipeParser):
	def parseRecipeDescription(self):
		try:
			description = super(SchemaOrgParser, self).parseRecipeDescription()
			if not description or description == "":
				return trim(self.soup.findAll(True, {"itemprop" : re.compile("description", re.IGNORECASE)})[0].get_text())
			else:
				return description
		except Exception, e:
			logging.info(e)
			return ""

	def parseRecipeIngredients(self):
		try:
			return [trim(ingredient.get_text()) for ingredient in self.soup.findAll(True, {"itemprop" : re.compile("ingredients", re.IGNORECASE)})]
		except:
			return []

	def parseRecipeInstructions(self):
		try:
			instructions = self.soup.findAll(True, {"itemprop" : re.compile("recipeInstructions", re.IGNORECASE)})
			if (len(instructions) > 1):
				return [trim(instruction.get_text()) for instruction in instructions]
			else:
				return [trim(instruction) for instruction in instructions[0].stripped_strings]
		except:
			return []

class HRecipeParser(RecipeParser):
	def parseRecipeDescription(self):
		try:
			description = super(HRecipeParser, self).parseRecipeDescription()
			if not description or description == "":
				return trim(self.soup.findAll(True, {"class" : re.compile("summary", re.IGNORECASE)})[0].get_text())
			else:
				return description
		except:
			return ""
	def parseRecipeIngredients(self):
		try:
			return [trim(ingredient.get_text()) for ingredient in self.soup.findAll(True, {"class" : re.compile("ingredient", re.IGNORECASE)})]
		except:
			return []

	def parseRecipeInstructions(self):
		try:
			return [trim(instruction) for instruction in self.soup.findAll(True, {"class" : re.compile("instructions", re.IGNORECASE)})[0].stripped_strings]
		except:
			return []