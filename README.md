# 📅 Group Event Calendar

## 📝 Overview
**Group Event Calendar** is a web application that allows users to create, manage, and participate in group-based events. Users can register, create groups, add events to groups they belong to, and RSVP to events. The application ensures that users only see events relevant to their groups while also allowing public events without group restrictions.

## ✨ Features
- 🔐 **User Authentication** – Register, log in, and manage user accounts.
- 👥 **Group Management** – Create groups, add/remove members, and assign roles (**Admin, Moderator, Member**).
- 📅 **Event Creation & Editing** – Users can create events and assign them to groups they belong to.
- ✅ **RSVP System** – Users can RSVP to events as *"Attending," "Maybe," or "Not Attending."*
- 🔎 **Filtered Event Visibility** – Users only see events from groups they belong to or public events.
- 🔑 **Role-Based Access Control** – Only admins can manage group members and modify event settings.

## 🚀 Installation & Setup

1. **Download and unzip** the project by pressing "Code" and "Download ZIP" in the top right corner. 
2. **Install venv** by doing the command 'python3 -m venv venv' inside the project directory.
3. **Activate venv** by doing 'source venv/bin/activate/' if you're on Linux, or 'source venv/Scripts/activate' on Windows.
4. **Install flask** once venv is activate by doing the command 'pip install flask'.
5. **Initialize database** via command 'sqlite3 database.db < schema.sql'
6. **Done!** You can now run the web app locally through 'flask run'.

## 📖 Usage
1. **Register an account** and log in.
2. **Create or join groups** to manage group-specific events.
3. **Create an event**, assigning it to a group (if applicable).
4. **RSVP to events** to track participation.
5. **Manage group members** if you are an admin.
6. **View only relevant events** based on your group memberships.

## 🛠 Technologies Used
- 🐍 **Python (Flask)** – Backend framework
- 🗄 **SQLite** – Database management
- 🎨 **HTML/CSS** – Frontend structure
- 🔧 **Jinja2** – Template rendering (used by Flask)

## 📜 License
This project is open-source and free to use under the **MIT License**.

## 🔮 Future Enhancements
- 📩 **Email notifications** for event updates
- 📆 **Calendar view integration**
- 💬 **Comment section** for event discussions

## ❌ Current known nuances that won't be fixed due to limited time window before deadline
- **Moderator** role doesn't do anything special. It's just like member.
- **Categories** cannot be deleted. This is because currently the category creator isn't logged and thus anyone could delete any category.

## 🔐 Page User Permissions
| Route | URL | Permissions Checked? |
|--------|------|--------------------|
| `index()` | `/` | ✅ Shows only public/group-allowed entries |
| `show_entry(entry_id)` | `/entry/<int:entry_id>` | ✅ Public entries are viewable, private require login & group check |
| `find_entry()` | `/find_entry` | ✅ Now ensures only public & user-allowed group entries are displayed |
| `register()` | `/register` | ✅ Redirects logged-in users to homepage |
| `create()` | `/create` | ✅ Prevents logged-in users from registering again |
| `login()` | `/login` | ✅ Redirects logged-in users to homepage |
| `logout()` | `/logout` | ✅ Only runs if logged in |
| `show_user(user_id)` | `/user/<int:user_id>` | ✅ Publicly viewable, but shows only public data |
| `new_entry()` | `/new_entry` | ✅ Requires login |
| `create_entry()` | `/create_entry` | ✅ Requires login & verifies group permissions |
| `edit_entry(entry_id)` | `/edit_entry/<int:entry_id>` | ✅ Requires login & user must own the entry |
| `update_entry()` | `/update_entry` | ✅ Requires login & user must own the entry |
| `delete_entry(entry_id)` | `/delete_entry/<int:entry_id>` | ✅ Requires login & user must own the entry |
| `confirm_delete()` | `/confirm_delete` | ✅ Requires login & password confirmation |
| `new_group()` | `/new_group` | ✅ Requires login |
| `create_group()` | `/create_group` | ✅ Requires login |
| `show_group()` | `/group/<int:group_id>` | ✅ Requires login and being a member of said group|
| `manage_groups()` | `/manage_groups` | ✅ Only group admins can access |
| `add_user_to_group()` | `/add_user_to_group` | ✅ Only group admins can add users |
| `remove_user_from_group()` | `/remove_user_from_group` | ✅ Only group admins can remove users |
| `change_user_role()` | `/change_user_role` | ✅ Only group admins can change roles |
| `new_category()` | `/new_category` | ✅ Requires login |
| `create_category()` | `/create_category` | ✅ Requires login |
| `rsvp()` | `/rsvp` | ✅ Requires login |


## 🔐 Form Permission Checks

### **User Authentication Forms**
| Form | URL | Method | Permission Check? |
|------|------|--------|------------------|
| **Register** | `/create` | `POST` | ✅ **Prevents logged-in users from re-registering** |
| **Login** | `/login` | `POST` | ✅ **Anyone can log in** |
| **Logout** | `/logout` | `GET` | ✅ **Only logs out if logged in** |

### **Entry Forms**
| Form | URL | Method | Permission Check? |
|------|------|--------|------------------|
| **Create Entry** | `/create_entry` | `POST` | ✅ **User must be logged in & can only assign groups they belong to** |
| **Edit Entry** | `/update_entry` | `POST` | ✅ **User must be logged in & must own the entry** |
| **Delete Entry** | `/confirm_delete` | `POST` | ✅ **User must own the entry & confirm password** |

### **Group Management Forms**
| Form | URL | Method | Permission Check? |
|------|------|--------|------------------|
| **Create Group** | `/create_group` | `POST` | ✅ **User must be logged in** |
| **Add User to Group** | `/add_user_to_group` | `POST` | ✅ **Only group admins can submit** |
| **Remove User from Group** | `/remove_user_from_group` | `POST` | ✅ **Only group admins can submit** |
| **Change User Role in Group** | `/change_user_role` | `POST` | ✅ **Only group admins can submit & can’t change their own role** |

### **Category Management Forms**
| Form | URL | Method | Permission Check? |
|------|------|--------|------------------|
| **Create Category** | `/create_category` | `POST` | ✅ **User must be logged in** |

### **RSVP System**
| Form | URL | Method | Permission Check? |
|------|------|--------|------------------|
| **RSVP Submission** | `/rsvp` | `POST` | ✅ **User must be logged in** |



## ✅ Course requirement checklist

## Basic Requirements (7 points)

- [x] User can create an account and log in to the application (1 point)
- [x] User can add, edit, and delete data items (1 point)
- [x] User can view the added data items in the application (1 point)
- [x] User can search for data items by keyword or other criteria (1 point)
- [x] User's page displays statistics and the user's added data items (1 point)
- [x] User can assign one or more categories to a data item (1 point)
- [x] User can submit additional information to a data item (1 point)

## Technical Requirements (8 points)

- [x] Application implemented according to the course materials (1 point)
- [x] Application implemented using Python and Flask library (1 point)
- [x] Application uses SQLite database (1 point)
- [x] Git and GitHub used during development (1 point)
- [x] Application interface consists of HTML pages (1 point)
- [x] No JavaScript code used in the application (1 point)
- [x] Database is used with raw SQL queries (no ORM) (1 point)
- [x] Only Flask library is used; no additional libraries installed (1 point)

## Functionality and Usability (15 points)

- [ ] User experience with the functionality of the application (5 points)
- [ ] User experience with the usability of the application (5 points)
- [ ] Line breaks in user-submitted text are visible in the browser (1 point)
- [ ] Alt attribute used for images (if images are present) (1 point)
- [ ] Label element used in forms (1 point)
- [ ] CSS used for layout and styling (2 points)

## Version Control (10 points)

- [x] Commits made regularly during development (1 point)
- [x] Commit messages written in English (1 point)
- [x] Commits are meaningful and contain clear messages (5 points)
- [x] No unnecessary files in version control (1 point)
- [x] README.md file provides a good overview of the application (2 points)

## Coding Style (15 points)

- [x] General code quality (clarity, readability, and style) (5 points)
- [x] Indentation level is four spaces (1 point)
- [x] Code written in English (1 point)
- [x] Variable and function names in snake_case (e.g., `total_count`, not `totalCount`) (1 point)
- [ ] Consistent use of single or double quotes for strings (1 point)
- [ ] Proper spacing around assignment (`=`) and comparison (`==`) operators (1 point)
- [ ] Proper spacing around commas (1 point)
- [ ] Avoid returning `True` or `False` directly after an `if` statement (1 point)
- [x] Functions should have multiple potential return values if needed (1 point)
- [x] No parentheses around conditions in `if` and `while` statements (1 point)
- [x] Use `is None` rather than `== None` for checking null values (1 point)

## Database Design (15 points)

- [x] Tables and columns named in English (1 point)
- [x] Tables and columns are named meaningfully (3 points)
- [x] Used `REFERENCES` for foreign key relationships (1 point)
- [x] Used `UNIQUE` constraint where applicable (1 point)
- [x] Avoided `SELECT *` queries (1 point)
- [x] Long SQL commands split across multiple lines for readability (1 point)
- [x] All data fetched in one SQL query if logically possible (3 points)
- [x] Avoided doing things in code that can be done meaningfully in SQL (3 points)
- [x] Used `try/except` around SQL commands only when necessary (1 point)

## Application Security (20 points)

- [x] Passwords stored securely in the database (1 point)
- [x] User permissions checked before allowing access to pages (5 points)
- [ ] User permissions checked before allowing form submissions (5 points)
- [ ] User inputs validated before being added to the database (3 points)
- [x] SQL queries use parameterized queries to prevent SQL injection (2 points)
- [x] Pages rendered through templates (2 points)
- [ ] CSRF protection used in forms (2 points)

## Handling Large Data Volumes (5 points)

- [ ] Application tested with large data sets, and results reported (3 points)
- [ ] Pagination implemented for handling large data sets (1 point)
- [ ] Index added to the database to speed up handling large data sets (1 point)

## Peer Reviews and Feedback (5 points)

- [x] First peer review given (1 point)
- [x] First peer review done thoroughly (1 point)
- [x] Second peer review given (1 point)
- [x] Second peer review done thoroughly (1 point)
- [ ] Course feedback provided (1 point)


---


