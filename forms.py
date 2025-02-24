from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, DateField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Optional, Length, Email, ValidationError

class ObituaryForm(FlaskForm):
    name = StringField('Naam', validators=[DataRequired(), Length(min=2, max=100)])
    age = IntegerField('Leeftijd', validators=[Optional()])
    birth_place = StringField('Geboorteplaats', validators=[Optional(), Length(max=100)])
    death_place = StringField('Plaats van Overlijden', validators=[DataRequired(), Length(max=100)])
    date_of_death = DateField('Datum van Overlijden', validators=[DataRequired()])
    prayer_time = DateTimeField('Tijd van Dodengebed', validators=[Optional()])
    death_prayer_location = SelectField('Locatie Dodengebed', validators=[DataRequired()])
    other_location_address = StringField('Adres', validators=[Length(max=200)])
    burial_location = StringField('Begraafplaats', validators=[Optional(), Length(max=200)])
    family_contact = StringField('Contact voor Condoleances', validators=[Optional(), Length(max=200)])
    additional_notes = TextAreaField('Aanvullende Opmerkingen', validators=[Optional(), Length(max=1000)])
    mosque_id = SelectField('Moskee voor Verificatie', coerce=int, validators=[DataRequired()])

    def validate_other_location_address(self, field):
        if self.death_prayer_location.data == 'andere' and not field.data:
            raise ValidationError('Adres is verplicht wanneer "Andere" is geselecteerd')