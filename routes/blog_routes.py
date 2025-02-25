from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from models import BlogPost, BlogCategory, LearningContent # Added LearningContent import
from forms import VideoForm, LearningContentForm # Added import for LearningContentForm
from datetime import datetime

blog = Blueprint('blog', __name__)

@blog.route('/gemeenschap', methods=['GET', 'POST'])
def community():
    form = VideoForm()

    if request.method == 'POST' and form.validate_on_submit():
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Alleen administrators kunnen videos toevoegen.', 'error')
            return redirect(url_for('blog.community'))

        # Create the blog post with video
        post = BlogPost(
            title=form.title.data,
            content=form.description.data,
            video_url=form.video_url.data,
            video_platform='youtube' if 'youtube' in form.video_url.data or 'youtu.be' in form.video_url.data else 'vimeo',
            has_video=True,
            author_id=current_user.id,
            published=True,
            slug=form.title.data.lower().replace(' ', '-')
        )

        # Add to community category
        community_category = BlogCategory.query.filter_by(name='Gemeenschap').first()
        if not community_category:
            community_category = BlogCategory(name='Gemeenschap')
            db.session.add(community_category)
        post.categories.append(community_category)

        db.session.add(post)
        db.session.commit()

        flash('Video succesvol toegevoegd!', 'success')
        return redirect(url_for('blog.community'))

    # Get video posts for the community section
    video_posts = BlogPost.query.join(BlogPost.categories)\
        .filter(
            BlogPost.published == True,
            BlogPost.has_video == True,
            BlogCategory.name == 'Gemeenschap'
        ).order_by(BlogPost.created_at.desc()).all()

    return render_template('blog/community.html', posts=video_posts, form=form)

@blog.route('/')
def index():
    # Get categories for the sidebar
    categories = {
        'actualiteit': {
            'title': 'Actualiteit & Nieuws',
            'subtopics': [
                'Maatschappij',
                'Gemeenschap',
                'Aankondigingen'
            ]
        },
        'vorming': {
            'title': 'Vorming & Educatie',
            'subtopics': [
                'Onderwijs & Onderzoek',
                'Opvoeding & Jeugd',
                'Workshops & Cursussen'
            ]
        },
        'gemeenschap': {
            'title': 'Gemeenschapsleven',
            'subtopics': [
                'Projecten & Initiatieven',
                'Vrijwilligers & Samenwerkingen'
            ]
        },
        'spiritualiteit': {
            'title': 'Geloof & Inspiratie',
            'subtopics': [
                'Aanbiddingen',
                'Reflecties & Inspiratie',
                'Lezingen',
                'Interlevensbeschouwelijk'
            ]
        }
    }

    # Get posts and their categories
    posts = BlogPost.query.filter_by(
        published=True
    ).order_by(BlogPost.created_at.desc()).all()

    return render_template('blog/index.html', 
                         posts=posts, 
                         categories=categories)

@blog.route('/leercentrum', methods=['GET'])
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

    # Get content for the selected topic/subtopic from URL parameters
    selected_topic = request.args.get('topic')
    selected_subtopic = request.args.get('subtopic')

    content = None
    if selected_topic and selected_subtopic:
        content = LearningContent.query.filter_by(
            topic=selected_topic,
            subtopic=selected_subtopic
        ).order_by(LearningContent.order).all()

    return render_template('blog/learning_center.html', 
                         topics=topics,
                         content=content,
                         selected_topic=selected_topic,
                         selected_subtopic=selected_subtopic)

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

    # Get all categories for the form
    categories = {
        'actualiteit': {
            'title': 'Actualiteit & Nieuws',
            'subtopics': [
                'Maatschappij',
                'Gemeenschap',
                'Aankondigingen'
            ]
        },
        'vorming': {
            'title': 'Vorming & Educatie',
            'subtopics': [
                'Onderwijs & Onderzoek',
                'Opvoeding & Jeugd',
                'Workshops & Cursussen'
            ]
        },
        'gemeenschap': {
            'title': 'Gemeenschapsleven',
            'subtopics': [
                'Projecten & Initiatieven',
                'Vrijwilligers & Samenwerkingen'
            ]
        },
        'spiritualiteit': {
            'title': 'Geloof & Inspiratie',
            'subtopics': [
                'Aanbiddingen',
                'Reflecties & Inspiratie',
                'Lezingen',
                'Interlevensbeschouwelijk'
            ]
        }
    }

    # Determine if we're creating a video post based on the referrer
    is_video = request.referrer and 'gemeenschap' in request.referrer.lower()

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
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

        # Create the blog post
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
            is_featured=is_featured
        )

        # Handle categories and subcategories
        selected_categories = request.form.getlist('categories[]')
        selected_subcategories = request.form.getlist('subcategories[]')

        # Add main categories
        for category_name in selected_categories:
            category = BlogCategory.query.filter_by(name=category_name).first()
            if not category:
                category = BlogCategory(name=category_name)
                db.session.add(category)
            post.categories.append(category)

        # Add subcategories
        for subcategory_name in selected_subcategories:
            subcategory = BlogCategory.query.filter_by(name=subcategory_name).first()
            if not subcategory:
                subcategory = BlogCategory(name=subcategory_name)
                db.session.add(subcategory)
            post.categories.append(subcategory)

        # Calculate reading time
        post.reading_time = post.calculate_reading_time()

        db.session.add(post)
        db.session.commit()

        flash('Video succesvol toegevoegd!' if has_video else 'Artikel succesvol aangemaakt!', 'success')
        return redirect(url_for('blog.view', slug=post.slug))

    return render_template('blog/create.html', 
                         is_video=is_video,
                         categories=categories)

@blog.route('/leercentrum/toevoegen', methods=['GET', 'POST'])
@login_required
def add_learning_content():
    if not current_user.is_admin:
        flash('Alleen administrators kunnen content toevoegen.', 'error')
        return redirect(url_for('blog.learning_center'))

    form = LearningContentForm()

    if form.validate_on_submit():
        # Determine video platform if video URL is provided
        video_platform = None
        has_video = False
        if form.video_url.data:
            has_video = True
            if 'youtube' in form.video_url.data or 'youtu.be' in form.video_url.data:
                video_platform = 'youtube'
            elif 'vimeo' in form.video_url.data:
                video_platform = 'vimeo'

        content = LearningContent(
            title=form.title.data,
            content=form.content.data,
            topic=form.topic.data,
            subtopic=form.subtopic.data,
            order=form.order.data or 0,  # Default to 0 if no order specified
            author_id=current_user.id,
            video_url=form.video_url.data,
            video_platform=video_platform,
            has_video=has_video
        )

        db.session.add(content)
        db.session.commit()

        flash('Content succesvol toegevoegd!', 'success')
        return redirect(url_for('blog.learning_center', 
                              topic=form.topic.data,
                              subtopic=form.subtopic.data))

    return render_template('blog/learning_content_form.html', form=form)