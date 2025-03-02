import db

def add_group(name, description, creator_id):
    sql = "INSERT INTO groups (name, description) VALUES (?, ?)"
    db.execute(sql, [name, description])  # Insert and get new group ID
    group_id= db.last_insert_id()

    # Assign the creator as an admin (role_id = 1)
    sql_assign_admin = "INSERT INTO user_groups (user_id, group_id, role_id) VALUES (?, ?, 1)"
    db.execute(sql_assign_admin, [creator_id, group_id])

    return group_id

def role_on_create_group(user_id, name):
    sql = """
        INSERT INTO user_groups (user_id, group_id, role_id)
        SELECT ?, id, 1 FROM groups WHERE name = ?
    """
    rows_affected = db.execute(sql, [user_id, name])

    # If no rows were inserted, the group name didn't exist
    if rows_affected == 0:
        return None


def is_user_admin(user_id, group_id):
    sql = """SELECT 1 FROM user_groups 
             WHERE user_id = ? AND group_id = ? AND role_id = 1"""
    result = db.query(sql, [user_id, group_id])
    return bool(result)  # True if user is an admin

def get_admin_groups(user_id):
    sql = """SELECT g.id, g.name FROM groups g
             JOIN user_groups ug ON g.id = ug.group_id
             WHERE ug.user_id = ? AND ug.role_id = 1"""
    
    result = db.query(sql, [user_id])

    # Convert to list of dictionaries to allow modification
    return [dict(row) for row in result]



def get_group(group_id):
    sql = "SELECT id, name, description FROM groups WHERE id = ?"
    result = db.query(sql, [group_id])
    return result[0] if result else None

def get_groups():
    sql = "SELECT id, name FROM groups"
    result = db.query(sql)
    
    # Convert result to list of dictionaries for compatibility
    return [dict(row) for row in result]


def get_entry_group_ids(entry_id):
    sql = "SELECT group_id FROM entry_groups WHERE entry_id = ?"
    result = db.query(sql, [entry_id])
    return {g["group_id"] for g in result}

def update_entry_groups(entry_id, new_group_ids):
    old_group_ids = get_entry_group_ids(entry_id)

    # Find groups to add and remove
    groups_to_add = new_group_ids - old_group_ids
    groups_to_remove = old_group_ids - new_group_ids

    # Remove deselected groups
    if groups_to_remove:
        db.execute("DELETE FROM entry_groups WHERE entry_id = ? AND group_id IN ({})".format(
            ",".join(["?"] * len(groups_to_remove))
        ), [entry_id] + list(groups_to_remove))

    # Add newly selected groups
    for group_id in groups_to_add:
        db.execute("INSERT INTO entry_groups (entry_id, group_id) VALUES (?, ?)", [entry_id, group_id])

# Function to check if a user is in a specific group
def is_user_in_group(user_id, group_id):
    sql = "SELECT 1 FROM user_groups WHERE user_id = ? AND group_id = ?"
    result = db.query(sql, [user_id, group_id])
    return bool(result)  # Returns True if user is in the group

# Function to add a user to a group
def add_user_to_group(user_id, group_id):
    if is_user_in_group(user_id, group_id):
        return "User is already in the group"

    sql = "INSERT INTO user_groups (user_id, group_id, role_id) VALUES (?, ?, 3)"
    db.execute(sql, [user_id, group_id])
    return "User added to group successfully"

def remove_user_from_group(user_id, group_id):
    sql = "DELETE FROM user_groups WHERE user_id = ? AND group_id = ?"
    db.execute(sql, [user_id, group_id])

def change_user_role(user_id, group_id, new_role):
    sql = "UPDATE user_groups SET role_id = ? WHERE user_id = ? AND group_id = ?"
    db.execute(sql, [new_role, user_id, group_id])

def get_user_groups(user_id):
    sql = """SELECT g.id, g.name FROM groups g
             JOIN user_groups ug ON g.id = ug.group_id
             WHERE ug.user_id = ?"""
    return db.query(sql, [user_id])

def get_user_group_ids(user_id):
    sql = "SELECT group_id FROM user_groups WHERE user_id = ?"
    result = db.query(sql, [user_id])

    # Convert rows into a proper list of integers
    group_ids = [int(row["group_id"]) for row in result]

    print(f"DEBUG: User {user_id} is in groups: {group_ids}")  # Updated debug

    return group_ids  # ✅ Now correctly returns a list of integers


