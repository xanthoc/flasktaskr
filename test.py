import os
import unittest

from views import app, db
from _config import basedir
from models import User

TEST_DB = "test.db"

class AllTests(unittest.TestCase):
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
			follow_redirects=True
			)
	def register(self, username, email, password, confirm):
		return self.app.post('/register/', data=dict(
			username=username, email=email, password=password, confirm=confirm),
			follow_redirects=True)

	def logout(self):
		return self.app.get('/logout/', follow_redirects=True)

	def create_task(self):
		return self.app.post('/add/', data=dict(
			name='Go to the bank', due_date='10/08/2016', priority='1',
			posted_date='10/08/2016', status='1'),
			follow_redirects=True)

	# test cases
	def test_form_is_present_on_root_page(self):
		response = self.app.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Please login to access your task list.', response.data)

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

	def test_users_can_add_task(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.login('michael', 'michaelherman')
		response = self.create_task()
		self.assertIn(b'New entry was successfully posted. Thanks!', response.data)
		self.assertIn(b'Go to the bank', response.data)

	def test_users_cannot_add_task_when_error(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.login('michael', 'michaelherman')
		response = self.app.post('/add/', data=dict(
			name='Go to the bank', due_date='', priority='1',
			posted_date='10/08/2016', status='1'),
			follow_redirects=True)
		self.assertIn(b'This field is required.', response.data)

	def test_users_can_complete_task(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.login('michael', 'michaelherman')
		self.create_task()
		response = self.app.get('/complete/1/', follow_redirects=True)
		self.assertIn(b'The task is complete. Nice.', response.data)

	def test_users_can_delete_task(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.login('michael', 'michaelherman')
		self.create_task()
		response = self.app.get('/delete/1/', follow_redirects=True)
		self.assertIn(b'The task was deleted.', response.data)

	def test_users_cannot_complete_task_that_are_not_created_by_them(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.login('michael', 'michaelherman')
		self.create_task()
		self.logout()
		self.register('fletcher', 'fletcher@realpython.com', 'python', 'python')
		self.login('fletcher', 'python')
		response = self.app.get('/complete/1/', follow_redirects=True)
		self.assertNotIn(b'The task is complete. Nice.', response.data)




	# def test_invalid_form_data(self):
	# 	response = self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
	# 	self.assertIn(b'Thanks for registering. Please login.', response.data)
	# 	response = self.login('michael', 'michaelherman')
	# 	self.assertIn(b'Welcome!', response.data)

if __name__ == "__main__":
	unittest.main()
