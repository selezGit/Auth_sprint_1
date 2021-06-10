from flask_restx import Model
from flask_restx.fields import String, Boolean, Integer, List, DateTime, Nested


auth_login_model = Model(
    'Login',
    {
        'access_token': String,
        'refresh_token': String,
        'expires_in': Integer,
        'token_type': String,
    }
)

user_create_model = Model(
    'Create',
    {
        'e-mail': String,
        'id': String,
        'login': String
    }
)


nested_history_model = Model(
    'History',
    {
        'active': Boolean,
        'date': DateTime(dt_format='rfc822'),
        'deviceType': String,
        'userAgent': String
    }
)

user_history_model = Model(
    'HistoryList',
    {
        'rows': List(Nested(nested_history_model))
    }
)
