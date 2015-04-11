from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

class WebPage(ndb.Model):
	"""A model for representing a web page"""
	site_url = ndb.StringProperty(indexed=True, required=True)
	site_feed_url = ndb.StringProperty(indexed=True, required=True)
	site_name = ndb.StringProperty(indexed=True, required=True)

	page_url = ndb.StringProperty(indexed=True, required=True)
	page_title = ndb.StringProperty(indexed=True, required=True)
	page_description = ndb.StringProperty(indexed=False, required=True)
	page_image_url = ndb.StringProperty(indexed=True, required=False)

	# only for blog posts for now
	page_date_published = ndb.DateTimeProperty(indexed=True, required=False)
	page_date_added = ndb.DateTimeProperty(auto_now_add=True)

	# only for pages that happen to be recipes
	page_recipe_ingredients = ndb.StringProperty(indexed=False, required=False, repeated=True)
	page_recipe_instructions = ndb.StringProperty(indexed=False, required=False, repeated=True)

	def to_dict(self):
		d = super(WebPage, self).to_dict()
		d["page_recipe_ingredients"] = [{"ingredient" : ingredient} for ingredient in d["page_recipe_ingredients"]]
		d["page_recipe_instructions"] = [{"instruction" : instruction} for instruction in d["page_recipe_instructions"]]
		return d

class BlogPost(ndb.Model):
	"""A model for representing a single blog post of a feed"""
	blog_url = ndb.StringProperty(indexed=True, required=True)
	blog_feed_url = ndb.StringProperty(indexed=True, required=True)
	blog_name = ndb.StringProperty(indexed=False, required=True)

	post_url = ndb.StringProperty(indexed=True, required=True)
	post_title = ndb.StringProperty(indexed=False, required=True)
	post_description = ndb.StringProperty(indexed=False, required=True)
	post_image_url = ndb.StringProperty(indexed=True, required=False)
	post_date_published = ndb.DateTimeProperty(indexed=True, required=False)
	post_date_added = ndb.DateTimeProperty(auto_now_add=True)

class BlogFeed(ndb.Model):
	feed_url = ndb.StringProperty(indexed=True, required=True)