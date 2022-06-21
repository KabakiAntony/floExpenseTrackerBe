from flask import Blueprint

users = Blueprint("users", __name__, url_prefix="")
expenses = Blueprint("expenses", __name__, url_prefix="")