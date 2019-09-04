from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('_config.py')
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from project.users.views import users_blueprint
from project.tasks.views import tasks_blueprint

app.register_blueprint(users_blueprint)
app.register_blueprint(tasks_blueprint)

@app.errorhandler(404)
def not_found(error):
	if app.debug == False:
		timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
		with open('error.log', 'a') as f:
			f.write(f"404 error at {timestamp}: {request.url}\n")
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	if app.debug == False:
		timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
		with open('error.log', 'a') as f:
			f.write(f"500 error at {timestamp}: {request.url}\n")
	return render_template('500.html'), 500

