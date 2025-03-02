import db

def add_rsvp(user_id, entry_id, status):
    sql = """INSERT INTO rsvps (user_id, entry_id, status)
             VALUES (?, ?, ?)
             ON CONFLICT(user_id, entry_id)
             DO UPDATE SET status = excluded.status"""
    db.execute(sql, [user_id, entry_id, status])

def get_user_rsvp(user_id, entry_id):
    sql = "SELECT status FROM rsvps WHERE user_id = ? AND entry_id = ?"
    result = db.query(sql, [user_id, entry_id])
    return result[0]["status"] if result else None

def get_event_rsvps(entry_id):
    sql = """SELECT u.username, r.status FROM rsvps r
             JOIN users u ON r.user_id = u.id
             WHERE r.entry_id = ?"""
    return db.query(sql, [entry_id])
