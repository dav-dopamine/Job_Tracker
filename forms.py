from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired
from models import JobStatusEnum

class JobApplicationForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    # Use a select field with choices from JobStatusEnum
    status = SelectField('Status',
                         choices=[(status.value, status.name) for status in JobStatusEnum],
                         validators=[DataRequired()])
    # Expecting date in YYYY-MM-DD format (adjust format if needed)
    date_applied = DateField('Date Applied', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Submit')
