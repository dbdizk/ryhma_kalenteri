import db

def add_category(name):
    sql = "INSERT INTO categories (name) VALUES (?)"
    db.execute(sql, [name])

def remove_category(name):
    sql = "DELETE FROM categories WHERE name = ?"
    db.execute(sql, [name])

def get_categories():
    sql = "SELECT id, name FROM categories ORDER BY id DESC"
    return db.query(sql)