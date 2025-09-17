"""
Main application routes.

This module contains the main application routes for the Aptitude Generator.
"""
from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from app.models.user import User, ExcelUserStore, UserStore
import os
import re
from . import bp


@bp.route('/')
def index():
    """Render the home page or redirect to dashboard if logged in."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    """Render the user dashboard."""
    # TODO: Replace with real stats when practice tests are implemented
    progress_percent = 0
    completed_tests = 0
    total_tests = 0
    return render_template(
        'dashboard.html',
        user=current_user,
        progress_percent=progress_percent,
        completed_tests=completed_tests,
        total_tests=total_tests,
    )


@bp.route('/account/edit', methods=['GET', 'POST'])
@login_required
def edit_account():
    """Allow the current user to edit their profile."""
    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()

        errors = []
        if not new_username:
            errors.append('Username is required.')
        if not new_email or '@' not in new_email:
            errors.append('Valid email is required.')

        # If username/email changed, ensure not taken by someone else
        if new_username != current_user.username:
            try:
                if ExcelUserStore.exists_username(new_username) or UserStore.exists_username(new_username):
                    errors.append('Username is already taken.')
            except Exception:
                if UserStore.exists_username(new_username):
                    errors.append('Username is already taken.')
        if new_email != current_user.email:
            try:
                if ExcelUserStore.exists_email(new_email) or UserStore.exists_email(new_email):
                    errors.append('Email is already registered.')
            except Exception:
                if UserStore.exists_email(new_email):
                    errors.append('Email is already registered.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('account_edit.html', user=current_user)

        # Apply updates to a new user object for persistence
        updated = User(username=new_username, email=new_email)
        updated.password_hash = current_user.password_hash
        updated.is_admin = getattr(current_user, 'is_admin', False)
        if new_password:
            updated.set_password(new_password)

        saved = False
        try:
            saved = ExcelUserStore.update_user(current_user.username, updated)
        except Exception:
            saved = False

        if not saved:
            # Fallback: update in-memory store
            # Remove old and add new
            # Simplest approach since store is ephemeral
            UserStore._users_by_username.pop(current_user.username, None)
            UserStore._users_by_email.pop(current_user.email, None)
            UserStore.add(updated)

        # Update current_user fields for active session
        current_user.username = updated.username
        current_user.email = updated.email
        current_user.password_hash = updated.password_hash
        current_user.is_admin = updated.is_admin

        flash('Account updated successfully.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('account_edit.html', user=current_user)


@bp.route('/practice')
def practice():
    """Show list of aptitude topics to begin practice."""
    topics = [
        {'title': 'Numerical Aptitude', 'slug': 'numerical-aptitude'},
        {'title': 'Verbal Aptitude', 'slug': 'verbal-aptitude'},
        {'title': 'Abstract / Logical Reasoning Aptitude', 'slug': 'abstract-logical-reasoning-aptitude'},
        {'title': 'Mechanical Aptitude', 'slug': 'mechanical-aptitude'},
        {'title': 'Spatial Aptitude', 'slug': 'spatial-aptitude'},
        {'title': 'Clerical / Perceptual Aptitude', 'slug': 'clerical-perceptual-aptitude'},
        {'title': 'Technical Aptitude', 'slug': 'technical-aptitude'},
        {'title': 'Creativity Aptitude', 'slug': 'creativity-aptitude'},
        {'title': 'Social / Emotional Aptitude', 'slug': 'social-emotional-aptitude'},
        {'title': 'Career-specific Aptitude Tests', 'slug': 'career-specific-aptitude-tests'},
    ]
    return render_template('practice.html', topics=topics)


def _parse_mcq_markdown(md_text: str):
    """Parse markdown file into a list of MCQ dicts with options and answer.

    Expected format per question:
    N) Question text
    - A) option
    - B) option
    - C) option
    - D) option
    Answer: X
    """
    lines = [l.strip() for l in md_text.splitlines()]
    questions = []
    current = None
    option_pattern = re.compile(r"^-\s*([A-Da-d])\)\s*(.+)$")
    q_pattern = re.compile(r"^\d+\)\s*(.+)$")
    answer_pattern = re.compile(r"^Answer:\s*([A-Da-d])(?:\b.*)?$")
    for line in lines:
        if not line:
            continue
        q_match = q_pattern.match(line)
        if q_match:
            if current is not None:
                # incomplete question without answer; skip adding
                pass
            current = {
                'question': q_match.group(1).strip(),
                'options': [],
                'answer': None,
            }
            questions.append(current)
            continue
        if current is not None:
            o_match = option_pattern.match(line)
            if o_match:
                key = o_match.group(1).upper()
                text = o_match.group(2).strip()
                current['options'].append({'key': key, 'text': text})
                continue
            a_match = answer_pattern.match(line)
            if a_match:
                current['answer'] = a_match.group(1).upper()
                current = None
                continue
    # filter valid questions
    return [q for q in questions if q.get('question') and q.get('options') and q.get('answer')]


@bp.route('/practice/<slug>')
def practice_topic(slug: str):
    """Render a topic page by loading markdown content from disk and showing MCQs."""
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'content')
    md_path = os.path.abspath(os.path.join(base_dir, f"{slug}.md"))
    # Ensure the path is within the content directory
    if not md_path.startswith(os.path.abspath(base_dir)):
        abort(404)
    if not os.path.exists(md_path):
        abort(404)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    questions = _parse_mcq_markdown(md_text)
    return render_template('practice_topic.html', questions=questions, slug=slug)
