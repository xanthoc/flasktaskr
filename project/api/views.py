import datetime
from functools import wraps
from flask import flash, redirect, jsonify, render_template, \
	session, url_for, Blueprint, make_response

from project import db
from project.models import Task

# config
api_blueprint = Blueprint('api', __name__)

# helper functions

# routes
@api_blueprint.route('/api/v1/tasks/')
def api_tasks():
	results = db.session.query(Task).limit(10).offset(0).all()
	json_results = []
	for result in results:
		data = {
			'id': result.id,
			'name': result.name,
			'due date': str(result.due_date),
			'priority': result.priority,
			'posted date': str(result.posted_date),
			'status': result.status,
			'user id': result.user_id
		}
		json_results.append(data)
	return jsonify(items=json_results)

@api_blueprint.route('/api/v1/tasks/<int:task_id>')
def api_one_task(task_id):
	result = db.session.query(Task).filter_by(id=task_id).first()
	if result:
		result = {
			'id': result.id,
			'name': result.name,
			'due date': str(result.due_date),
			'priority': result.priority,
			'posted date': str(result.posted_date),
			'status': result.status,
			'user id': result.user_id
		}
		code = 200
	else:
		result = {
			'error': 'Element does not exist.'
		}
		code = 404
	return make_response(jsonify(result), code)

