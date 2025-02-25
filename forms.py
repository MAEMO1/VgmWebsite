from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, DateField, DateTimeLocalField, SelectField, URLField
from wtforms.validators import DataRequired, Optional, Length, Email, ValidationError, Regexp, URL, NumberRange

class VideoForm(FlaskForm):
    title = StringField('Titel', validators=[
        DataRequired(message='Vul een titel in'),
        Length(min=2, max=200, message='Titel moet tussen 2 en 200 karakters zijn')
    ])
    video_url = URLField('Video URL', validators=[
        DataRequired(message='Vul een video URL in'),
        URL(message='Voer een geldige URL in'),
        Regexp(r'^https?://(www\.)?(youtube\.com|youtu\.be|vimeo\.com)/.+', 
               message='Alleen YouTube en Vimeo URLs zijn toegestaan')
    ])
    description = TextAreaField('Beschrijving', validators=[
        Optional(),
        Length(max=2000, message='Beschrijving mag maximaal 2000 karakters zijn')
    ])

class LearningContentForm(FlaskForm):
    title = StringField('Titel', validators=[
        DataRequired(message='Vul een titel in'),
        Length(min=2, max=200, message='Titel moet tussen 2 en 200 karakters zijn')
    ])
    content = TextAreaField('Inhoud', validators=[
        DataRequired(message='Vul de inhoud in'),
        Length(min=10, message='De inhoud moet minimaal 10 karakters bevatten')
    ])
    topic = SelectField('Onderwerp', validators=[DataRequired(message='Selecteer een onderwerp')], choices=[
        ('plichtenleer', 'Plichtenleer'),
        ('geloofsleer', 'Geloofsleer'),
        ('karaktervorming', 'Karaktervorming'),
        ('geschiedenis', 'Islamitische Geschiedenis')
    ])
    subtopic = SelectField('Subonderwerp', validators=[DataRequired(message='Selecteer een subonderwerp')])
    order = IntegerField('Volgorde', validators=[Optional()])
    video_url = URLField('Video URL (Optioneel)', validators=[
        Optional(),
        URL(message='Voer een geldige URL in'),
        Regexp(r'^https?://(www\.)?(youtube\.com|youtu\.be|vimeo\.com)/.+', 
               message='Alleen YouTube en Vimeo URLs zijn toegestaan')
    ])

    def __init__(self, *args, **kwargs):
        super(LearningContentForm, self).__init__(*args, **kwargs)
        # Dynamic subtopic choices based on main topic
        self.topic_subtopics = {
            'plichtenleer': ['Shahada', 'Gebed', 'Zakat', 'Vasten', 'Hadj'],
            'geloofsleer': ['Allah', 'Engelen', 'Koran', 'Profeten', 'De Laatste Dag', 'Het Lot'],
            'karaktervorming': ['Ethiek', 'Manieren', 'Omgang'],
            'geschiedenis': ['Profeet Mohammed ﷺ', 'Sahaba', 'Islamitische Beschaving', 'Islamitische geschiedenis in België']
        }
        # Set initial subtopic choices
        if self.topic.data in self.topic_subtopics:
            self.subtopic.choices = [(st, st) for st in self.topic_subtopics[self.topic.data]]

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

class FundraisingCampaignForm(FlaskForm):
    title = StringField('Titel', validators=[
        DataRequired(message='Vul een titel in'),
        Length(min=2, max=200, message='Titel moet tussen 2 en 200 karakters zijn')
    ])
    description = TextAreaField('Beschrijving', validators=[
        DataRequired(message='Vul een beschrijving in')
    ])
    goal_amount = IntegerField('Doelbedrag (€)', validators=[
        DataRequired(message='Vul een doelbedrag in'),
        NumberRange(min=1, message='Het doelbedrag moet minimaal €1 zijn')
    ])
    end_date = DateField('Einddatum', validators=[Optional()])
    image_url = URLField('Afbeelding URL', validators=[
        Optional(),
        URL(message='Voer een geldige URL in')
    ])