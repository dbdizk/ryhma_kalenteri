import db

def add_entry(title, description, date, time, duration, user_id, category_id):
    sql = """INSERT INTO entries (title, description, date, time, duration, user_id, category_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [title, description, date, time, duration, user_id, category_id])

    return db.last_insert_id()



def get_entries():
    sql = "SELECT id, title FROM entries ORDER BY id DESC"
    return db.query(sql)

def get_entry(entry_id):
    sql = """SELECT 
                entries.id, 
                entries.title, 
                entries.description, 
                entries.date, 
                entries.time, 
                entries.duration, 
                users.id AS user_id, 
                users.username, 
                categories.name AS category_name
             FROM entries
             JOIN users ON entries.user_id = users.id
             LEFT JOIN categories ON entries.category_id = categories.id
             WHERE entries.id = ?"""
    
    result = db.query(sql, [entry_id])
    return result[0] if result else None




def update_entry(entry_id, title, description, date, time, duration, category_id):
    sql = """UPDATE entries SET title = ?, description = ?, date = ?, time = ?, duration = ?, category_id = ? WHERE id = ?"""
    db.execute(sql, [title, description, date, time, duration, category_id, entry_id])

def delete_entry(entry_id):
    sql = "DELETE FROM entries WHERE id = ?"
    db.execute(sql, [entry_id])

def find_entries(query=None, group_ids=None, category_ids=None):
    sql = """SELECT e.id, e.title, e.description, e.date, e.time, e.duration, 
                    u.username, c.name AS category_name 
             FROM entries e
             JOIN users u ON e.user_id = u.id
             LEFT JOIN categories c ON e.category_id = c.id
             LEFT JOIN entry_groups eg ON e.id = eg.entry_id
             WHERE 1=1 """  # Always true, allows dynamic conditions

    params = []

    # Apply filters dynamically
    if query:
        sql += " AND (e.title LIKE ? OR e.description LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    
    if group_ids:
        placeholders = ",".join(["?"] * len(group_ids))
        sql += f" AND eg.group_id IN ({placeholders})"
        params.extend(group_ids)

    if category_ids:
        placeholders = ",".join(["?"] * len(category_ids))
        sql += f" AND e.category_id IN ({placeholders})"
        params.extend(category_ids)

    sql += " GROUP BY e.id ORDER BY e.date DESC"

    return db.query(sql, params)



def assign_entry_to_groups(entry_id, group_ids):
    if not entry_id:
        print("Error: entry_id is None. Cannot assign to groups.")
        return

    sql = "INSERT INTO entry_groups (entry_id, group_id) VALUES (?, ?)"
    
    for group_id in group_ids:
        db.execute(sql, [entry_id, group_id])


def get_entry_groups(entry_id):
    sql = """SELECT g.id, g.name FROM groups g
             JOIN entry_groups eg ON g.id = eg.group_id
             WHERE eg.entry_id = ?"""
    return db.query(sql, [entry_id])