from utils.color import print_color
from utils import safe
import db_functions as db
from flask import Blueprint, current_app, g, session, request, redirect, url_for
from auth import activated_required, sense_response
from exmat import contract_db_mg as cd
from tronpy import Tron
from tronpy.keys import PrivateKey

bp = Blueprint('contract', __name__)
client = Tron(
		network="shasta" # current_app.config["NETWORK"]
	)

@bp.route("/s/init")
def init():
	cur = db.get_db().cursor()
	cd.init_db(cur)
	cd.add_account(1, 0, 0, cur)
	for level in range(current_app.config["MAX_LEVEL"] + 1):
		cd.add_x3matrix(1, 0, level, cur)
		cd.add_upgrade(1, 0, 1, level, cur)
		cd.add_upgrade(1, 0, 2, level, cur)
	cur.connection.commit()

	results = []
	for i in range(1, 15):
		print_color(f'{i}'.center(78, ' '))
		session["user_id"] = i
# 		if i in (5,8):
# 		    results.append(register(3))
		if i >2:
		    if i== 4:
		        session["user_id"] = 3
		        results.append(buy_matrix(1,1))
		        session["user_id"] = 2
		        results.append(buy_matrix(1,1))
		        results.append(add_account('3wkzu'))
		        session["user_id"] = 4
		    results.append(register(2))
		else:
		    results.append(register())
	return str(results)

@bp.route('/s/register')
@activated_required
def register(sponsor=1):
	cur = db.get_db().cursor()
	if cd.get_account(g.user['id'], 0, cur):
		return dict(success=False, message="you've already registered")
	cd.add_account(g.user['id'], g.user['sponsor_id'] or sponsor, 0, cur)
	return buy_matrix(1, 0)

@bp.route('/s/login/<int:user_id>')
def login(user_id):
    session['user_id'] = user_id
    return redirect(url_for("contract.dashboard"))

@bp.route('/s/dashboard')
@activated_required
@sense_response
def dashboard():
    cur = db.get_db().cursor()
    user_id = g.user['id']
    sponsor_count = cd.get_sponsor_count(user_id, cur)
    partner_count = cd.get_partner_count(user_id, cur)
    sponsors = cd.query_sponsors(user_id, cur)
    def query_slot(matrix, level):
        return cd.query_slot(user_id, matrix, level, cur) or cur
    def pt(flag):
        return cd.pt(flag, cur)
    def has_matrix(matrix, level):
        return cd.get_x3matrix(user_id, level, cur) is not None
    return dict(success=True, sponsors=sponsors, 
        query_slot=query_slot, sponsor_count=sponsor_count, 
        partner_count=partner_count, paytypes=pt,
        has_matrix=has_matrix)

@bp.route("/s/buymatrix/<int:matrix>/<int:level>")
@activated_required
def buy_matrix(matrix, level):
	if not (0 < matrix < 3) or not (0 <= level <= current_app.config['MAX_LEVEL']):
		return dict(success=False, message="invalid parameters")

	db_conn = db.get_db()
	cur = db_conn.cursor()
	if cd.get_upgrade(g.user['id'], matrix, level, cur):
		return dict(success=False, message=f"level already activated")

	if level == 0:
		cost = 0
	else:
		if not cd.get_upgrade(g.user['id'], matrix, level - 1, cur):
			return dict(success=False, message=f"{level-1} is not activated")

		cost = current_app.config["MIN_PRICE"] * 2 ** (level-1) * current_app.config['CHARGE_RATE']
		cost = round(cost, 2)
		if False: # client.get_account_balance(g.user["address"]) < cost:
			return dict(success=False, message=f"insufficient balance, {cost} USDT is required")

	sponsor_id = cd.get_sponsor_id(g.user['id'], 0, cur)
	print_color(f"buy matrix: {dict(buyer=g.user['id'], sponsor_id=sponsor_id, matrix=('x3' if matrix==1 else 'x4'), level=level, cost=cost)}", 255, 50, 200)

	if matrix == 1:
		payee_id, payer_id, paytype = find_x3_payee(sponsor_id, g.user['id'], level, 1, cur)
	elif matrix == 2:
		payee_id, payer_id, paytype = find_x4_payee(sponsor_id, g.user['id'], level, 1, cur)

	print_color(f"found: {dict(payee_id=payee_id, payer_id=payer_id, paytype=cd.pt(paytype, cur))}", 150,150,255)
	if not payee_id:
		payee_id = 1

	payee = db.get_user(payee_id)
	payer = db.get_user(payer_id)
# 	priv_key = PrivateKey(bytes.fromhex(g.user["private_key"]))

# 	txn = (
# 		client.trx.transfer(g.user["address"], payee["address"], cost)
# 		.memo(f"buyMatrix(user_id:{g.user['referring_id']}, beneficiary_id:{payee['referring_id']}, matrix:{matrix}, level:{level}) @ exmat.io")
# 		.build()
# 		.sign(priv_key)
# 	)
	result = dict(result=True) #txn.broadcast()
	if result['result'] == True:
		cd.add_payment(payee['id'], payer['id'], matrix, level, paytype, "txn.txid", cur)
		cd.add_upgrade(g.user["id"], payee['id'], matrix, level, cur)
		db_conn.commit()
		return dict(success=True, message="matrix upgraded") #.update(result)
	return dict(success=False, message="matrix upgrade error") #.update(result)

@bp.route('/s/addaccount', methods=("POST",))
@activated_required
def add_account(sponsor_referring_id=''):
	if request.is_json:
		sponsor_referring_id = request.json.get('sponsor')
	else:
		sponsor_referring_id = sponsor_referring_id or request.form.get('sponsor')

	if not sponsor_referring_id:
		return dict(success=False, message="inviter id is required")
	elif not safe.is_text_id(sponsor_referring_id):
		return dict(success=False, message="invalid inviter id")
	sponsor = db.get_user(sponsor_referring_id)
	user_id = g.user['id']
	if not sponsor:
		return dict(success=False, message="inviter not identified")
	elif sponsor['id'] == user_id:
		return dict(success=False, message="self invitation is not allowed")

	db_conn = db.get_db()
	cur = db_conn.cursor()
	if cd.found_account(g.user['id'], sponsor["id"], cur):
		return dict(success=False, message="can't use an inviter twice")
	elif not (cd.get_x3matrix(user_id,1, cur)): # and cg.get_x4matrix(user_id,1, cur)):
		return dict(success=False, message="you haven't ugrade both matrix to level 1")
	elif not (cd.get_x3matrix(sponsor["id"],1, cur)): # and cg.get_x4matrix(sponsor["id"],1, cur)):
		return dict(success=False, message="inviter haven't ugrade both matrix to level 1")
	cost = current_app.config["MIN_PRICE"] * 2
# 	if client.get_account_balance(g.user["address"] < cost):
# 		return dict(success=False, message=f"insufficient balance, {cost} USDT is required")

	cd.add_account(user_id, sponsor['id'], cd.get_sponsor_count(user_id, cur), cur)
	print_color(f"account added: {dict(user_id=user_id, sponsor_id=sponsor['id'])}", 100, 200, 180)

	find_x3_payee(sponsor['id'], user_id, 0, 1, cur)
	#find_x4_payee(sponsor['id'], user_id, 0, 1, cur)

	payee_id, payer_id, paytype = find_x3_payee(sponsor['id'], user_id, 1, 1, cur)

	if not payee_id:
		payee_id = 1
	payee = db.get_user(payee_id)
	payer = db.get_user(payer_id)
# 	priv_key = PrivateKey(bytes.fromhex(g.user["private_key"]))

# 	txn = (
# 		client.trx.transfer(g.user["address"], payee["address"], cost)
# 		.memo(f"addAccount(user_id:{g.user['referring_id']}, inviter_id:{sponsor['referring_id']}, beneficiary_id:{payee['referring_id']}) @ exmat.io")
# 		.build()
# 		.sign(priv_key)
# 	)
	result = dict(result=True) #txn.broadcast()
	if result['result'] == True:
		cd.add_payment(payee['id'], payer['id'], 1, 1, paytype, "txn.txid", cur)
		cd.add_upgrade(g.user["id"], payee['id'], 1, 1, cur)
		db_conn.commit()
	else:
		return dict(success=False, message="account adding error") #.update(result)

# 	payee_id, payer_id, paytype = find_x4_payee(sponsor, g.user, 1, 1, cur)

# 	if not payee_id:
# 		payee_id = 1
# 	payee = db.get_user(payee_id)
# 	priv_key = PrivateKey(bytes.fromhex(g.user["private_key"]))

# 	txn = (
# 		client.trx.transfer(g.user["address"], payee["address"], cost)
# 		.memo(f"addAccount(user_id:{g.user['referring_id']}, inviter_id:{sponsor['referring_id']}, beneficiary_id:{payee['referring_id']}) @ exmat.io")
# 		.build()
# 		.sign(priv_key)
# 	)
# 	result = dict(result=True) #txn.broadcast()
# 	if result['result'] == True:
# 		cd.add_payment(payee['id'], payer['id'], matrix, level, paytype, 1, 0, "txn.txid", cur)
# 		cd.add_upgrade(g.user["id"], payee['id'], matrix, level, cur)
# 		db_conn.commit()
# 	else:
# 		return dict(success=False, message="account adding error") #.update(result)
	return dict(success=False, message="account added") #.update(result)

def find_x3_payee(user_id, part_id, level, paytype, cur):
	print_color(f"got {dict(user_id=user_id, part_id=part_id, level=level, paytype=cd.pt(paytype, cur))}",200,255,255)

	if not user_id:
		return user_id, part_id, paytype

	slot_count = cd.get_slot_count(user_id, 1, level, cur)
	index = (slot_count+1) // (3 * current_app.config['MAX_REOPEN'])
	matrix = cd.get_x3matrix(user_id, level, cur)
	# print_color(f"got user matrix: {dict((x,matrix[x]) for x in matrix.keys())}", 255,180,10)

	if not matrix:
		cd.add_miss_payment(user_id, part_id, 1, level, paytype, 1, cur)
		print_color(f"missed payment: {dict(payee=user_id, payer=part_id, matrix='x3', level=level, paytype=cd.pt(paytype, cur), reason=cd.rs(1, cur))}", 255,180,180)

		if paytype == 1:
			paytype = 2
		return find_x3_payee(cd.get_sponsor_id(user_id, index, cur), part_id, level, paytype, cur)
	if paytype in (1,2):
	    cd.add_x3matrix(part_id, user_id, level, cur)

	spon_count = cd.get_sponsor_count(user_id, cur)

	# check for reopen
	if (slot_count % 3) == 2:
		cd.add_slot(user_id, part_id, 1, level, 3, paytype, cur)
		print_color(f"slot filled: {dict(owner=user_id, filler=part_id, matrix='x3', level=level, position=3, paytype=cd.pt(paytype, cur))}", 255,180,180)
		print_color(f"reinvestemt: {dict(user_id=user_id, matrix='x3', level=level, count=(slot_count+1)//3)}", 255,150)

		# check if all accounts are full
		if index >= spon_count:
			print_color("all account full, payment to the next sponsor")
			nsi = matrix['next_sponsor_index']
			cd.set_x3_next_sponsor_index(user_id, level, nsi + 1 if nsi+1 < spon_count else 0, cur)
			return find_x3_payee(cd.get_sponsor_id(user_id, nsi, cur), user_id, level, 5, cur)
		# check if current account is full
		elif ((slot_count+1) % (3 * current_app.config['MAX_REOPEN'])) == 0:
			print_color("current account full, switching to the next account")
			print_color(f"account switched: {dict(user_id=user_id, sponsor_id={}, matrix='x3', level=level, count=index + 1)}", 100,200,255)

			cd.remove_x3matrix(matrix["id"], cur)
			assert cur.lastrowid != 0, "could not remove matrix"
			
			if level in (0,1):
				return find_x3_payee(cd.get_sponsor_id(user_id, 0, cur), user_id, level, 4, cur)
			else:
				return find_x3_payee(cd.get_sponsor_id(user_id, index, cur), user_id, level, 1, cur)
		else:
			return find_x3_payee(cd.get_sponsor_id(user_id, index, cur), user_id, level, 3, cur)

	cd.add_slot(user_id, part_id, 1, level, (slot_count % 3 + 1), paytype, cur)
	print_color(f"slot filled: {dict(owner=user_id, filler=part_id, matrix='x3', level=level, position=slot_count%3+1, paytype=cd.pt(paytype, cur))}", 255,180,180)

	if cd.is_offline_user(user_id, cur):
		cd.add_miss_payment(user_id, part_id, 1, level, paytype, 2, cur)
		print_color(f"missed payment: {dict(payee=user_id, payer=part_id, matrix='x3', level=level, paytype=cd.pt(paytype, cur), reason=cd.rs(2, cur))}", 255,180,180)

		npi = matrix['next_partner_index']
		downline, count = cd.get_next_downline(user_id, 1, level, npi, cur)
		
		cd.set_x3_next_partner_index(user_id, level, npi+1, cur)
		return find_x3_payee(downline, user_id, level, 6, cur)
	# if all account is full
	if index >= spon_count:
		print_color("all account full, payment to the next downline")
		cd.add_miss_payment(user_id, part_id, 1, level, paytype, 3, cur)
		print_color(f"missed payment: {dict(payee=user_id, payer=part_id, matrix='x3', level=level, paytype=cd.pt(paytype, cur), reason=cd.rs(3, cur))}", 255,180,180)

		npi = matrix['next_partner_index']
		downline, npi = cd.get_next_downline(user_id, 1, level, npi, cur)
		
		cd.set_x3_next_partner_index(user_id, level, npi+1, cur)
		return find_x3_payee(downline, user_id, level, 6, cur)
	return user_id, part_id, paytype

def find_x4_payee(user_id, part_id, level, paytype, cur):
	print_color(f"x4 got {dict(user_id=user_id, part_id=part_id, level=level, paytype=cd.pt(paytype, cur))}",200,255,255)

	if not user_id:
		return user_id, part_id, paytype


if __name__ == "__main__":
	db.show_table()
	register(0,1)
