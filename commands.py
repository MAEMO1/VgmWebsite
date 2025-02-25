from flask.cli import AppGroup
from app import db
from models import FundraisingCampaign
from datetime import datetime, timedelta

campaign_cli = AppGroup('campaigns')

@campaign_cli.command('init')
def init_campaigns():
    """Initialize example fundraising campaigns"""
    campaigns = [
        {
            'title': 'Renovatie Gebedsruimte',
            'description': 'Help ons de gebedsruimte te renoveren voor een betere gebedservaring.',
            'goal_amount': 25000.0,
            'current_amount': 15750.0,
            'end_date': datetime.utcnow() + timedelta(days=60)
        },
        {
            'title': 'Islamitisch Onderwijs Programma',
            'description': 'Steun ons educatief programma voor kinderen en jongeren.',
            'goal_amount': 10000.0,
            'current_amount': 3200.0,
            'end_date': datetime.utcnow() + timedelta(days=90)
        },
        {
            'title': 'Voedselbank Project',
            'description': 'Help ons voedselpakketten te verstrekken aan families in nood.',
            'goal_amount': 5000.0,
            'current_amount': 4200.0,
            'end_date': datetime.utcnow() + timedelta(days=30)
        }
    ]
    
    for campaign_data in campaigns:
        campaign = FundraisingCampaign(**campaign_data)
        db.session.add(campaign)
    
    db.session.commit()
    print('Example campaigns initialized successfully!')
