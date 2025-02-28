from datetime import date
import logging
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_babel import _

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ramadan = Blueprint('ramadan', __name__)

@ramadan.route('/iftar-map')
def iftar_map():
    """Temporarily disabled iftar map route"""
    flash(_('De Ramadan functionaliteit is momenteel niet beschikbaar.'), 'info')
    return redirect(url_for('main.index'))

@ramadan.route('/')
def index():
    """Temporarily disabled Ramadan main page"""
    flash(_('De Ramadan functionaliteit is momenteel niet beschikbaar.'), 'info')
    return redirect(url_for('main.index'))