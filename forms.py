from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, DateField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Optional, Length, Email

class ObituaryForm(FlaskForm):
    name = StringField('Naam', validators=[DataRequired(), Length(min=2, max=100)])
    age = IntegerField('Leeftijd', validators=[Optional()])
    birth_place = StringField('Geboorteplaats', validators=[Optional(), Length(max=100)])
    death_place = StringField('Plaats van Overlijden', validators=[DataRequired(), Length(max=100)])
    date_of_death = DateField('Datum van Overlijden', validators=[DataRequired()])
    prayer_time = DateTimeField('Tijd van Dodengebed', validators=[Optional()])
    death_prayer_location = StringField('Locatie Dodengebed', validators=[Optional(), Length(max=200)])
    burial_location = StringField('Begraafplaats', validators=[Optional(), Length(max=200)])
    family_contact = StringField('Contact voor Condoleances', validators=[Optional(), Length(max=200)])
    additional_notes = TextAreaField('Aanvullende Opmerkingen', validators=[Optional(), Length(max=1000)])
    mosque_id = SelectField('Moskee voor Verificatie', coerce=int, validators=[DataRequired()])
