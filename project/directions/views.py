from flask import render_template, request, Blueprint

from .forms import DirectionsForm
from project import db

import requests, json

# helper functions
def get_directions(origin=None, destination=None):
	res = []
	if origin != None and destination != None:
		# origin = "Los+Angeles+CA"
		# destination = "San+Francisco+CA"
		output_format = "json"
		google_api_key = "AIzaSyAujwrlZ65xunoTgoiJfYNtyaCsvor5vmY"
		url = "https://maps.googleapis.com/maps/api/directions/"
		url = url + output_format + "?origin=" + origin + "&destination=" + destination
		url = url + "&key=" + google_api_key

		r = requests.get(url)
		output = json.loads(str(r.content, 'utf-8'))
		for route in output["routes"]:
			for leg in route["legs"]:
				for step in leg["steps"]:
					res.append(step["html_instructions"])
	return res


# config
directions_blueprint = Blueprint('directions', __name__)

# routes
@directions_blueprint.route('/directions/')
def directions():
	return render_template('directions.html', form=DirectionsForm(request.form),
		directions=get_directions())

@directions_blueprint.route('/apply_directions/', methods=['GET', 'POST'])
def apply_directions():
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

	