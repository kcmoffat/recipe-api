import sys
sys.path.insert(0, 'lib')

#Not inluded in Google App Engine
from bs4 import BeautifulSoup
from bs4.dammit import EntitySubstitution
import feedparser

#Included in Google App Engine
from PIL import ImageFile
import urllib2
import urlparse
import httplib
import json
import logging
import re
from utils import trim, find_image, get_soup_from_url
from feeds import feeds
from Models import BlogFeed, BlogPost, WebPage
from RecipeParser import getRecipeIngredientsFromSoup, getRecipeInstructionsFromSoup
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import memcache
from time import mktime
from datetime import datetime


# Find all new blog entries and insert them into GAE datastore
def fetch_all_recipe_feed_entries():
	new_posts_for_feed = 0
	existing_posts_for_feed = 0
	errors = 0
	error_feeds = []
	for feed in BlogFeed.query().fetch():
		feed_url = feed.feed_url
		result = json.loads(fetch_recipe_feed_entries_new(feed_url))
		new_posts_for_feed += result['response']['new']
		existing_posts_for_feed += result['response']['existing']
		errors += result['response']['errors']
		error_feeds = error_feeds + result['response']['error_feed']
	return json.dumps({"response" : {"new" : new_posts_for_feed,
									"existing" : existing_posts_for_feed,
									"errors" : errors,
									"error_feeds" : error_feeds}})

def fetch_recipe_feed_entries(feed_url):
	logging.info("fetchies entries for %s", feed_url)
	new_posts = 0
	existing_posts = 0
	errors = 0
	try:
		d = feedparser.parse(feed_url)
		blog_url = d.feed.link
		blog_feed_url = feed_url
		blog_name = d.feed.title
		posts = []
		for entry in d.entries:
			post_url = entry.link
			existing_post = memcache.get(post_url)
			if existing_post is not None:
				logging.info("skipping %s in memcache", post_url)
				existing_posts += 1
				continue
			existing_post = BlogPost.query(BlogPost.post_url == post_url).fetch(1)
			
			# fetch images and parse data only if we have to
			if not existing_post:
				new_posts += 1

				post_title = entry.title
				post_description = parse_entry_description(entry.description)
				post_date_published = datetime.fromtimestamp(mktime(entry.published_parsed)) if ("published_parsed" in entry.keys()) else None
				post_image_url = find_image(post_url)
				post = BlogPost(blog_url = blog_url,
							blog_feed_url = blog_feed_url,
							blog_name = blog_name,
							post_url = post_url,
							post_title = post_title,
							post_description = post_description,
							post_image_url = post_image_url,
							post_date_published = post_date_published)
				logging.info("inserting %s", post_url)
				post.put()
				memcache.add(post_url, post, 7200)
			else:
				logging.info("skipping %s", post_url)
				existing_posts += 1
				memcache.add(post_url, existing_post, 7200)
		return json.dumps({"response" : {"new" : new_posts,
										"existing" : existing_posts,
										"errors" : 0,
										"error_feed" : []}})
	except Exception, e:
		logging.warning("error parsing feed %s", e)
		return json.dumps({"response" : {"new" : new_posts,
								"existing" : existing_posts,
								"errors" : 1,
								"error_feed" : [feed_url]}})

def fetch_recipe_feed_entries_new(feed_url):
	logging.info("fetchies entries for %s", feed_url)
	new_posts = 0
	existing_posts = 0
	errors = 0
	try:
		d = feedparser.parse(feed_url)
		blog_url = d.feed.link
		blog_feed_url = feed_url
		blog_name = d.feed.title
		posts = []
		for entry in d.entries:
			post_url = entry.link
			existing_post = memcache.get(post_url)
			if existing_post is not None:
				logging.info("skipping %s in memcache", post_url)
				existing_posts += 1
				continue
			existing_post = WebPage.query(WebPage.page_url == post_url).fetch(1)
			
			# fetch images and parse data only if we have to
			if not existing_post:
				new_posts += 1

				post_title = entry.title
				post_description = parse_entry_description(entry.description)
				post_date_published = datetime.fromtimestamp(mktime(entry.published_parsed)) if ("published_parsed" in entry.keys()) else None
				
				logging.info("getting soup")
				soup = get_soup_from_url(post_url)
				if soup is None:
					logging.warning("issue parsing html for %s", post_url)
					errors += 1
					continue
				post_image_url = find_image(post_url, soup)
				post_recipe_ingredients = getRecipeIngredientsFromSoup(soup)
				post_recipe_instructions = getRecipeInstructionsFromSoup(soup)

				web_page = WebPage(site_url = blog_url,
									site_feed_url = blog_feed_url,
									site_name = blog_name,
									page_url = post_url,
									page_title = post_title,
									page_description = post_description,
									page_image_url = post_image_url,
									page_date_published = post_date_published,
									page_recipe_ingredients = post_recipe_ingredients,
									page_recipe_instructions = post_recipe_instructions)

				logging.info("inserting %s", post_url)
				web_page.put()
				memcache.add(post_url, web_page)
			else:
				logging.info("skipping %s", post_url)
				existing_posts += 1
				memcache.add(post_url, existing_post)
		return json.dumps({"response" : {"new" : new_posts,
										"existing" : existing_posts,
										"errors" : 0,
										"error_feed" : []}})
	except Exception, e:
		logging.warning("error parsing feed %s", e)
		return json.dumps({"response" : {"new" : new_posts,
								"existing" : existing_posts,
								"errors" : 1,
								"error_feed" : [feed_url]}})


def parse_entry_description(description):
	soup = BeautifulSoup(trim(description))
	return "\n\n".join(soup.stripped_strings)

# Create a 'news feed' of the latest recipes
def get_latest_recipes(curs):
	posts, next_curs, more = BlogPost.query().order(-BlogPost.post_date_published).fetch_page(50, start_cursor=curs)
	posts = [post.to_dict() for post in posts]
	results = {"recipes" : posts,
				"next_page" : ("http://recipe-api.appspot.com/latest_recipes/?cursor=" + next_curs.urlsafe() if (next_curs and more) else "")}
	return json.dumps(results, default = date_handler)

def get_latest_recipes_new(curs):
	posts, next_curs, more = WebPage.query().order(-WebPage.page_date_published).fetch_page(50, start_cursor=curs)
	posts = [post.to_dict() for post in posts]
	results = {"recipes" : [{"recipe" : post} for post in posts],
				"next_page" : ("http://recipe-api.appspot.com/latest_recipes/?cursor=" + next_curs.urlsafe() if (next_curs and more) else "")}
	return json.dumps(results, default = date_handler)


def date_handler(obj):
	return obj.isoformat() if  hasattr(obj, 'isoformat') else obj


# Get/add RSS feeds to regularly check
def add_feed(url):
	blog_feed = BlogFeed(feed_url = url)
	existing_blog_feed = BlogFeed.query(BlogFeed.feed_url == url).fetch(1)
	if not existing_blog_feed:
		logging.info("inserting %s", url) 
		blog_feed.put()
		return json.dumps({"response" : {"added" : 1,
										"ignored" : 0}})
	else:
		logging.info("skipping %s with datastore entry %s", url, existing_blog_feed)
		return json.dumps({"response" : {"added" : 0,
										"ignored" : 1}})

def get_feeds():
	feeds = [feed.to_dict() for feed in BlogFeed.query().fetch()]
	return json.dumps({"feeds" : feeds})

def add_recipe_feed_set():
	feed_urls = feeds
	new_feeds = 0
	existing_feeds = 0
	for feed_url in feed_urls:
		result = json.loads(add_feed(feed_url))
		new_feeds += result["response"]["added"]
		existing_feeds += result["response"]["ignored"]
	return json.dumps({"response" : {"new" : new_feeds,
									"existing" : existing_feeds}})

