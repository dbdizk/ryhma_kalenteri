import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session
import config
import db
import entries
import users
import categories
import groups


app = Flask(__name__)
app.secret_key = config.secret_key

def check_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
def index():
    all_entries = entries.get_entries()
    return render_template("index.html", entries=all_entries)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    entries = users.get_entries(user_id)
    return render_template("show_user.html", user=user, entries=entries)

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
    if not entry:
        abort(404)
    return render_template("show_entry.html", entry=entry)


@app.route("/new_entry")
def new_entry():
    check_login()
    all_categories=categories.get_categories()
    return render_template("new_entry.html", categories=all_categories)

@app.route("/new_group")
def new_group():
    check_login()
    return render_template("new_group.html")

@app.route("/create_group", methods=["POST"])
def create_group():
    check_login()
    name = request.form["name"]
    if not name or len(name) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    user_id = session["user_id"]
    groups.add_group(name, description)
    return redirect("/")

@app.route("/new_category")
def new_category():
    check_login()
    return render_template("new_category.html")

@app.route("/create_category", methods=["POST"])
def create_category():
    check_login()
    name = request.form["category_name"]
    if not name or len(name) > 50:
        abort(403)
    categories.add_category(name)
    return redirect("/")

@app.route("/create_entry", methods=["POST"])
def create_entry():
    check_login()
    title=request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description=request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    date=request.form["date"]
    time=request.form["time"]
    duration=request.form["duration"]
    user_id = session["user_id"]

    category_id = request.form["category"]
    group = request.form["group"]
    entries.add_entry(title,description,date,time,duration,user_id,category_id)


    return redirect("/")

@app.route("/edit_entry/<int:entry_id>")
def edit_entry(entry_id):
    check_login()
    entry = entries.get_entry(entry_id)
    all_categories = categories.get_categories()
    if not entry:
        abort(404)
    if entry["user_id"] != session["user_id"]:
        abort(403)
    return render_template("edit_entry.html", entry=entry, categories=all_categories)

@app.route("/update_entry", methods=["POST"])
def update_entry():
    entry_id=request.form["entry_id"]
    entry = entries.get_entry(entry_id)
    if not entry:
        abort(404)
    if entry["user_id"] != session["user_id"]:
        abort(403)

    title=request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description=request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    date=request.form["date"]
    time=request.form["time"]
    duration=request.form["duration"]
    category_id = request.form["category"]

    entries.update_entry(entry_id, title, description, date, time, duration, category_id)

    return redirect("/entry/" + str(entry_id))

# For later use, after implementing user roles properly. WIP.
#@app.route("/delete_category")
#def delete_entry(entry_id):
#    check_login()
#    entry = entries.get_entry(entry_id)
#    if not entry:
#        abort(404)
#    if entry["user_id"] != session["user_id"]:
#        abort(403)
#    return render_template("delete_entry.html", entry=entry)

@app.route("/confirm_delete", methods=["POST"])
def confirm_delete():
    entry_id = request.form["entry_id"]
    password = request.form["password"]

    if users.check_password(session["user_id"], password):
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
    
    try:
        users.create_user(username, password1)
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
        
        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "ERROR: Wrong username or password"

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")