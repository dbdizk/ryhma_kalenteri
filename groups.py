import db

def add_group(name, description):
    sql = "INSERT INTO groups (name, description) VALUES (?, ?)"
    db.execute(sql, [name, description])