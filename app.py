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
app.secret_key = config.secret_key  # Secret key for session management

# Function to check if a user is logged in
# If not logged in, return 403 Forbidden error

def check_login():
    if "user_id" not in session:
        abort(403)

# Route for homepage - displays all entries
@app.route("/")
def index():
    all_entries = entries.get_entries()
    return render_template("index.html", entries=all_entries)

# Route to display a specific user's profile and their entries
@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    user_entries = users.get_entries(user_id)
    return render_template("show_user.html", user=user, entries=user_entries)

# Route to search for entries using query, group, or category filters
@app.route("/find_entry")
def find_entry():
    query = request.args.get("query", "").strip()
    
    # Get selected group and category IDs as lists
    group_ids = request.args.getlist("group_id")
    category_ids = request.args.getlist("category_id")
    
    # Convert them to integers (if valid)
    group_ids = [int(g) for g in group_ids if g.isdigit()]
    category_ids = [int(c) for c in category_ids if c.isdigit()]

    results = entries.find_entries(query, group_ids, category_ids)
    
    # Fetch all available groups and categories for filtering
    all_groups = groups.get_groups()
    all_categories = db.query("SELECT * FROM categories")

    return render_template(
        "find_entry.html",
        query=query,
        results=results,
        all_groups=all_groups,
        all_categories=all_categories,
        selected_groups=group_ids,
        selected_categories=category_ids
    )

# Route to display a specific entry and its assigned groups
@app.route("/entry/<int:entry_id>")
def show_entry(entry_id):
    entry = entries.get_entry(entry_id)
    if not entry:
        abort(404)
    
    entry_groups = entries.get_entry_groups(entry_id)
    return render_template("show_entry.html", entry=entry, entry_groups=entry_groups)

# Route to display new group creation form
@app.route("/new_group")
def new_group():
    check_login()
    return render_template("new_group.html")

# Route to create a new group
@app.route("/create_group", methods=["POST"])
def create_group():
    check_login()
    name = request.form["group_name"]
    if not name or len(name) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    user_id = session["user_id"]
    
    try:
        groups.add_group(name, description)
    except sqlite3.IntegrityError:
        return "ERROR: Group already exists <br> <a href='/'>return to main page</a>"
    
    users.role_on_create_group(user_id, name)
    return "Group created <br> <a href='/'>return to main page</a>"

# Route to display new category creation form
@app.route("/new_category")
def new_category():
    check_login()
    return render_template("new_category.html")

# Route to create a new category
@app.route("/create_category", methods=["POST"])
def create_category():
    check_login()
    name = request.form["category_name"]
    if not name or len(name) > 50:
        abort(403)
    categories.add_category(name)
    return redirect("/")

# Route to display new entry form
@app.route("/new_entry")
def new_entry():
    check_login()
    all_categories = categories.get_categories()
    all_groups = groups.get_groups()
    return render_template("new_entry.html", categories=all_categories, groups=all_groups)

# Route to create a new entry
@app.route("/create_entry", methods=["POST"])
def create_entry():
    check_login()
    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    date = request.form["date"]
    time = request.form["time"]
    duration = request.form["duration"]
    user_id = session["user_id"]
    
    category_id = request.form["category"]
    entry_id = entries.add_entry(title, description, date, time, duration, user_id, category_id)
    
    if not entry_id:
        return "Error: Could not create entry", 500
    
    group_ids = request.form.getlist("groups")
    entries.assign_entry_to_groups(entry_id, group_ids)
    
    return redirect("/")

# Route to display entry edit form
@app.route("/edit_entry/<int:entry_id>")
def edit_entry(entry_id):
    check_login()
    entry = entries.get_entry(entry_id)
    if not entry:
        abort(404)
    if entry["user_id"] != session["user_id"]:
        abort(403)
    
    all_categories = categories.get_categories()
    all_groups = groups.get_groups()
    entry_group_ids = groups.get_entry_group_ids(entry_id)
    return render_template("edit_entry.html", entry=entry, categories=all_categories, all_groups=all_groups, entry_group_ids=entry_group_ids)

# Route to update an existing entry
@app.route("/update_entry", methods=["POST"])
def update_entry():
    entry_id = request.form["entry_id"]
    entry = entries.get_entry(entry_id)
    if not entry:
        abort(404)
    if entry["user_id"] != session["user_id"]:
        abort(403)
    
    title = request.form["title"]
    description = request.form["description"]
    date = request.form["date"]
    time = request.form["time"]
    duration = request.form["duration"]
    category_id = request.form["category"]
    
    entries.update_entry(entry_id, title, description, date, time, duration, category_id)
    new_group_ids = set(request.form.getlist("groups"))
    groups.update_entry_groups(entry_id, new_group_ids)
    
    return redirect("/entry/" + str(entry_id))

# Route to logout user
@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")
