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
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import memcache
from time import mktime
from datetime import datetime

def trim(s):
	"""
	remove whitespace on left and right of string s.
	trim whitespace between characters to a single space
	"""
	return " ".join(s.split())

def get_soup_from_url(url):
	try:
		request = urllib2.Request(url)

		#try to avoid 403 forbidden errors.  not sure if this actually works
		request.add_header('User-Agent', 'Googlebot')
		logging.debug(request.headers)
		response = urllib2.urlopen(url)
		html = response.read()
		return BeautifulSoup(html)
	except Exception, e:
		logging.warning("error fetching page: %s", e)
		return None

def find_image(url, soup=None):
	logging.info("finding image for %s", url)
	
	cached_image = memcache.get(url)
	if cached_image is not None:
		logging.info("found image_url in cache")
		return cached_image

	if soup is None:
		soup = get_soup_from_url(url)
		if soup is None:
			return None

	# allow author to specify thumbnail.
	# <meta property="og:image" content="http://...">
	# og_image = (soup.find('meta', property='og:image')) or (soup.find('meta', attrs={'name' : 'og:image'}))
	og_image = (soup.find('meta', property=re.compile("og:image", re.IGNORECASE))) or (soup.find('meta', attrs={'name' : re.compile('og:image', re.IGNORECASE)}))
	if og_image and og_image['content']:
		logging.info("og_image")
		logging.debug("adding %s to memcache", og_image['content'])
		memcache.add(url, og_image['content'])
		return og_image['content']

	# <link rel="image_src" href="http://...">
	image_src = soup.find('link', rel=re.compile('image_src', re.IGNORECASE))
	if image_src and image_src['href']:
		logging.info("image_src")
		logging.debug("adding %s to memcache", image_src['href'])
		memcache.add(url, image_src['href'])
		return image_src['href']

	# no guidance from author, look for largest image
	max_area = 0
	max_url = None

	for image_url in extract_image_urls(url, soup):
		logging.info("testing %s", image_url)

		#ignore image_urls with logo or icon in name
		if "logo" in image_url or "icon" in image_url:
			logging.info("ignore logo %s", image_url)
			continue

		#ignore image_urls with sharing options in name
		if ("facebook" in image_url or "twitter" in image_url or 
		"instagram" in image_url or "pinterest" in image_url or "email" in image_url or "subscribe" in image_url):
			logging.info("ignore social sharing image %s", image_url)
			continue

		#ignore avatars
		if "avatar" in image_url.lower():
			logging.info("ignore avatar")

		#resolve url to absolute url
		if image_url.startswith('//'):
			image_url = coerce_url_to_protocol(image_url)

		size = fetch_image_size(image_url)
		if not size:
			continue

		area = size[0] * size[1]

		#ignore little images
		if area < 5000:
			logging.info("ignore little %s", image_url)
			continue

		#ignore excessively long/wide images
		if max(size) / min(size) > 1.5:
			logging.info("ignore dimensions %s", image_url)

		#penalize images with "sprite in their name"
		if 'sprite' in image_url.lower():
			logging.info("penalizing sprinte %s", image_url)
			area /= 10

		if area > max_area:
			max_area = area
			max_url = image_url
	logging.info("largest image")
	logging.debug("adding %s to memcache", max_url)
	memcache.add(url, max_url)
	return max_url

def extract_image_urls(url, soup):
	for img in soup.findAll('img', src=True):
		yield urlparse.urljoin(url, img['src'])

def fetch_image_size(image_url):
	logging.info("fetching image size for %s", image_url)
	response = None
	parser = ImageFile.Parser()
	try:
		response = urllib2.urlopen(image_url)
		while True:
			chunk = response.read(1024)
			if not chunk:
				break
			parser.feed(chunk)
			if parser.image:
				logging.debug("size: %s", parser.image.size)
				return parser.image.size
	except Exception, e:
		logging.info("error accessing %s: %s", image_url, e)
		return None
	finally:
		if response:
			response.close()

def find_title(url, soup=None):
	logging.info("finding title for %s", url)

	if soup is None:
		soup = get_soup_from_url(url)
		if soup is None or soup.html.head is None:
			logging.info("couldn't find head tag")
			return None
	head_soup = soup.html.head

	title = None

	# try to find an og:title meta tag to use
	og_title = (head_soup.find("meta", attrs={"property": "og:title"}) or
				head_soup.find("meta", attrs={"name": "og:title"}))
	if og_title and og_title["content"]:
		logging.info("og_title")
		return og_title["content"]

	# if that failed, look for a <title> tag to use instead
	if head_soup.title and head_soup.title.string:
		logging.info("<title>")
		return head_soup.title.string

	logging.info("couldn't find title")
	return None


