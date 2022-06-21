import os
import jwt
import datetime
from app.api import users
from app.api.model import db
from flask import request, abort
from app.api.model.user import User, user_schema
from app.api.utils import (
    check_for_whitespace,
    custom_make_response,
    isValidPassword,
    isValidEmail,
    generate_unique_string
)

# get environment variables
KEY = os.getenv("SECRET_KEY")
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')


@users.route('/users/login', methods=["POST"])
def user_signin():
    """
    Signin a user into the system.
    """
    try:
        user_data = request.get_json()

        if ('email' or 'password') not in user_data.keys():
            abort(
                400,
                """
                Email and or password is missing,
                please check and try again.""")

        email = user_data['email']
        password = user_data['password']

        check_for_whitespace(user_data, ["email", "password"])
        isValidEmail(email)
        isValidPassword(password)

        user = User.query.filter_by(email=email).first()
        if not user:
            abort(
                404,
                "User account could not be found,\
                    Please sign up to use the application.")

        _user = user_schema.dump(user)
        _password = _user["password"]

        if not User.compare_password(_password, password):
            abort(
                403,
                "Email and or password is incorrect,\
                    please check and try again.")

        token = jwt.encode(
            {
                "id": _user["user_sys_id"],
                "exp":
                datetime.datetime.utcnow() + datetime.timedelta(minutes=480),
            },
            KEY,
            algorithm="HS256",
        )
        response = custom_make_response(
            "data",
            {
                "message":
                "Signed in successfully preparing your dashboard...",
                "auth_token": token.decode('utf-8'),
                "screen_name": _user['username'],
            }, 200
        )
        return response

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@users.route('/admin')
def create_admin():
    """
    create admin account, account is only
    created if it does not exist
    """
    admin_user = User.query.filter_by(
        email=ADMIN_EMAIL).filter_by(email=ADMIN_EMAIL).first()
    if admin_user:
        abort(409, "An admin account already exists.")

    # create account
    admin_id = generate_unique_string()
    new_admin_user = User(
        user_sys_id=admin_id, email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD, username='Flo')
    db.session.add(new_admin_user)
    db.session.commit()

    return custom_make_response(
        "data",
        "Admin account created successfully",
        201
    )
