
from functools import wraps
from flask import request
from db.db_models import User




def token_required(f):
    """Проверка токена на авлидность"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token_payload = _check_access_token(admin_only=False)
        for name, val in token_payload.items():
            setattr(decorated, name, val)
        return f(*args, **kwargs)

    return decorated


def _check_access_token():
    token = request.headers.get("Authorization")
    if not token:
        raise ValueError(description="Unauthorized")
    result = User.decode_access_token(token)
    if result.failure:
        raise ValueError(
            description=result.error,
            error="invalid_token",
            error_description=result.error,
        )
    return result.value