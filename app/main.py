from flask import Blueprint, session, render_template, request, g, current_app
from auth import user_needed, user_required
from exmat.contract_db_mg import get_account
import db_functions as db

bp = Blueprint('main', __name__)

@bp.route('/')
@user_needed
def home():
#     for i in dir(g.user):
#         print(i)
#     print(g.user.keys())
	has_registered = get_account(g.user['id'], 0, db.get_db()) is not None
	return render_template("home.html", len=len, has_registered=has_registered)

@bp.route('/reset_db')
def reset_db():
	import db as _db
	from werkzeug.security import generate_password_hash
	from utils.unique_id import generate_id
	_db.init_db()
	c = "abcdefghijklmnopqrstuvwxyz"
	for i in range(len(current_app.config['ACCOUNTS'])):
		email = f"{c[i]}@{c[i]}.{c[i]}"
		pw = generate_password_hash(c[i].upper()+c[i]+"      ")
		db.add_account(email, pw, None)
		db.activate_email(i+1, generate_id(i), **current_app.config["ACCOUNTS"][i])
	return "database reset successful"

@bp.route('/request')
def request_prop():
	from pprint import pprint
	data = {}
	for p in dir(request):
		if p[0] != '_' and p[0].islower():
			try:
				data[p] = str(eval('request.'+p))
			except TypeError:
				data[p] = eval('request.'+p)
	pprint(data)
	return data

@bp.route('/view/<table>')
def view_table(table):
	cur = db.get_db().cursor()
	cur.execute(f'select * from {table}')
	return render_template("view_table.html", cur=cur)