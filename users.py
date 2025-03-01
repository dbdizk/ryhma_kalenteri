import db
from werkzeug.security import generate_password_hash, check_password_hash

def get_user(user_id):
    sql = """SELECT id, username FROM users WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_entries(user_id):
    sql = """SELECT id, title FROM entries WHERE user_id = ? ORDER BY id DESC"""
    return db.query(sql, [user_id])

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

    # Retrieve and return the new user ID
    sql_get_id = "SELECT id FROM users WHERE username = ?"
    result = db.query(sql_get_id, [username])
    return result[0]["id"] if result else None


def check_password(user_id, password):
    sql = "SELECT password_hash FROM users WHERE id = ?"
    result = db.query(sql, [user_id])[0]
    password_hash = result["password_hash"]
    return check_password_hash(password_hash, password)


def check_login(username, password):
        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])
        if not result:
            return None
        
        user_id = result[0]["id"]
        password_hash = result[0]["password_hash"]
        if check_password_hash(password_hash, password):
            return user_id
        else:
            return None
        
def role_on_create_group(user_id, name):
    sql = """
        INSERT INTO user_groups (user_id, group_id)
        SELECT ?, id FROM groups WHERE name = ?
    """
    rows_affected = db.execute(sql, [user_id, name])

    # If no rows were inserted, the group name didn't exist
    if rows_affected == 0:
        return None

     