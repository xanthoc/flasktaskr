import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import User

TEST_DB = "test.db"

class UsersTest(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['DEBUG'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + \
			os.path.join(basedir, TEST_DB)
		self.app = app.test_client()
		db.create_all()

		self.assertEqual(app.debug, False)

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

	def create_admin_user(self):
		new_user = User(
			name='admin', email='admin@b.com', password=bcrypt.generate_password_hash(
				'admin'), role='admin')
		db.session.add(new_user)
		db.session.commit()

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
		self.assertIn(b'Thanks for registering. Please sign in.', response.data)

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
		self.assertIn(b'You need to sign in first.', response.data)

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

	def test_only_admin_users_can_see_users_link(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		response = self.login('michael', 'michaelherman')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'>Tasks<', response.data)
		self.assertNotIn(b'>Users<', response.data)
		self.logout()
		db.session.add(
			User('admin', 'admin@b.com',
				bcrypt.generate_password_hash('admin'), 'admin')
			)
		db.session.commit()
		response = self.login('admin', 'admin')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'>Tasks<', response.data)
		self.assertIn(b'>Users<', response.data)

	def test_only_admin_users_can_see_users_page(self):
		response = self.app.get('/users/', follow_redirects=True)
		self.assertIn(b'You need to sign in first.', response.data)
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.login('michael', 'michaelherman')
		response = self.app.get('/users/', follow_redirects=True)
		self.assertIn(b'You must have admin privilege.', response.data)
		self.logout()
		db.session.add(
			User('admin', 'admin@b.com',
				bcrypt.generate_password_hash('admin'), 'admin')
			)
		db.session.commit()
		self.login('admin', 'admin')
		response = self.app.get('/users/', follow_redirects=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Users:', response.data)
		self.assertIn(b'Role', response.data)

	def test_admin_users_can_change_role(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.create_admin_user()
		self.login('admin', 'admin')
		response = self.app.get('/change_role/1/', follow_redirects=True)
		self.assertIn(b'The role was changed.', response.data)

	def test_admin_users_can_delete_user(self):
		self.register('michael', 'michael@mherman.org', 'michaelherman', 'michaelherman')
		self.create_admin_user()
		self.login('admin', 'admin')
		response = self.app.get('/delete_user/1/', follow_redirects=True)
		self.assertIn(b'The user was deleted.', response.data)
		self.assertNotIn(b'michael', response.data)

	def test_admin_users_cannot_see_links_for_themselves(self):
		self.create_admin_user()
		self.login('admin', 'admin')
		response = self.app.get('/users/', follow_redirects=True)
		self.assertNotIn(b'Delete', response.data)
		self.assertNotIn(b'Change Role', response.data)




if __name__ == "__main__":
	unittest.main()
