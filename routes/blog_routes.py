from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from models import BlogPost
from datetime import datetime

blog = Blueprint('blog', __name__)

@blog.route('/blog')
def index():
    posts = BlogPost.query.filter_by(
        published=True
    ).order_by(BlogPost.created_at.desc()).all()
    return render_template('blog/index.html', posts=posts)

@blog.route('/blog/<slug>')
def view(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    return render_template('blog/view.html', post=post)

@blog.route('/blog/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        flash('Only administrators can create blog posts.', 'error')
        return redirect(url_for('blog.index'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        image_url = request.form.get('image_url')
        
        # Create URL-friendly slug from title
        slug = title.lower().replace(' ', '-')
        
        post = BlogPost(
            title=title,
            content=content,
            excerpt=excerpt,
            image_url=image_url,
            slug=slug,
            author_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('blog.view', slug=post.slug))
        
    return render_template('blog/create.html')
