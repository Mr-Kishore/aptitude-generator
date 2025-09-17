"""
Main application routes.

This module contains the main application routes for the Aptitude Generator.
"""
from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from app.models.user import User, ExcelUserStore, UserStore
from app.models.progress import progress_store
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
    # Get user progress data
    user_progress = progress_store.get_user_progress(current_user.username)
    overall_stats = user_progress.get_overall_progress()
    
    # Define all available categories
    categories = [
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
    
    # Get progress for each category
    category_progress = []
    for category in categories:
        progress = user_progress.get_category_progress(category['slug'])
        category_progress.append({
            'title': category['title'],
            'slug': category['slug'],
            'questions_attempted': progress.questions_attempted,
            'questions_correct': progress.questions_correct,
            'accuracy_percentage': progress.accuracy_percentage,
            'completion_percentage': progress.completion_percentage,
            'last_attempted': progress.last_attempted
        })
    
    # Get recent activities from progress data
    recent_activities = []
    
    # Add quiz completion activities (most recent first)
    for activity in reversed(user_progress.activities[-5:]):  # Show last 5 activities
        if activity['type'] == 'quiz_completed':
            # Get category title from slug
            category_title = next((cat['title'] for cat in categories if cat['slug'] == activity['category_slug']), activity['category_slug'])
            recent_activities.append(f"Completed {category_title} - {activity['score']}")
    
    # If no activities, show account creation
    if not recent_activities:
        recent_activities = ["Created an account"]
    
    return render_template(
        'dashboard.html',
        user=current_user,
        overall_stats=overall_stats,
        category_progress=category_progress,
        recent_activities=recent_activities,
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


@bp.route('/profile')
@login_required
def profile():
    """Show user profile with detailed statistics."""
    # Get user progress data
    user_progress = progress_store.get_user_progress(current_user.username)
    overall_stats = user_progress.get_overall_progress()
    
    # Define all available categories
    categories = [
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
    
    # Get detailed progress for each category
    category_progress = []
    for category in categories:
        progress = user_progress.get_category_progress(category['slug'])
        category_progress.append({
            'title': category['title'],
            'slug': category['slug'],
            'questions_attempted': progress.questions_attempted,
            'questions_correct': progress.questions_correct,
            'accuracy_percentage': progress.accuracy_percentage,
            'completion_percentage': progress.completion_percentage,
            'last_attempted': progress.last_attempted
        })
    
    # Get recent activities
    recent_activities = []
    for activity in reversed(user_progress.activities[-10:]):  # Show last 10 activities
        if activity['type'] == 'quiz_completed':
            category_title = next((cat['title'] for cat in categories if cat['slug'] == activity['category_slug']), activity['category_slug'])
            recent_activities.append({
                'type': 'quiz_completed',
                'description': f"Completed {category_title}",
                'score': activity['score'],
                'timestamp': activity['timestamp']
            })
    
    # Calculate additional statistics
    total_categories = len(categories)
    categories_started = len([cat for cat in category_progress if cat['questions_attempted'] > 0])
    categories_completed = len([cat for cat in category_progress if cat['completion_percentage'] >= 100])
    
    # Calculate study streak (simplified - based on recent activities)
    study_streak = 0
    if recent_activities:
        # Simple streak calculation based on consecutive days with activities
        from datetime import datetime, timedelta
        today = datetime.now().date()
        current_date = today
        
        for activity in reversed(recent_activities):
            activity_date = datetime.fromisoformat(activity['timestamp']).date()
            if activity_date == current_date:
                study_streak += 1
                current_date -= timedelta(days=1)
            elif activity_date < current_date:
                break
    
    return render_template('profile.html',
                         user=current_user,
                         overall_stats=overall_stats,
                         category_progress=category_progress,
                         recent_activities=recent_activities,
                         total_categories=total_categories,
                         categories_started=categories_started,
                         categories_completed=categories_completed,
                         study_streak=study_streak)


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
    
    # Get user's current progress for this category
    user_progress = progress_store.get_user_progress(current_user.username)
    category_progress = user_progress.get_category_progress(slug)
    
    return render_template('practice_topic.html', 
                         questions=questions, 
                         slug=slug,
                         category_progress=category_progress)


@bp.route('/practice/<slug>/submit', methods=['POST'])
@login_required
def submit_practice(slug: str):
    """Handle quiz submission and update user progress."""
    print(f"DEBUG: Submit practice called for slug: {slug}")
    print(f"DEBUG: Form data: {dict(request.form)}")
    
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
    
    print(f"DEBUG: Found {len(questions)} questions")
    
    # Calculate results
    correct_answers = 0
    total_questions = len(questions)
    
    for i, question in enumerate(questions):
        user_answer = request.form.get(f'question_{i}')
        print(f"DEBUG: Question {i}: user_answer={user_answer}, correct_answer={question['answer']}")
        if user_answer and user_answer.upper() == question['answer']:
            correct_answers += 1
    
    print(f"DEBUG: Final score: {correct_answers}/{total_questions}")
    
    # Update user progress
    progress_store.update_user_progress(
        current_user.username, 
        slug, 
        total_questions, 
        correct_answers
    )
    
    print(f"DEBUG: Progress updated for user {current_user.username}")
    
    # Calculate percentage
    percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    flash(f'Quiz completed! You scored {correct_answers}/{total_questions} ({percentage:.1f}%)', 'success')
    return redirect(url_for('main.dashboard'))
