from multiprocessing import connection
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

con = sqlite3.connect("animescorer.db")
cur = con.cursor()

@app.route("/")
def index():
    return redirect("/search")

@app.route("/search")
def search():

    q = request.args.get("q")

    if not q:
        flash("please provide some search terms", "message")
        return render_template("search.html")

    limit = 100
    url = f"https://api.jikan.moe/v4/anime?q={q}&limit={limit}"
    response = requests.get(url)
    response.raise_for_status()

    results = response.json()

    titles = []
    for anime in results["data"]:
        titles.append(anime["title_english"])

    return render_template("searchresults.html", results=results)

def login():
    return "login"

@app.route("/register")
def register():
    return "register"