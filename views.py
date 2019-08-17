import sqlite3
from flask import Flask, flash, redirect, render_template, \
	request, session, url_for
from functools import wraps
#import pdb

app = Flask(__name__)
app.config.from_object('_config')

def connect_db():
	return sqlite3.connect(app.config['DATABASE_PATH'])

def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			flash("You need to login first.")
			return redirect(url_for('login'))
	return wrap


@app.route('/', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		if request.form['username']==app.config['USERNAME'] and \
			request.form['password']==app.config['PASSWORD']:
			session['logged_in'] = True
			flash("Welcome!")
			return redirect(url_for('tasks'))
		else:
			error = 'Invalid credentials. Please try again ...'
			return render_template('login.html', error=error)
	return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('Goodbye!')
	return redirect(url_for('login'))

if __name__ == '__main__':
	#pdb.set_trace()
	app.run(debug=True)
