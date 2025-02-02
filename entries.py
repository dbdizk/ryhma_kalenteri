import db

def add_entry(title,description,date,duration,user_id):
    sql = "INSERT INTO entries (title, description, date, duration, user_id) VALUES (?, ?,?,?,?)"
    db.execute(sql, [title, description, date, duration, user_id])


def get_entries():
    sql = "SELECT id, title FROM entries ORDER BY id DESC"
    return db.query(sql)