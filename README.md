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

---

