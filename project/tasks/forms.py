from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired

class AddTaskForm(FlaskForm):
	name = StringField('Task Name', validators=[DataRequired()])
	due_date = DateField('Date Due (mm/dd/yyyy)', \
		validators=[DataRequired()], format='%m/%d/%Y')
	priority = SelectField('Priority', \
		validators=[DataRequired()], \
		choices = [
				('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), \
				('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')
			])
	status = IntegerField('Status')

	def __repr__(self):
		return "<AddTaskForm: {}, {}, {}, {}".format(
			self.name.data, self.due_date.data,
			self.priority.data, self.status.data)
