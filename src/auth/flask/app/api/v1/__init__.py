from flask import Blueprint
from flask_restx import Api


from .views.auth import auth_ns
from .views.user import user_ns

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")
authorizations = {
    "access_token": {"type": "apiKey",
                     "in": "header",
                     "name": "Authorization"}
}

api = Api(
    api_bp,
    version="1.0",
    title="API Auth with JWT tokens",
    description="Welcome to the Swagger UI documentation site!",
    authorizations=authorizations,
)

api.add_namespace(auth_ns, path="/auth")
api.add_namespace(user_ns, path="/user")
