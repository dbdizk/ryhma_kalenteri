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

    
    group_ids = [int(g) for g in group_ids if g.isdigit()]
    category_ids = [int(c) for c in category_ids if c.isdigit()]

    results = entries.find_entries(query, group_ids, category_ids)

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

    

@app.route("/entry/<int:entry_id>")
def show_entry(entry_id):
    entry = entries.get_entry(entry_id)
    if not entry:
        abort(404)
    
    entry_groups = entries.get_entry_groups(entry_id)
    return render_template("show_entry.html", entry=entry,entry_groups=entry_groups)




@app.route("/new_group")
def new_group():
    check_login()
    return render_template("new_group.html")

@app.route("/create_group", methods=["POST"])
def create_group():
    check_login()
    
    name = request.form["group_name"]
    description = request.form["description"]
    creator_id = session["user_id"]

    if not name or len(name) > 50:
        abort(403)
    if not description or len(description) > 1000:
        abort(403)

    try:
        group_id = groups.add_group(name, description, creator_id)
    except sqlite3.IntegrityError:
        return "ERROR: Group already exists <br> <a href='/'>Return to main page</a>"

    return "Group created <br> <a href='/'>return to main page</a>"


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

    selected_groups = set(request.form.getlist("groups"))
    user_group_ids = set(groups.get_user_group_ids(user_id))

    if not selected_groups.issubset(user_group_ids):
        return "Error: You cannot add an entry to a group you do not belong to <br> <a href='/new_entry'>Return to entry creation</a>"
    entry_id = entries.add_entry(title,description,date,time,duration,user_id,category_id)
    
    if not entry_id:
        return "Error: Could not create entry", 500  # Stop execution if entry creation fails

    group_ids=request.form.getlist("groups")
    entries.assign_entry_to_groups(entry_id, group_ids)


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
    selected_groups = set(request.form.getlist("groups"))
    user_group_ids = set(groups.get_user_group_ids(user_id))

    if not selected_groups.issubset(user_group_ids):
        return "Error: You cannot assign this entry to a group you do not belong to"

    entries.update_entry(entry_id, title, description, date, time, duration, category_id)
    new_group_ids = set(request.form.getlist("groups"))
    groups.update_entry_groups(entry_id, new_group_ids)

    return redirect("/entry/" + str(entry_id))


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
        user_id = users.create_user(username, password1)  # Get the new user's ID
        session["user_id"] = user_id  # Automatically log in
        session["username"] = username
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"
    
    return redirect("/")


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
