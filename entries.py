import db

def add_entry(title,description,date,duration,user_id):
    sql = "INSERT INTO entries (title, description, date, duration, user_id) VALUES (?, ?,?,?,?)"
    db.execute(sql, [title, description, date, duration, user_id])