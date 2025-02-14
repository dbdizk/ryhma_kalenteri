import db

def add_entry(title,description,date,time ,duration,user_id):
    sql = "INSERT INTO entries (title, description, date, time, duration, user_id) VALUES (?, ?, ?, ?, ?, ?)"
    db.execute(sql, [title, description, date, time, duration, user_id])


def get_entries():
    sql = "SELECT id, title FROM entries ORDER BY id DESC"
    return db.query(sql)

def get_entry(entry_id):
    sql = """SELECT entries.id, entries.title, entries.description, entries.date, entries.time, entries.duration, users.id user_id, users.username FROM entries, users WHERE entries.user_id = users.id AND entries.id = ?"""
    return db.query(sql, [entry_id])[0]

def update_entry(entry_id, title, description, date, time, duration):
    sql = """UPDATE entries SET title = ?, description = ?, date = ?, time = ?, duration = ? WHERE id = ?"""
    db.execute(sql, [title, description, date, time, duration, entry_id])