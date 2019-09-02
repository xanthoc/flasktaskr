from datetime import date

from project import db
from project.models import Task, User

db.create_all()

db.session.add(User("admin", "a@b.com", "admin", "admin"))
db.session.add(Task("Finish this tutorial", date(2016, 9, 22), 10,
	date(2016, 9, 22), 1, 1))
db.session.add(Task("Finish Real Python", date(2016, 10, 3), 10,
	date(2016, 10, 3), 1, 1))

db.session.commit()