from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from models import BlogPost
from datetime import datetime

blog = Blueprint('blog', __name__)

@blog.route('/')
def index():
    # Get categories for the sidebar
    categories = {
        'actualiteit': {
            'title': 'Actualiteit & Nieuws',
            'subtopics': [
                'Maatschappij',
                'Gemeenschap',
                'Aankondigingen',
                'Vorming & Educatie'
            ]
        },
        'onderwijs': {
            'title': 'Onderwijs & Onderzoek',
            'subtopics': [
                'Opvoeding & Jeugd',
                'Workshops & Cursussen',
                'Gemeenschapsleven'
            ]
        },
        'gemeenschap': {
            'title': 'Projecten & Initiatieven',
            'subtopics': [
                'Vrijwilligers & Samenwerkingen',
                'Geloof & Inspiratie'
            ]
        },
        'spiritualiteit': {
            'title': 'Geloof & Inspiratie',
            'subtopics': [
                'Aanbiddingen',
                'Reflecties & Inspiratie',
                'Lezingen'
            ]
        }
    }

    posts = BlogPost.query.filter_by(
        published=True
    ).order_by(BlogPost.created_at.desc()).all()

    return render_template('blog/index.html', 
                         posts=posts, 
                         categories=categories)

@blog.route('/gemeenschap')
def community():
    # Get video posts for the community section
    video_posts = BlogPost.query.filter_by(
        published=True,
        has_video=True,
        category='Gemeenschap'
    ).order_by(BlogPost.created_at.desc()).all()
    return render_template('blog/community.html', posts=video_posts)

@blog.route('/leercentrum')
def learning_center():
    topics = {
        'plichtenleer': {
            'title': 'Plichtenleer',
            'subtopics': ['Shahada', 'Gebed', 'Zakat', 'Vasten', 'Hadj']
        },
        'geloofsleer': {
            'title': 'Geloofsleer',
            'subtopics': ['Allah', 'Engelen', 'Koran', 'Profeten', 'De Laatste Dag', 'Het Lot']
        },
        'karaktervorming': {
            'title': 'Karaktervorming',
            'subtopics': ['Ethiek', 'Manieren', 'Omgang']
        },
        'geschiedenis': {
            'title': 'Islamitische Geschiedenis',
            'subtopics': ['Profeet Mohammed ﷺ', 'Sahaba', 'Islamitische Beschaving', 'Islamitische geschiedenis in België']
        }
    }
    return render_template('blog/learning_center.html', topics=topics)

@blog.route('/<slug>')
def view(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    return render_template('blog/view.html', post=post)

@blog.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        flash('Alleen administrators kunnen content aanmaken.', 'error')
        return redirect(url_for('blog.index'))

    # Determine if we're creating a video post based on the referrer
    is_video = request.referrer and 'gemeenschap' in request.referrer.lower()

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        category = request.form.get('category', 'Video' if is_video else 'Nieuws')
        is_featured = bool(request.form.get('is_featured', False))

        # Handle media type (image or video)
        media_type = request.form.get('mediaType')
        image_url = None
        video_url = None
        video_platform = None
        has_video = False

        if media_type == 'image':
            image_url = request.form.get('image_url')
        else:  # video
            video_url = request.form.get('video_url')
            video_platform = request.form.get('video_platform')
            has_video = bool(video_url)

        # Create URL-friendly slug from title
        slug = title.lower().replace(' ', '-')

        post = BlogPost(
            title=title,
            content=content,
            excerpt=excerpt,
            image_url=image_url,
            video_url=video_url,
            video_platform=video_platform,
            has_video=has_video,
            slug=slug,
            author_id=current_user.id,
            is_featured=is_featured,
            category=category
        )

        # Calculate reading time
        post.reading_time = post.calculate_reading_time()

        db.session.add(post)
        db.session.commit()

        flash('Video succesvol toegevoegd!' if has_video else 'Blog post succesvol aangemaakt!', 'success')
        return redirect(url_for('blog.view', slug=post.slug))

    return render_template('blog/create.html', is_video=is_video)