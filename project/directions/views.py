from flask import render_template, request, Blueprint

from .forms import DirectionsForm
from project import db
from project.commons import login_required

import requests, json

import os

# helper functions
def get_directions(origin=None, destination=None):
	google_api_key = os.environ['GOOGLE_API_KEY']
	res = []
	total_dist_in_meter = 0
	if origin != None and destination != None:
		output_format = "json"
		url = "https://maps.googleapis.com/maps/api/directions/"
		url = url + output_format + "?origin=" + origin + "&destination=" + destination
		url = url + "&key=" + google_api_key

		r = requests.get(url)
		output = json.loads(str(r.content, 'utf-8'))
		for route in output["routes"]:
			for leg in route["legs"]:
				total_dist_in_meter += leg["distance"]["value"]
				for step in leg["steps"]:
					res.append(step["html_instructions"]+" ("+step["distance"]["text"]+")")
		res.insert(0, "========================================================")
		res.insert(0, f"Total distance is <b>{total_dist_in_meter//1000} km</b>")

	return res


# config
directions_blueprint = Blueprint('directions', __name__)

# routes
@directions_blueprint.route('/directions/')
@login_required
def directions():
	return render_template('directions.html', form=DirectionsForm(request.form),
		directions=get_directions())

@directions_blueprint.route('/directions/get/', methods=['GET', 'POST'])
@login_required
def directions_get():
	error = None
	form = DirectionsForm(request.form)
	origin, destination = None, None
	if request.method == 'POST':
		if form.validate_on_submit():
			origin = form.from_st_addr.data.replace(" ", "+") + "+" + \
				form.from_city.data.replace(" ", "+") + "+" + form.from_state.data
			destination = form.to_st_addr.data.replace(" ", "+") + "+" + \
				form.to_city.data.replace(" ", "+") + "+" + form.to_state.data
	return render_template('directions.html', form=DirectionsForm(request.form),
		directions=get_directions(origin, destination))

	