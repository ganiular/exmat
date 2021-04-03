from db import get_db

def commit_db(command, args, db_conn=None):
	con = db_conn or get_db()
	cur = con.cursor()
	cur.execute(command, args)
	return db_conn or con.commit()

def query_one(command, args=None):
	cur = get_db().cursor()
	if args:
		return cur.execute(command, args).fetchone()
	return cur.execute(command).fetchone()

def query_iter(command, args=None):
	cur = get_db().cursor()
	if args:
		return cur.execute(command, args)
	return cur.execute(command)

def show_table():
	cur = get_db().cursor()
	for i in cur.execute("SELECT * FROM user"):
		print(i)
	
def get_user(id):
	if isinstance(id, int):
		column = 'id'
	elif id.find("@") > 0:
		column = 'email'
	else:
		column = 'referring_id'
	return query_one(f"SELECT * FROM user WHERE {column} = ? LIMIT 1", (id,))

def add_account(email, password, sponsor_id, db=None):
	con = get_db()
	cur = con.execute("REPLACE INTO user(email, password, sponsor_id) VALUES(?,?,?)", (email,password, sponsor_id))
	con.commit()
	return cur.lastrowid

def update_password(user_id, password, ):
	commit_db("UPDATE user SET password=? WHERE id=?", (password, user_id))

def activate_email(user_id, referring_id, address, private_key):
	commit_db("""
	    UPDATE user SET activated=1, referring_id=?,
	    address=?, private_key=? WHERE id=?""", 
	    (referring_id, address, private_key, user_id)
	)

def update_user_login(user_id, time):
	commit_db("UPDATE user SET last_login=? WHERE id=?", (time, user_id))

def confirm_password_change(user_id):
	commit_db(
		"UPDATE user SET transaction_name='change password', transaction_confirmed=1 "
		"WHERE id=?", (user_id,))

def set_confirmation(user_id, name, code, time):
	commit_db("REPLACE INTO confirmation(user_id, name, code, created) "
	          "VALUES(?, ?, ?, ?) ", (user_id, name, code, time))

def get_confirmation(user_id):
	return query_one("SELECT * FROM confirmation WHERE user_id=? LIMIT 1", (user_id,))

def increase_triers(user_id):
    commit_db("UPDATE user set error_triers=error_triers+1 WHERE id=?", (user_id,))

def reset_triers(user_id):
    commit_db("UPDATE user set error_triers=0 WHERE id=?", (user_id,))

def get_last_time_error(user_id):
    return query_one("SELECT created FROM confirmation WHERE user_id=? LIMIT 1", (user_id,))[0]