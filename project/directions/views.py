from flask import render_template, request, Blueprint

from .forms import DirectionsForm
from project import db

import requests, json

# helper functions
def get_directions():
	res = []
	origin = "Los+Angeles+CA"
	destination = "San+Francisco+CA"
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
	tmp = render_template('directions.html', form=DirectionsForm(request.form),
		directions=get_directions())
	print(tmp)
	return tmp

	