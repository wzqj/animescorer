from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

import sqlite3
import requests
import urllib.parse

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

con = sqlite3.connect("animescorer.db", check_same_thread=False)
cur = con.cursor()

@app.route("/")
def index():
    return redirect("/search")

@app.route("/search")
def search():

    q = request.args.get("q")
    page = request.args.get("page")

    if not q:
        flash("please provide some search terms", "message")
        return render_template("search.html")

    if not page:
        page = ""

    limit = 100
    url = f"https://api.jikan.moe/v4/anime?q={q}&page={page}&limit={limit}"
    response = requests.get(url)
    response.raise_for_status()

    results = response.json()

    titles = []
    for anime in results["data"]:
        titles.append(anime["title_english"])

    return render_template("searchresults.html", q=q, page=page, results=results)

@app.route("/login", methods=["GET", "POST"])
def login():

    # Clear existing sessions
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return "no username entered"
        password = request.form.get("password")
        if not password:
            return "no password entered"

        # Get id of user
        id = cur.execute("SELECT id FROM users WHERE username = (?)", (username,)).fetchone()[0]
        if not id:
            return "user not found"

        # Remember user's id
        session["user_id"] = id
        app.logger.info(id)
        
        return redirect("/")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return "no username entered"
        password = request.form.get("password")
        if not password:
            return "no password entered"
        confirm = request.form.get("confirm")
        if not confirm == password:
            return "passwords do not match"
        
        # Read from db to check if username already exists
        if cur.execute("SELECT * FROM users WHERE username = (?)", (username,)).fetchone():
            return "username already exists"

        cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, generate_password_hash(password)))
        con.commit()

        id = cur.execute("SELECT id FROM users WHERE username = (?)", (username,)).fetchone()
        session["user_id"] = id

        
        return redirect("/")

    return render_template("register.html")
