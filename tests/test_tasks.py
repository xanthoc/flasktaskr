import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import User

TEST_DB = "test.db"

class TasksTest(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['DEBUG'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + \
			os.path.join(basedir, TEST_DB)
		self.app = app.test_client()
		db.create_all()

		self.assertEqual(app.debug, False)

		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.login('michael', 'michaelherman')

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

	def create_task(self):
		return self.app.post('/tasks/add/', data=dict(
			name='Go to the bank', due_date='10/08/2016', priority='1',
			posted_date='10/08/2016', status='1'),
			follow_redirects=True)

	def create_admin_user(self):
		new_user = User(
			name='admin', email='admin@b.com', password=bcrypt.generate_password_hash(
				'admin'), role='admin')
		db.session.add(new_user)
		db.session.commit()

	# test cases
	def test_users_can_add_task(self):
		response = self.create_task()
		self.assertIn(b'New entry was successfully posted. Thanks!', response.data)
		self.assertIn(b'Go to the bank', response.data)

	def test_users_cannot_add_task_when_error(self):
		response = self.app.post('/tasks/add/', data=dict(
			name='Go to the bank', due_date='', priority='1',
			posted_date='10/08/2016', status='1'),
			follow_redirects=True)
		self.assertIn(b'This field is required.', response.data)

	def test_users_can_complete_task(self):
		self.create_task()
		response = self.app.get('/tasks/complete/1/', follow_redirects=True)
		self.assertIn(b'The task is complete. Nice.', response.data)

	def test_users_can_delete_task(self):
		self.create_task()
		response = self.app.get('/tasks/delete/1/', follow_redirects=True)
		self.assertIn(b'The task was deleted.', response.data)

	def test_users_cannot_complete_task_that_are_not_created_by_them(self):
		self.create_task()
		self.logout()
		self.register('fletcher', 'fletcher@realpython.com', 'python', 'python')
		self.login('fletcher', 'python')
		response = self.app.get('/tasks/complete/1/', follow_redirects=True)
		self.assertNotIn(b'The task is complete. Nice.', response.data)
		self.assertIn(b'You can only update tasks that belong to you.',
			response.data)

	def test_users_cannot_delete_task_that_are_not_created_by_them(self):
		self.create_task()
		self.logout()
		self.register('fletcher', 'fletcher@realpython.com', 'python', 'python')
		self.login('fletcher', 'python')
		response = self.app.get('/tasks/delete/1/', follow_redirects=True)
		self.assertNotIn(b'The task was deleted. Why not add a new one?', response.data)
		self.assertIn(b'You can only delete tasks that belong to you.',
			response.data)

	def test_admin_users_can_complete_tasks_that_are_not_created_by_them(self):
		self.create_task()
		self.logout()
		self.create_admin_user()
		self.login('admin', 'admin')
		response = self.app.get('/tasks/complete/1/', follow_redirects=True)
		self.assertIn(b'The task is complete. Nice.', response.data)
		self.assertNotIn(b'You can only update tasks that belong to you.',
			response.data)

	def test_admin_users_can_delete_task_that_are_not_created_by_them(self):
		self.create_task()
		self.logout()
		self.create_admin_user()
		self.login('admin', 'admin')
		response = self.app.get('/tasks/delete/1/', follow_redirects=True)
		self.assertIn(b'The task was deleted. Why not add a new one?', response.data)
		self.assertNotIn(b'You can only delete tasks that belong to you.',
			response.data)

	def test_users_cannot_see_task_modify_links_for_tasks_not_created_by_them(self):
		self.create_task()
		self.logout()
		self.register('fletcher', 'fletcher@realpython.com', 'python', 'python')
		self.login('fletcher', 'python')
		response = self.app.get('/tasks/', follow_redirects=True)
		self.assertNotIn(b'Mark as complete', response.data)
		self.assertNotIn(b'Delete', response.data)

	def test_users_can_see_task_modify_links_for_tasks_created_by_them(self):
		self.create_task()
		self.logout()
		self.register('fletcher', 'fletcher@realpython.com', 'python', 'python')
		self.login('fletcher', 'python')
		self.create_task()
		response = self.app.get('/tasks/', follow_redirects=True)
		self.assertNotIn(b'/tasks/complete/1/', response.data)
		self.assertNotIn(b'/tasks/delete/1/', response.data)
		self.assertIn(b'/tasks/complete/2/', response.data)
		self.assertIn(b'/tasks/delete/2/', response.data)

	def test_admin_users_can_see_task_modify_links_for_all_tasks(self):
		self.create_task()
		self.logout()
		self.create_admin_user()
		self.login('admin', 'admin')
		self.create_task()
		response = self.app.get('/tasks/', follow_redirects=True)
		self.assertIn(b'/tasks/complete/1/', response.data)
		self.assertIn(b'/tasks/delete/1/', response.data)
		self.assertIn(b'/tasks/complete/2/', response.data)
		self.assertIn(b'/tasks/delete/2/', response.data)



if __name__ == "__main__":
	unittest.main()
