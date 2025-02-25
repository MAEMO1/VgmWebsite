from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, DateField, DateTimeLocalField, SelectField
from wtforms.validators import DataRequired, Optional, Length, Email, ValidationError, Regexp

class ObituaryForm(FlaskForm):
    # Indiener (submitter) information - required fields
    submitter_name = StringField('Uw Naam *', validators=[
        DataRequired(message='Vul uw naam in'),
        Length(min=2, max=100, message='Naam moet tussen 2 en 100 karakters zijn')
    ])
    submitter_phone = StringField('Uw GSM Nummer *', validators=[
        DataRequired(message='Vul uw GSM nummer in'),
        Regexp(r'^\+?[0-9\s-]{8,}$', message='Voer een geldig telefoonnummer in')
    ])
    family_contact = StringField('Contactpersoon Familie *', validators=[
        DataRequired(message='Vul de naam van de contactpersoon in'), 
        Length(min=2, max=100, message='Naam moet tussen 2 en 100 karakters zijn')
    ])

    # Deceased person information
    name = StringField('Naam van de Overledene *', validators=[DataRequired(), Length(min=2, max=100)])
    age = IntegerField('Leeftijd', validators=[Optional()])
    birth_place = StringField('Geboorteplaats', validators=[Optional(), Length(max=100)])
    death_place = StringField('Plaats van Overlijden *', validators=[DataRequired(), Length(max=100)])
    date_of_death = DateField('Datum van Overlijden *', validators=[DataRequired()])

    # Prayer details
    death_prayer_location = SelectField('Locatie Begrafenisgebed (Janazah) *', validators=[DataRequired()])
    other_location_address = StringField('Adres', validators=[Length(max=200)])

    time_type = SelectField('Type Tijdsaanduiding *',
        choices=[
            ('specific', 'Specifiek Tijdstip'),
            ('after_prayer', 'Na een Gebed')
        ],
        validators=[DataRequired()]
    )
    prayer_time = DateTimeLocalField('Tijdstip Begrafenisgebed (Janazah)', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    prayer_date = DateField('Datum Begrafenisgebed (Janazah)', validators=[Optional()])
    after_prayer = SelectField('Na welk Gebed',
        choices=[
            ('fajr', 'Na Fajr (Ochtendgebed)'),
            ('dhuhr', 'Na Dhuhr (Middaggebed)'),
            ('asr', 'Na Asr (Namiddaggebed)'),
            ('maghrib', 'Na Maghrib (Zonsonderganggebed)'),
            ('isha', 'Na Isha (Avondgebed)'),
            ('jumuah', 'Na Jumuah (Vrijdaggebed)')
        ],
        validators=[Optional()]
    )

    burial_location = StringField('Begraafplaats', validators=[Optional(), Length(max=200)])
    additional_notes = TextAreaField('Aanvullende Opmerkingen', validators=[Optional(), Length(max=1000)])

    def validate_other_location_address(self, field):
        if self.death_prayer_location.data == '0' and not field.data:
            raise ValidationError('Adres is verplicht wanneer "Andere locatie" is geselecteerd')

    def validate_prayer_time(self, field):
        if self.time_type.data == 'specific' and not field.data:
            raise ValidationError('Tijdstip is verplicht wanneer "Specifiek Tijdstip" is geselecteerd')

    def validate_prayer_date(self, field):
        if self.time_type.data == 'after_prayer' and not field.data:
            raise ValidationError('Datum is verplicht wanneer "Na een Gebed" is geselecteerd')

    def validate_after_prayer(self, field):
        if self.time_type.data == 'after_prayer' and not field.data:
            raise ValidationError('Selecteer een gebed wanneer "Na een Gebed" is geselecteerd')