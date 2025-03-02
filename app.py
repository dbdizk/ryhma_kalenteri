import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session
import secrets
import config
import db
import entries
import users
import categories
import groups
import rsvps
import re


app = Flask(__name__)
app.secret_key = config.secret_key

def check_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    user_id = session.get("user_id")

    # Fetch events
    all_entries = entries.get_entries(user_id)

    # Fetch RSVP statuses if logged in
    user_rsvp_status = {}
    if user_id:
        for entry in all_entries:
            user_rsvp_status[entry["id"]] = rsvps.get_user_rsvp(user_id, entry["id"])

    # Organize entries by group
    grouped_entries = {}
    for entry in all_entries:
        group_name = entry["group_name"] if entry["group_name"] else "Public Events"
        if group_name not in grouped_entries:
            grouped_entries[group_name] = []
        grouped_entries[group_name].append(entry)

    return render_template("index.html", grouped_entries=grouped_entries, user_rsvp_status=user_rsvp_status)



@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)

    user_entries = users.get_entries(user_id)
    total_entries = entries.count_user_entries(user_id) # This exists just because week 3 feedback told to use aggregate functions
    user_groups = groups.get_user_groups(user_id)

    return render_template(
        "show_user.html",
        user=user,
        entries=user_entries,
        total_entries=total_entries,
        user_groups=user_groups
    )


@app.route("/rsvp", methods=["POST"])
def rsvp():
    check_login()
    check_csrf()
    user_id = session["user_id"]
    entry_id = request.form["entry_id"]
    status = request.form["status"].strip().lower()

    # Validation
    if status not in ["attending", "maybe", "not attending"]:
        return "Error: Invalid RSVP status."

    rsvps.add_rsvp(user_id, entry_id, status)
    return redirect(f"/entry/{entry_id}")


@app.route("/group/<int:group_id>")
def show_group(group_id):
    check_login()
    user_id = session["user_id"]
    group = groups.get_group(group_id)
    if not group:
        abort(404)

    user_groups = groups.get_user_group_ids(user_id)

    if group_id not in user_groups:
        return "Error: You do not have permission to view this group", 403

    group_members = users.get_users_in_group_with_roles(group_id)
    group_entries = entries.get_entries_by_group(group_id)

    return render_template("show_group.html", group=group, members=group_members, entries=group_entries)


@app.route("/manage_groups")
def manage_groups():
    check_login()
    user_id = session["user_id"]

    # Fetch only groups where the user is an admin
    admin_groups = groups.get_admin_groups(user_id)

    if not admin_groups:
        return "Error: You are not an admin of any group <br> <a href='/'>Return to main page</a>"

    all_users = users.get_all_users()

    # Attach members and roles for each group
    for group in admin_groups:
        group["members"] = users.get_users_in_group_with_roles(group["id"])  # ✅ Now this works!

    return render_template("manage_groups.html", groups=admin_groups, users=all_users)




@app.route("/add_user_to_group", methods=["POST"])
def add_user_to_group():
    check_login()
    check_csrf()
    user_id = request.form.get("user_id")
    group_id = request.form.get("group_id")

    # Ensure both user and group exist
    if not users.get_user(user_id):
        return "Error: User does not exist <br> <a href='/manage_groups'>Return to group management</a>"
    if not groups.get_group(group_id):
        return "Error: Group does not exist <br> <a href='/manage_groups'>Return to group management</a>"

    # Add user to group
    result = groups.add_user_to_group(user_id, group_id)

    return redirect("/manage_groups")

@app.route("/remove_user_from_group", methods=["POST"])
def remove_user_from_group():
    check_login()
    check_csrf()
    admin_id = session["user_id"]
    user_id = request.form["user_id"]
    group_id = request.form["group_id"]

    # Ensure the admin has permission to remove users
    if not groups.is_user_admin(admin_id, group_id):
        return "Error: You do not have permission to remove members from this group <br> <a href='/'>Return to main page</a>"

    # Prevent admins from removing themselves
    if admin_id == user_id:
        return "Error: Admins cannot remove themselves <br> <a href='/manage_groups'>Return to group management</a>"

    groups.remove_user_from_group(user_id, group_id)

    return redirect("/manage_groups")

@app.route("/change_user_role", methods=["POST"])
def change_user_role():
    check_login()
    check_csrf()
    admin_id = session["user_id"]
    user_id = request.form["user_id"]
    group_id = request.form["group_id"]
    new_role = request.form["new_role"]

    # Ensure the admin has permission to change roles
    if not groups.is_user_admin(admin_id, group_id):
        return "Error: You do not have permission to change roles in this group <br> <a href='/'Return to main page</a>"

    # Prevent users from changing their own role
    if admin_id == int(user_id):
        return "Error: You cannot change your own role <br> <a href='/manage_groups'>Return to group management</a>"

    groups.change_user_role(user_id, group_id, new_role)

    return redirect("/manage_groups")





@app.route("/find_entry")
def find_entry():
    query = request.args.get("query", "").strip()
    group_ids = request.args.getlist("group_id")
    category_ids = request.args.getlist("category_id")

    # Convert IDs to integers
    group_ids = [int(g) for g in group_ids if g.isdigit()]
    category_ids = [int(c) for c in category_ids if c.isdigit()]

    user_id = session.get("user_id")

    # Fetch only allowed entries
    results = entries.find_entries(query, group_ids, category_ids, user_id)

    all_groups = groups.get_groups()
    all_categories = categories.get_categories()

    return render_template(
        "find_entry.html",
        query=query,
        results=results,
        all_groups=all_groups,
        all_categories=all_categories,
        selected_groups=group_ids,
        selected_categories=category_ids
    )


    

@app.route("/entry/<int:entry_id>")
def show_entry(entry_id):
    entry = entries.get_entry(entry_id)
    if not entry:
        abort(404)

    entry_groups = entries.get_entry_groups(entry_id)

    # If the event has groups, enforce access restrictions
    if entry_groups:
        if "user_id" not in session:  # Require login for group events
            return "Error: You must be logged in to view this entry", 403

        user_id = session["user_id"]
        user_group_ids = set(groups.get_user_group_ids(user_id))
        entry_group_ids = {group["id"] for group in entry_groups}

        # If the user is not in any of the entry’s groups, deny access
        if not entry_group_ids.intersection(user_group_ids):
            return "Error: You do not have permission to view this entry", 403

    # Fetch RSVP details if logged in
    user_rsvp = None
    event_rsvps = []
    if "user_id" in session:
        user_rsvp = rsvps.get_user_rsvp(session["user_id"], entry_id)
        event_rsvps = rsvps.get_event_rsvps(entry_id)

    return render_template("show_entry.html", entry=entry, entry_groups=entry_groups, user_rsvp=user_rsvp, event_rsvps=event_rsvps)







@app.route("/new_group")
def new_group():
    check_login()
    return render_template("new_group.html")

@app.route("/create_group", methods=["POST"])
def create_group():
    check_login()
    check_csrf()
    name = request.form["group_name"].strip()
    description = request.form["description"].strip()

    # Validation
    if not name or len(name) < 3 or len(name) > 50:
        return "Error: Group name must be between 3 and 50 characters."
    if len(description) > 1000:
        return "Error: Description cannot exceed 1000 characters."

    user_id = session["user_id"]
    try:
        groups.add_group(name, description, user_id)
    except sqlite3.IntegrityError:
        return "Error: Group already exists."

    return redirect("/")



@app.route("/new_category")
def new_category():
    check_login()
    return render_template("new_category.html")

@app.route("/create_category", methods=["POST"])
def create_category():
    check_login()
    check_csrf()
    name = request.form["category_name"]
    if not name or len(name) > 50:
        abort(403)
    categories.add_category(name)
    return redirect("/")

@app.route("/new_entry")
def new_entry():
    check_login()
    user_id = session["user_id"]
    all_categories=categories.get_categories()
    user_groups = groups.get_user_groups(user_id)
    return render_template("new_entry.html", categories=all_categories, groups=user_groups)

@app.route("/create_entry", methods=["POST"])
def create_entry():
    check_login()
    check_csrf()
    user_id = session["user_id"]

    # Strip whitespace from user inputs
    title = request.form["title"].strip()
    description = request.form["description"].strip()
    date = request.form["date"].strip()
    time = request.form["time"].strip()
    duration = request.form["duration"].strip()
    category_id = request.form["category"].strip()

    # Validate title
    if not title or len(title) > 50:
        return "Error: Title must be between 1 and 50 characters.<br> <a href='/new_entry'>Return to entry creation</a>"

    # Validate description
    if not description or len(description) > 1000:
        return "Error: Description cannot exceed 1000 characters.<br> <a href='/new_entry'>Return to entry creation</a>"

    # Validate date format (YYYY-MM-DD)
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        return "Error: Invalid date format. Use YYYY-MM-DD.<br> <a href='/new_entry'>Return to entry creation</a>"

    # Validate time format (HH:MM)
    if not re.match(r"^\d{2}:\d{2}$", time):
        return "Error: Invalid time format. Use HH:MM.<br> <a href='/new_entry'>Return to entry creation</a>"

    # Validate duration (must be a number: int or float)
    if not re.match(r"^\d+(\.\d+)?$", duration):
        return "Error: Duration must be a valid number.<br> <a href='/new_entry'>Return to entry creation</a>"

    # Validate category_id (must be a number)
    if not category_id.isdigit():
        return "Error: Invalid category selection.<br> <a href='/new_entry'>Return to entry creation</a>"

    # Convert category_id to integer
    category_id = int(category_id)

    # Get selected groups and validate
    selected_groups = set(map(int, request.form.getlist("groups")))
    user_group_ids = set(groups.get_user_group_ids(user_id))


    # Ensure user can only assign to groups they belong to
    if not selected_groups.issubset(user_group_ids):
        return "Error: You cannot add an entry to a group you do not belong to.<br> <a href='/new_entry'>Return to entry creation</a>"

    # Create the entry
    entry_id = entries.add_entry(title, description, date, time, duration, user_id, category_id)
    
    if not entry_id:
        return "Error: Could not create entry", 500  # Stop execution if entry creation fails

    # Assign entry to groups
    entries.assign_entry_to_groups(entry_id, selected_groups)

    return redirect("/")


@app.route("/edit_entry/<int:entry_id>")
def edit_entry(entry_id):
    check_login()
    user_id = session["user_id"]
    entry = entries.get_entry(entry_id)
    all_categories = categories.get_categories()
    if not entry:
        abort(404)
    if entry["user_id"] != session["user_id"]:
        abort(403)
    user_groups = groups.get_user_groups(user_id)
    entry_group_ids = groups.get_entry_group_ids(entry_id)
    return render_template("edit_entry.html", entry=entry, categories=all_categories, all_groups=user_groups, entry_group_ids=entry_group_ids)

@app.route("/update_entry", methods=["POST"])
def update_entry():
    check_login()
    check_csrf()
    user_id = session["user_id"]
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
    selected_groups = set(map(int, request.form.getlist("groups")))
    user_group_ids = set(groups.get_user_group_ids(user_id))

    if not selected_groups.issubset(user_group_ids):
        return "Error: You cannot assign this entry to a group you do not belong to"

    entries.update_entry(entry_id, title, description, date, time, duration, category_id)
    new_group_ids = set(request.form.getlist("groups"))
    groups.update_entry_groups(entry_id, new_group_ids)

    return redirect("/entry/" + str(entry_id))


@app.route("/confirm_delete", methods=["POST"])
def confirm_delete():
    check_csrf()
    entry_id = request.form["entry_id"]
    password = request.form["password"]

    if users.check_password(session["user_id"], password):
        entries.delete_entry(entry_id)
        return redirect("/")
    else:
        return f"ERROR: Wrong password <br> <a href='/entry/{entry_id}'>Return to the entry</a>"
    

@app.route("/register")
def register():
    if "user_id" in session:
        return redirect("/")  # Redirect logged-in users to homepage
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    if "user_id" in session:
        return redirect("/")  # Prevent logged-in users from submitting

    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    # Validation
    if not username or len(username) < 3 or len(username) > 20:
        return "Error: Username must be between 3 and 20 characters."
    if len(password1) < 8:
        return "Error: Password must be at least 8 characters long."
    if password1 != password2:
        return "Error: Passwords do not match."

    try:
        user_id = users.create_user(username, password1)
        session["user_id"] = user_id  # Automatically log in
        session["username"] = username
    except sqlite3.IntegrityError:
        return "Error: Username already taken."

    return redirect("/")



@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/")
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        
        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["csrf_token"] = secrets.token_hex(16)
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
