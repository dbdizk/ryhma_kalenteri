import random
import sqlite3

# Connect to the database
db = sqlite3.connect("database.db")

# Clear existing data (CAUTION: This will delete all existing entries!)
db.execute("DELETE FROM users")
db.execute("DELETE FROM categories")
db.execute("DELETE FROM groups")
db.execute("DELETE FROM entries")
db.execute("DELETE FROM user_groups")
db.execute("DELETE FROM entry_groups")

# Define the number of test data to generate
user_count = 10000  # Number of test users
category_count = 1000  # Number of categories
group_count = 2000  # Number of groups
entry_count = 10**6  # Number of test entries

# Generate Users
for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
               [f"user{i}", "testpasswordhash"])  # Fake password hash

# Generate Categories
for i in range(1, category_count + 1):
    db.execute("INSERT INTO categories (name) VALUES (?)",
               [f"Category {i}"])

# Generate Groups
for i in range(1, group_count + 1):
    db.execute("INSERT INTO groups (name, description) VALUES (?, ?)",
               [f"Group {i}", f"This is the description for Group {i}"])

# Assign Users to Groups (Randomly)
for user_id in range(1, user_count + 1):
    num_groups = random.randint(1, 5)  # Each user joins 1-5 groups
    group_ids = random.sample(range(1, group_count + 1), num_groups)
    
    for group_id in group_ids:
        role_id = random.choice([1, 2, 3])  # Random role (1 = admin, 2 = mod, 3 = member)
        db.execute("INSERT INTO user_groups (user_id, group_id, role_id) VALUES (?, ?, ?)",
                   [user_id, group_id, role_id])

# Generate Entries (Assigned to Users & Groups)
for i in range(1, entry_count + 1):
    user_id = random.randint(1, user_count)
    category_id = random.randint(1, category_count)
    
    # 50% chance of being public (no group), otherwise assigned to 1-3 groups
    assigned_groups = []
    if random.random() > 0.5:
        num_groups = random.randint(1, 3)
        assigned_groups = random.sample(range(1, group_count + 1), num_groups)

    db.execute("""INSERT INTO entries (title, description, date, time, duration, user_id, category_id) 
                  VALUES (?, ?, date('now', ? || ' days'), ?, ?, ?, ?)""",
               [f"Entry {i}", f"This is the description for Entry {i}",
                random.randint(-30, 30),  # Random past/future dates
                f"{random.randint(0, 23):02}:{random.randint(0, 59):02}",  # Random time
                random.randint(30, 240),  # Random duration in minutes
                user_id, category_id])

    entry_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]  # Get last inserted entry ID

    # Assign Entry to Groups (If not public)
    for group_id in assigned_groups:
        db.execute("INSERT INTO entry_groups (entry_id, group_id) VALUES (?, ?)",
                   [entry_id, group_id])

# Commit and close
db.commit()
db.close()

print(f"Seed data successfully added: {user_count} users, {category_count} categories, {group_count} groups, {entry_count} entries!")
