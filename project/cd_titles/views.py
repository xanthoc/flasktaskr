from flask import render_template, Blueprint

from project.commons import login_required

# config
cd_titles_blueprint = Blueprint('cd_titles', __name__)

# helper functions

# routes
@cd_titles_blueprint.route('/cd_titles/')
@login_required
def cd_titles():
	return render_template('cd_titles.html')

