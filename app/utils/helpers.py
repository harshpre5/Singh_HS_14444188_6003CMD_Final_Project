from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    """Decorator to restrict access by user role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                abort(403)
            if not current_user.is_approved and current_user.role == 'employee':
                flash('Your account is pending approval.', 'info')
                return redirect(url_for('auth.pending'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def approval_required(f):
    """Decorator to ensure user account is approved."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_approved:
            flash('Your account is pending approval from a manager.', 'info')
            return redirect(url_for('auth.pending'))
        return f(*args, **kwargs)
    return decorated_function
