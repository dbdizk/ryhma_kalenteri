import db

def add_group(name, description):
    sql = "INSERT INTO groups (name, description) VALUES (?, ?)"
    db.execute(sql, [name, description])

def get_groups():
    sql = "SELECT id, name FROM groups ORDER BY id DESC"
    return db.query(sql)

