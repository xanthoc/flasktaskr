from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class DirectionsForm(FlaskForm):
	from_st_addr = StringField('From Street Address', validators=[DataRequired()])
	from_city = StringField('From City', validators=[DataRequired()])
	from_state = StringField('From State', validators=[DataRequired()])

	to_st_addr = StringField('To Street Address', validators=[DataRequired()])
	to_city = StringField('To City', validators=[DataRequired()])
	to_state = StringField('To State', validators=[DataRequired()])
