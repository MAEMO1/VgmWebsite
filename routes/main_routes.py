from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/board')
def board():
    return render_template('board.html')

@main.route('/donate-vgm')
def donate_vgm():
    return render_template('donate_vgm.html')

@main.route('/community')
def community():
    return render_template('blog/community.html')

@main.route('/memorandum')
def memorandum():
    return render_template('memorandum.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/mosques')
def mosques():
    return render_template('mosques.html')