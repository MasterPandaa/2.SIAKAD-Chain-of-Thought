from functools import wraps

from flask import abort
from flask_login import current_user


def role_required(*roles: str):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                # Let @login_required handle redirects if used together
                abort(401)
            # Resolve role to a plain string (supports Enum or raw string)
            role_value = (
                current_user.role.value
                if hasattr(current_user.role, "value")
                else current_user.role
            )
            if role_value not in roles:
                abort(403)
            return f(*args, **kwargs)

        return wrapper

    return decorator
