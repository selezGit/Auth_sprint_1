"""Parsers and serializers for /auth API endpoints."""
from flask_restx.inputs import email
from flask_restx.reqparse import RequestParser

auth_register_parser = RequestParser(bundle_errors=True)
auth_register_parser.add_argument(name="login", type=str, location="form", required=True, nullable=False)
auth_register_parser.add_argument(name="email", type=email(check=True), location="form", required=True, nullable=False)
auth_register_parser.add_argument(name="password", type=str, location="form", required=True, nullable=False)


auth_login_parser = RequestParser(bundle_errors=True)
auth_login_parser.add_argument(name="login", type=str, location="form", required=True, nullable=False)
auth_login_parser.add_argument(name="password", type=str, location="form", required=True, nullable=False)

change_password_parser = RequestParser(bundle_errors=True)
change_password_parser.add_argument(name="old_password", type=str, location="form", required=True, nullable=False)
change_password_parser.add_argument(name="new_password", type=str, location="form", required=True, nullable=False)

change_email_parser = RequestParser(bundle_errors=True)
change_email_parser.add_argument(name="email", type=email(check=True), location="form", required=True, nullable=False)
change_email_parser.add_argument(name="password", type=str, location="form", required=True, nullable=False)

delete_me_parser = RequestParser(bundle_errors=True)
delete_me_parser.add_argument(name="password", type=str, location="form", required=True, nullable=False)