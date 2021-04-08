from flask import Blueprint, session, render_template, request, g, current_app, make_response
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
	has_registered = False
	if g.user:
		has_registered = get_account(g.user['id'], 0, db.get_db()) is not None
	return render_template("home.html", len=len, has_registered=has_registered)

@bp.route('/test')
def test_session():
    # session['name'] = "adewale"
    print(request.cookies)
    print(session)

    res = make_response( session.get("name") or "no session")
    #res.set_cookie('name', 'aremu', max_age=60)
    return res

@bp.route('/reset_db')
def reset_db():
	import db as _db
	from werkzeug.security import generate_password_hash
	from utils.unique_id import generate_id
	from utils.hex_encryption import encrypt
	_db.init_db()
	c = "abcdefghijklmnopqrstuvwxyz"
	d = "xyz"
	j = -1
	for i in range(len(c)*2):
		if i % 26 == 0:
			j += 1
		addr, priv = current_app.config["ACCOUNTS"][i%len(current_app.config['ACCOUNTS'])].values()
		email = f"{c[i%26]}@{c[i%26]}.{c[i%26]}{d[j]}"
		pw = generate_password_hash(c[i%26].upper()+c[i%26]+"      ")
		db.add_account(email, pw, None)
		db.activate_email(i+1, generate_id(i), addr, encrypt(priv))
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