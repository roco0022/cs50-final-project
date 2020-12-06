import os
import re
import cs50
import ctypes

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session,jsonify, url_for
from flask_session import Session
from flask import Flask
from tempfile import mkdtemp
from flask_jsglue import JSGlue
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup
from selenium import webdriver
from datetime import date

# Configure application
app = Flask(__name__)
jsglue = JSGlue(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///C:/Users/Administrator/Documents/vsc/cs50x/finalproject.db")

# Make sure API key is set
if not os.environ.get("GOOGLE_API_KEY"):
    raise RuntimeError("GOOGLE_API_KEY not set")
if not os.environ.get("TM_API_KEY"):
    raise RuntimeError("TM_API_KEY not set")
if not os.environ.get("WETHER_API_KEY"):
    raise RuntimeError("WETHER_API_KEY not set")

#get corrent date    
today = str(date.today())

# Home index
@app.route("/")
@login_required
def index():
    # check if the wether API KEY is set.
    if not os.environ.get("WETHER_API_KEY"):
        raise RuntimeError("WETHER_API_KEY not set")

    #split and convert the date in int
    date = today.split('-')
    new_date = ""
    for dates in date:
        new_date = new_date + dates
    int_date = int(new_date)

    # Delete any event that aready passed
    db.execute("INSERT INTO deletesEvents (id, event, location, date, int_date) \
                SELECT id, event, location, date, int_date FROM events \
                WHERE id=:id AND int_date<:int_date", id=session["user_id"], int_date=int_date)

    db.execute("DELETE  FROM events WHERE id=:id AND int_date<:int_date", id=session["user_id"], int_date=int_date)

    myEvent = db.execute("SELECT * FROM events WHERE id=:id ORDER BY int_date ASC LIMIT 5", id=session["user_id"])
    
    
    return render_template("index.html", wether_key=os.environ.get("WETHER_API_KEY"), myEvent=myEvent)

# Events
@app.route("/events")
@login_required
def events():

    # check if the ticket Master API KEY is set.
    if not os.environ.get("TM_API_KEY"):
        raise RuntimeError("TM_API_KEY not set")

    # check if the Google API KEY is set.
    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY not set")

    return render_template("events.html", tm_key=os.environ.get("TM_API_KEY"),google_key=os.environ.get("GOOGLE_API_KEY"))

# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", 
                            username=request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and / or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# Change user password
@app.route("/changePassword", methods=["GET", "POST"])
def changePassword():

    #Change user password
    if request.method == "POST":
        # Ensure old password was submitted
        if not request.form.get("oldpassword"):
            return apology("Must provide the old password", 403)

        # Ensure new password was submitted
        elif not request.form.get("newpassword"):
            return apology("Must provide the new password", 403)

        # check if the passwords match
        elif request.form.get("newpassword") != request.form.get("cpassword"):
            return apology("New Password doesn't match")

        rows = db.execute("SELECT * FROM users WHERE id = :id",
                         id=session["user_id"])

        # Ensure that password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("oldpassword")):
            return apology("Invalid old password", 403)

        hash = generate_password_hash(request.form.get("newpassword"))

        #Update the new password
        db.execute("UPDATE users SET hash = :hash WHERE id = :id",  hash = hash, id=session["user_id"])

        return render_template("passwordChangeSuccess.html")

    else:
        return render_template("changePassword.html")

# logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# Register page.
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # make sure that enter a username
        if request.form.get("username") == "":
            return apology("Must enter username")

        # make sure that enter a password
        elif request.form.get("password") == "":
            return apology("Must enter password")

        # check if the passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Password doesn't match")

        # hash the user password
        hash = generate_password_hash(request.form.get("password"))

        # check if is a new user 
        new_user_check = db.execute("SELECT username from users WHERE username=:username",\
        username=request.form.get("username"))

        # check if the username already exist
        if new_user_check:
            return apology("Username already exist")

        new_user_check = db.execute("SELECT email from users WHERE email=:email",\
        email=request.form.get("email"))

        # check if the user email already exist
        if new_user_check:
            return apology("Email already exist")

        #insert a new user
        result = db.execute("INSERT INTO users (username, email, hash) VALUES(:username, :email, :hash)",\
        username=request.form.get("username"), email=request.form.get("email"), hash = hash)

        session["user_id"] = result

        return render_template("registed.html")

    else:
        return render_template("register.html")

# Places
@app.route("/places")
@login_required
def places():
    """Render map."""
    # Ensure the Google API was set.
    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY not set")

    return render_template("places.html", key=os.environ.get("GOOGLE_API_KEY"))

# Look up articles for geo.
@app.route("/articles")
def articles():
    """Look up articles for geo."""

    geo = request.args.get("geo")

    #if not geo, not argument, raise RunTimeError
    if not geo:
        raise RuntimeError("Not article")

    #lookup, search for article in geo
    print(lookup(geo))
    articles = lookup(geo)

    #return up to 5 articles
    if len(articles) > 5:
        return jsonify([articles[0], articles[1], articles[2], articles[3], articles[4]])

    else:
        return jsonify(articles)

# Search for places that match query.
@app.route("/search")
def search():
    """Search for places that match query."""

    #get q from the user input
    q = request.args.get("q") + "%"

    #search for places that match with q
    places = db.execute("SELECT * FROM places WHERE postal_code LIKE :q OR place_name LIKE :q OR admin_name1 LIKE :q", q=q)

    #show up to 10 places
    if len(places) > 10:
        return jsonify([places[0], places[1], places[2], places[3], places[4], places[5], places[6], places[7], places[8], places[9]])

    else:
        return jsonify(places)

# Find up to 10 places within view.
@app.route("/update")
def update():
    """Find up to 10 places within view."""

    # ensure parameters are present
    if not request.args.get("sw"):
        raise RuntimeError("missing sw")
    if not request.args.get("ne"):
        raise RuntimeError("missing ne")

    # ensure parameters are in lat,lng format
    if not re.search(r"^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("sw")):
        raise RuntimeError("invalid sw")
    if not re.search(r"^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("ne")):
        raise RuntimeError("invalid ne")

    # explode southwest corner into two variables
    (sw_lat, sw_lng) = [float(s) for s in request.args.get("sw").split(",")]

    # explode northeast corner into two variables
    (ne_lat, ne_lng) = [float(s) for s in request.args.get("ne").split(",")]

    # find 10 cities within view, pseudorandomly chosen if more within view
    if (sw_lng <= ne_lng):

        # doesn't cross the antimeridian
        rows = db.execute("""SELECT * FROM places
            WHERE :sw_lat <= latitude AND latitude <= :ne_lat AND (:sw_lng <= longitude AND longitude <= :ne_lng)
            GROUP BY country_code, place_name, admin_code1
            ORDER BY RANDOM()
            LIMIT 10""",
            sw_lat=sw_lat, ne_lat=ne_lat, sw_lng=sw_lng, ne_lng=ne_lng)

    else:

        # crosses the antimeridian
        rows = db.execute("""SELECT * FROM places
            WHERE :sw_lat <= latitude AND latitude <= :ne_lat AND (:sw_lng <= longitude OR longitude <= :ne_lng)
            GROUP BY country_code, place_name, admin_code1
            ORDER BY RANDOM()
            LIMIT 10""",
            sw_lat=sw_lat, ne_lat=ne_lat, sw_lng=sw_lng, ne_lng=ne_lng)

    # output places as JSON
    return jsonify(rows)

#Saved eventes yn a database
@app.route("/events/save", methods=["POST"])
def save():

    req = request.get_json()

    # select the events from the user
    new_event = db.execute("SELECT * FROM events WHERE id=:id", id = session["user_id"])
    
    for event_check in new_event:

        # check if the event already exist
        if (event_check['event'] == req['eventName'] and event_check['location'] == req['location'] and event_check['date'] == req['date']):
            ctypes.windll.user32.MessageBoxW(0, "Event already exists!", "Event", 0)
            return render_template("events.html")
    
    # convert string date in a integer
    date_str = req['date']
    date = date_str.split('-')
    new_date = ""
    for dates in date:
        new_date = new_date + dates
    int_date = int(new_date)

    # insert new event in the database
    db.execute("INSERT INTO events (id, event, location, date, int_date) VALUES(:id, :event, :location, :date, :int_date)", \
                    id=session["user_id"], event=req['eventName'], location=req['location'], date=req['date'], int_date=int_date)
        
    return render_template("events.html")

# Display My Events
@app.route("/myEvents")
@login_required
def myEvents():
    """Show my events"""

    # select the 5 closes events
    myEvent = db.execute("SELECT * from events WHERE id=:id ORDER BY int_date ASC", id=session["user_id"])
    
    return render_template("myEvents.html", myEvent=myEvent)

# Delete events
@app.route("/myEvents/delete/<int:event_id>", methods = ['GET'])
def delete(event_id):
    """Deleting Events"""

    # insert in delete events table the event that going to be delete
    db.execute("INSERT INTO deletesEvents (id, event_id, event, location, date, int_date) \
                SELECT id, event_id, event, location, date, int_date FROM events WHERE event_id=%s", (event_id))

    # deleting a event
    db.execute("DELETE FROM events WHERE event_id=%s", (event_id))
    
    return redirect("/myEvents")

# Restoring events
@app.route("/myEvents/restore/<int:event_id>", methods = ['GET'])
def restore(event_id):

    # restore a event    
    db.execute("INSERT INTO events (id, event, location, date, int_date) \
                SELECT id, event, location, date, int_date FROM deletesEvents WHERE event_id=%s", (event_id))

    db.execute("DELETE FROM deletesEvents WHERE event_id=%s", (event_id))

    return redirect("/deleteEvents")

#My Deletes events
@app.route("/deleteEvents")
def deleteEvents():

    # select the user delete events
    myEvent = db.execute("SELECT * from deletesEvents WHERE id=:id", id=session["user_id"])
    
    return render_template("deleteEvents.html", myEvent=myEvent)

# Empty the delete events table
@app.route("/deleteEvents/deleteTable")
def deleteTable():
 
    # delete all the events in the delete event table from the user
    db.execute("DELETE FROM deletesEvents WHERE id=:id", id=session["user_id"])

    return render_template("deleteEvents.html")

# Error Handler
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
