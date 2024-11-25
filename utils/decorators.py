from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user


def user_has_role(*role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Devi essere autenticato per accedere a questa pagina.")
                return redirect(url_for('login'))
            if not any(current_user.has_role(role) for role in role_names):
                flash("Non hai il permesso per accedere a questa pagina.")
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
