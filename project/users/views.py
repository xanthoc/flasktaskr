from functools import wraps
from flask import flash, redirect, render_template, \
	request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError

from .forms import RegisterForm, LoginForm
from project import db, bcrypt
from project.models import User

# config
users_blueprint = Blueprint('users', __name__)

# helper functions
def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			flash("You need to login first.")
			return redirect(url_for('users.login'))
	return wrap

def admin_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if not 'logged_in' in session:
			flash("You need to login first.")
			return redirect(url_for('users.login'))
		elif session['role'] == 'admin':
			return test(*args, **kwargs)
		else:
			flash("You must have admin privilege.")
			return redirect(url_for('tasks.tasks'))
	return wrap

def all_users():
	return db.session.query(User).order_by(User.id.asc())


# routes
@users_blueprint.route('/', methods=['GET', 'POST'])
def login():
	error = None
	form = LoginForm(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			user = User.query.filter_by(name=request.form['username']).first()
			if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
				session['logged_in'] = True
				session['user_id'] = user.id
				session['role'] = user.role
				session['username'] = user.name
				flash("Welcome!")
				return redirect(url_for('tasks.tasks'))
			else:
				error = 'Invalid credentials. Please try again.'
	return render_template('login.html', form=form, error=error)

@users_blueprint.route('/logout/')
@login_required
def logout():
	session.pop('logged_in', None)
	session.pop('user_id', None)
	session.pop('role', None)
	session.pop('username', None)
	flash('Goodbye!')
	return redirect(url_for('users.login'))

@users_blueprint.route('/register/', methods=['GET', 'POST'])
def register():
	error = None
	form = RegisterForm(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			new_user = User(
				form.username.data,
				form.email.data,
				bcrypt.generate_password_hash(form.password.data)
				)
			try:
				db.session.add(new_user)
				db.session.commit()
				flash("Thanks for registering. Please sign in.")
				return redirect(url_for('users.login'))
			except IntegrityError:
				error = "That username and/or email already exist."
	return render_template('register.html', form=form, error=error)

@users_blueprint.route('/users/')
@admin_required
def users():
	return render_template(
		'users.html', 
		all_users=all_users()
		)

@users_blueprint.route('/delete_user/<int:user_id>/')
@admin_required
def delete_user(user_id):
	delete_id = user_id
	db.session.query(User).filter_by(id=delete_id).delete()
	db.session.commit()
	flash("The user was deleted.")
	return redirect(url_for('users.users'))

@users_blueprint.route('/change_role/<int:user_id>/')
@admin_required
def change_role(user_id):
	complete_id = user_id
	user = db.session.query(User).filter_by(id=complete_id)
	if user.first().role == 'admin':
		user.update({"role": "user"})
	else:
		user.update({"role": "admin"})
	db.session.commit()
	flash("The role was changed.")
	return redirect(url_for('users.users'))
