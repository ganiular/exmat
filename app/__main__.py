from flask import Blueprint, session
import db_functions as db

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
	user_id = session.get("user_id")
	if not user_id:
		return "1) Login \n2) Register"
	user = db.get_user(user_id)
	return "welcome {user['email']}\n1) Logout"

@bp.route('/reset_db')
def reset_db():
	db.init_db()
	return "database reset successful"
