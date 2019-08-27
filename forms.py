from flask_wtf import Form
from wtforms import StringField, DateField, IntegerField, SelectField, \
	PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Email

class AddTaskForm(Form):
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

class RegisterForm(Form):
	username = StringField('Username', \
		validators=[DataRequired(), Length(min=5, max=25)])
	email = StringField('Email', \
		validators=[DataRequired(), Email(), Length(min=5, max=40)])
	password = PasswordField('Password', \
		validators=[DataRequired(), Length(min=5, max=40)])
	confirm = PasswordField('Repeat Password', \
		validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

class LoginForm(Form):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])