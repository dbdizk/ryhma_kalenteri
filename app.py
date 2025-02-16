import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import entries

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_entries = entries.get_entries()
    return render_template("index.html", entries=all_entries)

@app.route("/find_entry")
def find_entry():
    query = request.args.get("query")
    if query:
        results = entries.find_entries(query)
    else:
        query = ""
        results = []
    return render_template("find_entry.html", query=query, results=results)    

@app.route("/entry/<int:entry_id>")
def show_entry(entry_id):
    entry = entries.get_entry(entry_id)
    return render_template("show_entry.html", entry=entry)


@app.route("/new_entry")
def new_entry():
    return render_template("new_entry.html")


@app.route("/create_entry", methods=["POST"])
def create_entry():
    title=request.form["title"]
    description=request.form["description"]
    date=request.form["date"]
    time=request.form["time"]
    duration=request.form["duration"]
    user_id = session["user_id"]

    entries.add_entry(title,description,date,time,duration,user_id)


    return redirect("/")

@app.route("/edit_entry/<int:entry_id>")
def edit_entry(entry_id):
    entry = entries.get_entry(entry_id)
    return render_template("edit_entry.html", entry=entry)

@app.route("/update_entry", methods=["POST"])
def update_entry():
    entry_id=request.form["entry_id"]
    title=request.form["title"]
    description=request.form["description"]
    date=request.form["date"]
    time=request.form["time"]
    duration=request.form["duration"]

    entries.update_entry(entry_id, title, description, date, time, duration)

    return redirect("/entry/" + str(entry_id))

@app.route("/delete_entry/<int:entry_id>")
def delete_entry(entry_id):
    entry = entries.get_entry(entry_id)
    return render_template("delete_entry.html", entry=entry)

@app.route("/confirm_delete", methods=["POST"])
def confirm_delete():
    entry_id = request.form["entry_id"]
    password = request.form["password"]

    sql = "SELECT password_hash FROM users WHERE id = ?"
    result = db.query(sql, [session["user_id"]])[0]
    password_hash = result["password_hash"]

    if check_password_hash(password_hash, password):
        entries.delete_entry(entry_id)
        return redirect("/")
    else:
        return f"ERROR: Wrong password <br> <a href='/entry/{entry_id}'>Return to the entry</a>"
    

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu <br> <a href='/'>Etusivulle</a>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        
        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])[0]
        user_id = result["id"]
        password_hash = result["password_hash"]
        

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")