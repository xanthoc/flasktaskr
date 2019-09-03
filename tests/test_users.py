import os
import unittest

from project import app, db
from project._config import basedir
from project.models import User

TEST_DB = "test.db"

class UsersTest(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + \
			os.path.join(basedir, TEST_DB)
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	# helper functions
	def login(self, username, password):
		return self.app.post('/', data=dict(
			username=username, password=password),
			follow_redirects=True)

	def register(self, username, email, password, confirm):
		return self.app.post('/register/', data=dict(
			username=username, email=email, password=password, confirm=confirm),
			follow_redirects=True)

	def logout(self):
		return self.app.get('/logout/', follow_redirects=True)

	# test cases
	def test_form_is_present_on_root_page(self):
		response = self.app.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Please sign in to access your task list.', response.data)

	def test_users_cannot_login_unless_registered(self):
		response = self.login('foo', 'bar')
		self.assertIn(b'Invalid credentials. Please try again.', response.data)

	def test_form_is_present_on_register_page(self):
		response = self.app.get('/register/')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Please register to access the task list.', response.data)

	def test_users_can_register(self):
		response = self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.assertIn(b'Thanks for registering. Please login.', response.data)

	def test_users_can_login_if_registered(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		response = self.login('michael', 'michaelherman')
		self.assertIn(b'Welcome!', response.data)

	def test_users_must_be_unique(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		response = self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.assertIn(b'That username and/or email already exist.', response.data)

	def test_logged_in_users_can_logout(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.login('michael', 'michaelherman')
		response = self.logout()
		self.assertIn(b'Goodbye!', response.data)

	def test_not_logged_in_users_cannot_logout(self):
		response = self.logout()
		self.assertNotIn(b'Goodbye!', response.data)

	def test_logged_in_users_can_access_tasks_page(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.login('michael', 'michaelherman')
		response = self.app.get('/tasks/')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Add a new task:', response.data)

	def test_not_logged_in_users_cannot_access_tasks_page(self):
		response = self.app.get('/tasks/', follow_redirects=True)
		self.assertIn(b'You need to login first.', response.data)

	def test_default_user_role(self):
		db.session.add(
			User('johnny', 'john@doe.com', 'johnny')
			)
		db.session.commit()
		users = db.session.query(User).all()
		print(users)
		for user in users:
			self.assertEqual(user.role, 'user')

	def test_task_template_displays_logged_in_username(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.login('michael', 'michaelherman')
		response = self.app.get('/tasks/', follow_redirects=True)
		self.assertIn(b'michael', response.data)


if __name__ == "__main__":
	unittest.main()
