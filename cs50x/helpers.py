import os
import csv
import feedparser
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

# Render message as an apology to user.
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Looks up articles for geo.
def lookup(geo):
    """Looks up articles for geo."""

    # check cache for geo
    if geo in lookup.cache:
        return lookup.cache[geo]

    # get feed from Google
    feed = feedparser.parse("http://news.google.com/news?geo={}&output=rss".format(urllib.parse.quote(geo, safe="")))

    # if no items in feed, get feed from Onion
    if not feed["items"]:
        feed = feedparser.parse("http://www.theonion.com/feeds/rss")

    # cache results
    lookup.cache[geo] = [{"link": item["link"], "title": item["title"]} for item in feed["items"]]

    # return results
    return lookup.cache[geo]

# initialize cache
lookup.cache = {}
