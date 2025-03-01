import db

def add_entry(title,description,date,time,duration,user_id,category_id):
    sql = "INSERT INTO entries (title, description, date, time, duration, user_id, category_id) VALUES (?, ?, ?, ?, ?, ?, ?)"
    db.execute(sql, [title, description, date, time, duration, user_id, category_id])


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

def find_entries(query):
    sql = """SELECT id, title FROM entries WHERE description LIKE ? OR title LIKE ? ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])