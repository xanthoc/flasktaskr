import datetime
from flask import flash, redirect, render_template, \
	request, session, url_for, Blueprint

from .forms import AddTaskForm
from project import db
from project.models import Task
from project.commons import login_required

# config
tasks_blueprint = Blueprint('tasks', __name__)

# helper functions
def open_tasks():
	return db.session.query(Task) \
		.filter_by(status='1').order_by(Task.due_date.asc())

def closed_tasks():
	return db.session.query(Task) \
		.filter_by(status='0').order_by(Task.due_date.asc())

# routes
@tasks_blueprint.route('/tasks/')
@login_required
def tasks():
	return render_template('tasks.html', 
		form=AddTaskForm(request.form),
		open_tasks=open_tasks(), closed_tasks=closed_tasks(),
		username=session['username'])

# it's not essential to include 'GET' in methods, but it's good to do
@tasks_blueprint.route('/tasks/add/', methods=['GET', 'POST'])
@login_required
def add():
	error = None
	form = AddTaskForm(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			new_task = Task(
				form.name.data, form.due_date.data, \
				form.priority.data, datetime.datetime.utcnow(), \
				'1', session['user_id'])
			db.session.add(new_task)
			db.session.commit()
			flash("New entry was successfully posted. Thanks!")
			return redirect(url_for('tasks.tasks'))
	return render_template("tasks.html", form=form, error=error,
		open_tasks=open_tasks(), closed_tasks=closed_tasks())

@tasks_blueprint.route('/tasks/delete/<int:task_id>/')
@login_required
def delete(task_id):
	delete_id = task_id
	task = db.session.query(Task).filter_by(id=delete_id)
	if session['user_id'] == task.first().user_id or session['role'] == 'admin':
		db.session.query(Task).filter_by(id=delete_id).delete()
		db.session.commit()
		flash("The task was deleted. Why not add a new one?")
	else:
		flash("You can only delete tasks that belong to you.")
	return redirect(url_for('tasks.tasks'))

@tasks_blueprint.route('/tasks/complete/<int:task_id>/')
@login_required
def complete(task_id):
	complete_id = task_id
	task = db.session.query(Task).filter_by(id=complete_id)
	if session['user_id'] == task.first().user_id or session['role'] == 'admin':
		task.update({"status": "0"})
		db.session.commit()
		flash("The task is complete. Nice.")
	else:
		flash('You can only update tasks that belong to you.')
	return redirect(url_for('tasks.tasks'))
	