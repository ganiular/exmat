import re
from datetime import datetime
from functools import wraps

from flask import (
	Blueprint, render_template, redirect, url_for, request,
	session, current_app, g
)
from werkzeug.security import check_password_hash, generate_password_hash
from utils import safe
from utils.data_signature import verify
from utils.hex_encryption import encrypt
from utils import mail
from utils.unique_id import generate_id
from utils.decorators import sense_response
import db_functions as db


bp = Blueprint('auth', __name__)

def activated_required(f):
	@wraps(f)
	def wrapped(*args, **kwargs):
		user_id = session.get('user_id')
		if user_id:
			g.user = db.get_user(user_id)
			if g.user:
				update_user_login(user_id)
				if g.user["activated"]:
					return f(*args, **kwargs)
				else:
					return redirect(url_for("auth.email_confirmation", next=request.url))
		return redirect(url_for("auth.login", next=request.url))
	return wrapped

def user_required(f):
	@wraps(f)
	def wrapped(*args, **kwargs):
		user_id = session.get('user_id')
		if user_id:
			g.user = db.get_user(user_id)
			if g.user:
				update_user_login(user_id)
				return f(*args, **kwargs)
		print('user_id:', user_id)
		return redirect(url_for("auth.login", next=request.url))
	return wrapped

def user_needed(f):
	@wraps(f)
	def decorated_func(*args, **kwargs):
		user_id = session.get('user_id')
		if not user_id:
			g.user = None
		else:
			g.user = db.get_user(user_id)
			update_user_login(user_id)
		return f(*args, **kwargs)
	return decorated_func

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if session.get("user_id") is None:
			return {"success":False, "message":"login required", 
					"redirect":url_for("auth.login")}
		return view(**kwargs)
	return wrapped_view

@bp.route("/register-new/s-<sponsor_referring_id>", methods=('GET','POST'))
@bp.route("/register-new", methods=('GET','POST'))
@sense_response
def register(sponsor_referring_id=''):
	if request.method == "POST":
		if request.is_json:
			data = request.json
		else:
			data = request.form
		email = data.get('email', '').lower()
		password = data.get('password')
		cpw = data.get('cpassword')
		if not email:
			return {"success":False, "message":'email is required'}
		elif not safe.is_email(email):
			return {"success":False, "message":'invalid email'}
		elif not password:
			return {"success":False, "message":"password is required"}
		elif not cpw:
			return {"success":False, "message":"confirm password is required"}
		elif len(password) < 8:
			return {"success":False, "message":"password must be at least 8 characters"}
		elif not re.search('[A-Z]', password):
			return {"success":False, "message":"password must include upper-case"}
		elif not re.search('[a-z]', password):
			return {"success":False, "message":"password must include lower-case"}
		elif not re.search('[\\W\\b_]', password):
			return {"success":False, "message":"password must include non aphabet"}
		elif cpw != password:
			return {"success":False, "message":"password not matched"}

		user = db.get_user(email)
		if user is not None and user["activated"]:
			return {"success":False, "message":'email is already taken'}

		sponsor_id = None
		sponsor_referring_id = (sponsor_referring_id or data.get('sponsor','')).lower()
		if sponsor_referring_id:
			if safe.is_text_id(sponsor_referring_id):
				sponsor = db.get_user(sponsor_referring_id)
				if sponsor:
					sponsor_id = sponsor['id']

		user_id = db.add_account(email, generate_password_hash(password), sponsor_id)
# 		address, private_key = current_app.config['ACCOUNT'][user_id].values()
# 		db.add_address(user_id, address, private_key)

		session.clear()
		session["user_id"] = user_id
		return {
			"success":True,
			"message":'account created',
			"redirect": url_for("auth.email_confirmation")
		}

	return {"template":"auth/register.html", "sponsor_id":sponsor_referring_id}


@bp.route("/login", methods=("POST","GET"))
def login():
	if request.method == "POST":
		if request.is_json:
			data = request.json
		else:
			data = request.form
		email = data.get('email', '').lower()
		pw = data.get('password')

		if not email:
			return {"success":False, "message":"email is required"}
		elif not pw:
			return {"success":False, "message":"password is required"}
		elif not safe.is_email(email):
			return {"success":False, "message":'invalid email'}

		user = db.get_user(email)
		if user is None or not check_password_hash(user['password'], pw):
			return {"success":False, 
					"message":'incorrect email or password'}

		session.clear()
		session['user_id'] = user['id']
        
		if not user["activated"]:
			return {"success":False, "message":'unactivated account',
					"redirect":url_for("auth.email_confirmation")}

		return {"success":True, "message":"logged in", 
				"redirect": request.args.get('next') or url_for("main.home")}
	return render_template("auth/login.html")

@bp.route("/logout")
@sense_response
def logout():
	session.clear()
	return {"success":True, "message":"logged out", 
			"redirect":url_for("auth.login")}

@bp.route("/auth/email-confirmation", methods=('GET','POST'))
@user_required
@sense_response
def email_confirmation():
	# send new confirmation code for every reload
	if g.user["activated"]:
			return {"success":True, "message":'email is already confirmed',
					"redirect":url_for("main.home")}

	if g.user["error_triers"] >= current_app.config['MAXIMUM_ERROR_TRIER']:
		tsec = int((datetime.today() - db.get_last_time_error(g.user['id'])).total_seconds())
		if tsec < current_app.config['PENALTY_PERIOD']:
			rs = current_app.config['PENALTY_PERIOD'] - tsec
			return dict(success=False, template="confirmation.html",
				message=f"You have made {g.user['error_triers']} confirmation errors, "
						f"retry again after {rs//3600} hr, {(rs%3600)//60} min and {(rs%3600)%60} sec",
				)
	user_id = g.user['id']
	if request.method == "GET":
		code = safe.make_code()
		db.set_confirmation(
			user_id,
			"confirm email", 
			generate_password_hash(code),
			datetime.today()
		)
		mail.send_email_confirmation_code(g.user["email"], code)
		print('code:', code)
		return dict(template="confirmation.html")

	if request.method == "POST":
		if request.is_json:
			code = request.json.get('code')
		else:
			code = request.form.get('code')
		if not code:
			return dict(success=False, message="confirmation code is required")
		elif re.fullmatch('[0-9]{6}', code):
			conf = db.get_confirmation(user_id)
			if conf and conf["name"] == "confirm email":
				tr = datetime.today() - conf["created"]
				if tr.seconds > current_app.config['CONFIRMATION_TIMEOUT']:
					return {"success":False, "message":"code expired"}
				elif check_password_hash(conf["code"], code):
					address, private_key = current_app.config['ACCOUNTS'][(user_id-1)%len(current_app.config['ACCOUNTS'])].values()
					db.activate_email(
						user_id,
						generate_id(user_id - 1),
						address,
						encrypt(private_key),
					)
					# db.reset_triers(g.user['id'])
					return dict(success=True, message="email confirmed", redirect=url_for("main.home"))
		db.increase_triers(g.user["id"])
		return dict(success=False, message="confirmation error")

def update_user_login(user_id):
	db.update_user_login(user_id, datetime.today())

@bp.route("/auth/password-confirmation", methods=("GET", "POST"))
@sense_response
def password_confirmation():
	if not session.get('is_email_set'):
		return dict(success=False, message="email not set", redirect=url_for('auth.resetpassword'))

	user = db.get_user(session['user_id_set'])
	if user["error_triers"] >= current_app.config['MAXIMUM_ERROR_TRIER']:
		tsec = int((datetime.today() - db.get_last_time_error(user['id'])).total_seconds())
		if tsec < current_app.config['PENALTY_PERIOD']:
			rs = current_app.config['PENALTY_PERIOD'] - tsec
			return dict(success=False, template="confirmation.html",
				message=f"You have made {user['error_triers']} confirmation errors, "
						f"retry again after {rs//3600} hr, {(rs%3600)//60} min and {(rs%3600)%60} sec",
				)

	if request.method == "GET":
		code = safe.make_code()
		db.set_confirmation(
			session['user_id_set'],
			"change password", 
			generate_password_hash(code),
			datetime.today()
		)
		mail.send_email_confirmation_code(session["email_set"], code)
		print('code:', code)
		return dict(template="confirmation.html")

	if request.method == "POST":
		if request.is_json:
			code = request.json.get('code')
		else:
			code = request.form.get('code')
		if not code:
			return dict(success=False, message="confirmation code is required")
		elif re.fullmatch('[0-9]{6}', code):
			conf = db.get_confirmation(session["user_id_set"])
			if conf and conf["name"] == "change password":
				tr = datetime.today() - conf["created"]
				if tr.seconds > current_app.config['CONFIRMATION_TIMEOUT']:
					return {"success":False, "message":"code expired"}
				elif check_password_hash(conf["code"], code):
					session["is_confirmed"] = True
					session["confirmed_time"] = datetime.today()
					db.reset_triers(session['user_id_set'])
					return dict(success=True, message="confirmed password change", 
							redirect=url_for("auth.resetpassword"))
		db.increase_triers(session['user_id_set'])
		return dict(success=False, message="confirmation error")

@bp.route('/resetpassword', methods=('GET','POST'))
@sense_response
def resetpassword():
	if request.method == "GET":
		if not session.get('is_email_set'):
			return dict(template="auth/get_email.html")
		elif not session.get('is_confirmed'):
			return dict(redirect=url_for('auth.password_confirmation'))
		else:
			return dict(template="auth/set_password.html")

	if request.method == "POST":
		if request.is_json:
			data = request.json
		else:
			data = request.form
		if not session.get('is_email_set'):
			email = data.get('email', '').lower()
			if not email:
				return dict(success=False, message="email is required")
			if not safe.is_email(email):
				return dict(success=False, message="invalid email")
			user = db.get_user(email)
			if not user:
				return dict(success=False, message="unidentified email")
			session['email_set'] = email
			session['user_id_set'] = user['id']
			session['is_email_set'] = True
			return dict(redirect=url_for("auth.password_confirmation"),
					success=True, message="email verified")
		elif not session.get('is_confirmed'):
			return dict(redirect=url_for("auth.password_confirmation"))
		else:
			password = data.get('password')
			cpw = data.get('cpassword')
			if not password:
				return {"success":False, "message":"password is required"}
			elif not cpw:
				return {"success":False, "message":"confirm password is required"}
			elif len(password) < 8:
				return {"success":False, "message":"password must be at least 8 characters"}
			elif not re.search('[A-Z]', password):
				return {"success":False, "message":"password must include upper-case"}
			elif not re.search('[a-z]', password):
				return {"success":False, "message":"password must include lower-case"}
			elif not re.search('[\\W\\b_]', password):
				return {"success":False, "message":"password must include non aphabet"}
			elif cpw != password:
				return {"success":False, "message":"password not matched"}

			tr = datetime.today() - session["confirmed_time"]
			if tr.seconds > current_app.config["TRANSACTION_TIMEOUT"]:
				session.clear()
				return {"success":False, "message":"transaction timeout"}

			db.update_password(session["user_id_set"], generate_password_hash(password))
			session.clear()
			return dict(success=True, message="password reset", redirect=url_for('auth.login'))

