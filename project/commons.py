from functools import wraps
from flask import session, flash, redirect, url_for

# helper functions
def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			flash("You need to sign in first.")
			return redirect(url_for('users.login'))
	return wrap

def admin_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if not 'logged_in' in session:
			flash("You need to sign in first.")
			return redirect(url_for('users.login'))
		elif session['role'] == 'admin':
			return test(*args, **kwargs)
		else:
			flash("You must have admin privilege.")
			return redirect(url_for('tasks.tasks'))
	return wrap




