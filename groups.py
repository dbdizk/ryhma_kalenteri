import db

def add_group(name, description):
    sql = "INSERT INTO groups (name, description) VALUES (?, ?)"
    db.execute(sql, [name, description])

def get_groups():
    sql = "SELECT id, name FROM groups ORDER BY id DESC"
    return db.query(sql)

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
