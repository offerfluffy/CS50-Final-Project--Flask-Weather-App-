from flask import Flask, render_template, request, session, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from cs50 import SQL
from datetime import datetime

from helpers import get_weather, login_required

db = SQL("sqlite:///wether.db")

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.template_filter('datetimeformat')
def datetimeformat(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%H:%M:%S')

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":

        city = request.form.get("city")

        if not city:
            flash("Enter the city")

        response = get_weather(city)

        if "error" in response:
            flash(f"{response['error']}")
            return redirect("/")
        
        recent_searches = session.get("recent_searches", [])

        city_weather_data = {
            "city": response["city"],
            "country": response["country"],
            "temperature": response["main"]["temperature"],
            "description": response["weather"]["description"],
            "icon": response["weather"]["icon"],
            "coordinates": response["coordinates"],
        }

        if city_weather_data not in recent_searches:
            if len(recent_searches) >= 3:  
                recent_searches.pop(0)
            recent_searches.append(city_weather_data)

        session["recent_searches"] = recent_searches

        return render_template("weather.html", info = response)

    else:
        return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            flash("Must provide username")
            return redirect("/login")

        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect("/login")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password")
            return redirect("/login")

        session["user_id"] = rows[0]["id"]

        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            flash("Must provide username") 
            return redirect("/register")

        elif not request.form.get("password"):
            flash("Must provide password") 
            return redirect("/register")

        elif not request.form.get("confirmation"):
            flash("Must provide password confirmation") 
            return redirect("/register")

        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Password and password confirmation must be identical") 
            return redirect("/register")

        try:
            db.execute(
                "INSERT INTO users (username, hash) VALUES(?, ?)",
                request.form.get("username"),
                generate_password_hash(request.form.get("confirmation"), method="pbkdf2:sha256"),
            )
        except ValueError:
            flash("Username is already used")
            return redirect("/register")

        session["user_id"] = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )[0]["id"]

        return redirect("/")
    else:
        return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
