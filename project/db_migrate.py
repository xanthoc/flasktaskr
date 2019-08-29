from views import db
from _config import DATABASE_PATH
import sqlite3
from datetime import datetime

with sqlite3.connect(DATABASE_PATH) as conn:
	c = conn.cursor()
	c.execute("ALTER TABLE tasks RENAME TO old_tasks")
	c.execute("ALTER TABLE users RENAME TO old_users")
	db.create_all()
	c.execute("SELECT name, due_date, priority, posted_date, status, user_id \
		FROM old_tasks ORDER BY task_id ASC")
	data = [
		(row[0], row[1], row[2], row[3], row[4], row[5])
		for row in c.fetchall()
		]
	c.executemany("INSERT INTO \
		tasks (name, due_date, priority, posted_date, status, user_id) \
		VALUES(?, ?, ?, ?, ?, ?)", data)

	c.execute("SELECT username, email, password \
		FROM old_users ORDER BY user_id ASC")
	data = [
		(row[0], row[1], row[2]) for row in c.fetchall()
		]
	c.executemany("INSERT INTO users (name, email, password) \
		VALUES(?, ?, ?)", data)
	c.execute("DROP TABLE old_tasks")
	c.execute("DROP TABLE old_users")
