from db import get_db
from datetime import datetime
from utils.color import print_color

from flask import current_app

_paytypes = ()
_reansons = ()

def init_db(cur):
    with current_app.open_instance_resource('contract_schema.sql') as f:
        cur.executescript(f.read().decode("utf-8"))

def is_offline_user(user_id, cur):
    # is true if user has not login for the active periods and has receive 
    # more than 2 payments, otherwise false
    cur.execute(
        "SELECT user.last_login, COUNT(payment.payer) FROM payment "
        "JOIN user ON payment.payee=user.id "
        "WHERE user.id=? AND user.last_login < payment.time ",
        (user_id,))
    last_login, pay_count = cur.fetchone()
    t = pay_count > 2 and (datetime.today() - last_login).days > current_app.config["ACTIVE_PERIOD"] 
    print_color( f"ID {user_id}  is {'offline' if t else 'online'}")
    return t

def is_full_matrix(user_id, matrix, level, cur):
    # is true if all slots of the last account is filled

    # TODO: use full join to query both count at once
    slots = cur.execute('''
        SELECT COUNT(filler) FROM slot
        WHERE owner=? AND matrix=? AND level=?''',
        (user_id, matrix, level)).fetchone()[0]
    accounts = cur.execute(
        'SELECT COUNT(sponsor) FROM account WHERE partner=?', (user_id,)).fetchone()[0]
    if matrix == 1:
        return slots // (3 * current_app.config['MAX_REOPEN']) >= account
    elif matrix == 2:
        return slots // (6 * current_app.config['MAX_REOPEN']) >= account

def get_upgrade(user_id, matrix, level, cur):
    return cur.execute(
        'SELECT * FROM upgrade WHERE by=? AND matrix=? AND level=? LIMIT 1',
        (user_id, matrix, level)).fetchone()
def add_upgrade(user_id, beneficiary, matrix, level, cur):
    cur.execute(
        "INSERT INTO upgrade (by, beneficiary, matrix, level) "
        "VALUES (?,?,?,?)", (user_id, beneficiary, matrix, level))
def get_slot_count(user_id, matrix, level, cur):
    return cur.execute(
        'SELECT COUNT(filler) FROM slot WHERE owner=? AND matrix=? AND level=?',
        (user_id, matrix, level)).fetchone()[0]
def query_slot(owner, matrix, level, cur):
    cur.execute(
        "SELECT filler, position, paytype FROM slot WHERE owner=? AND matrix=? AND level=?",
        (owner, matrix, level))
    
def add_slot(owner, filler, matrix, level, position, paytype, cur):
    cur.execute(
        "INSERT INTO slot(owner, filler, matrix, level, position, paytype) "
        "VALUES(?,?,?,?,?,?)", (owner, filler, matrix, level, position, paytype))
def get_x3matrix(user_id, level, cur):
    return cur.execute(
        "SELECT * FROM x3matrix WHERE owner=? AND level=? LIMIT 1",
        (user_id, level)).fetchone()
def get_owner(matrix_id, cur):
    owner = cur.execute("SELECT owner FROM x4matrix WHERE id=? LIMIT 1", (matrix_id,)).fetchone()
    return owner[0] if owner else 0
def add_x3matrix(user_id, upline, upline_matrix_id, level, cur):
    cur.execute(
        "INSERT INTO x3matrix(owner, upline, level) VALUES(?,?,?)",
        (user_id, upline, level))
    cur.execute(
        "UPDATE x3matrix SET partner_count=partner_count+1 WHERE id=? LIMIT 1", 
        (upline_matrix_id,))
def remove_x3matrix(matrix_id, upline, level, cur):
    cur.execute("DELETE FROM x3matrix WHERE id=? LIMIT 1", (matrix_id,))
    cur.execute(
        "UPDATE x3matrix SET partner_count=partner_count-1 WHERE owner=? AND level=? LIMIT 1", 
        (upline, level))
def make_x3_slot_count(matrix_id, cur):
    cur.execute(
        "UPDATE x3matrix SET slot_count=slot_count+1 WHERE id=? LIMIT 1",
        (matrix_id,))
def set_x3_last_sponsor_index_and_reopen(matrix_id, value, cur):
    cur.execute(
        "UPDATE x3matrix SET last_sponsor_index=?, "
        "reopen_count=reopen_count+1, slot_count=0 "
        "WHERE id=? LIMIT 1",
        (value, matrix_id))
def set_x3_next_partner_index(matrix_id, value, cur):
    cur.execute(
        "UPDATE x3matrix SET next_partner_index=? WHERE id=? LIMIT 1",
        (value, matrix_id))
def make_x3_reopen_count(matrix_id, cur):
    cur.execute(
        "UPDATE x3matrix SET reopen_count=reopen_count+1, slot_count=0 WHERE id=? LIMIT 1",
        (matrix_id,))
def set_x3(user_id, level, account_index, last_sponsor_index, next_partner_index, partner_count, cur):
    cur.execute(
        "UPDATE x3matrix SET account_index=?, last_sponsor_index=?, next_partner_index=?, "
        "partner_count=? WHERE owner=? AND level=? LIMIT 1",
        (account_index, last_sponsor_index, next_partner_index, partner_count, user_id, level))
def get_account(user_id, index, cur):
    return cur.execute(
        'SELECT sponsor FROM account WHERE partner=? AND _index=? '
        'LIMIT 1', (user_id, index)).fetchone()
def get_sponsor_count(user_id, cur):
    return cur.execute(
        'SELECT COUNT(sponsor) FROM account WHERE partner=?', 
        (user_id,)).fetchone()[0]
def get_partner_count(sponsor_id, cur):
    return cur.execute(
        'SELECT COUNT(partner) FROM account WHERE sponsor=?', 
        (sponsor_id,)).fetchone()[0]
def query_sponsors(user_id, cur):
    return cur.execute('SELECT sponsor FROM account WHERE partner=?', (user_id,))
def get_current_sponsor(user_id, matrix, level, cur):
    slot_count = get_slot_count(user_id, matrix, level, cur)
    if matrix == 1:
        index = slot_count // (3 * current_app.config['MAX_REOPEN'])
    elif matrix == 2:
        index = slot_count // (6 * current_app.config['MAX_REOPEN'])
    sponsor_id = cur.execute(
        'SELECT sponsor FROM account WHERE partner=? AND index=? '
        'LIMIT 1', (user_id, index)).fetchone()[0]
    return cur.execute("SELECT * FROM user WHERE id=? LIMIT 1", (sponsor_id,)).fetchone()
def get_sponsor_id(user_id, index, cur):
    return cur.execute(
        'SELECT sponsor FROM account WHERE partner=? AND _index=? '
        'LIMIT 1', (user_id, index)).fetchone()[0]
def add_payment(payee, payer, matrix, level, paytype, txn_id, cur):
    cur.execute("""
        INSERT INTO payment(payee, payer, matrix, level, paytype, txn_id)
        VALUES(?,?,?,?,?,?)""",
        (payee, payer, matrix, level, paytype, txn_id))
def add_miss_payment(payee, payer, matrix, level, paytype, reason, cur):
    cur.execute("""
        INSERT INTO miss_payment(payee, payer, matrix, level, paytype, reason)
        VALUES(?,?,?,?,?,?)""",
        (payee, payer, matrix, level, paytype, reason))
def add_account(partner_id, sponsor_id, index, cur):
    cur.execute("INSERT INTO account VALUES(?,?,?)", (sponsor_id, partner_id, index))
def found_account(partner_id, sponsor_id, cur):
    return cur.execute("SELECT * FROM account WHERE sponsor=? AND partner=? LIMIT 1",
        (sponsor_id, partner_id)).fetchone() is not None
def add_partner(upline, downline, matrix, level, cur):
    return cur.execute(
        "INSERT INTO partner(upline, downline, matrix, level) "
        "VALUES(?,?,?,?)", (upline, downline, matrix, level)).lastrowid
def get_upline(downline, matrix, level, index, cur):
    return cur.execute(
        "SELECT upline FROM partner WHERE downline=?, matrix=?, level=?, _index=? LIMIT 1",
        (downline, matrix, level, index)).fetchone()
def get_downline(upline, matrix, level, index, cur):
    return cur.execute(
        "SELECT downline, COUNT(downline) FROM partner WHERE id=? AND upline=? AND matrix=? AND level=? LIMIT 1",
        (index, upline, matrix, level)).fetchone()
def get_next_downline(upline, matrix, level, index, cur):
    table = "x3matrix" if matrix == 1 else "x4matrix"
    downline = cur.execute(
        f"SELECT owner, id FROM {table} WHERE upline=? AND level=? AND id>=? LIMIT 1",
        (upline, level, index)).fetchone()
    if downline is None:
        downline = cur.execute(
            f"SELECT owner, id FROM {table} WHERE upline=? AND level=? AND id<? LIMIT 1",
            (upline, level, index)).fetchone()
    return downline or (0, 0)
def pt(flag, cur):
    global _paytypes
    if not _paytypes:
        _paytypes = cur.execute(
            "SELECT name FROM paytypes").fetchall()
    return _paytypes[flag - 1][0]
def rs(flag, cur):
    global _reansons
    if not _reansons:
        _reansons = cur.execute(
            "SELECT name FROM reasons").fetchall()
    return _reansons[flag - 1][0]




def add_x4matrix(user_id, upline, upline_matrix_id, level, cur):
    cur.execute(
        "INSERT INTO x4matrix(owner, upline, level) VALUES(?,?,?)",
        (user_id, upline, level))
    cur.execute(
        "UPDATE x4matrix SET partner_count=partner_count+1 WHERE id=? LIMIT 1", (upline_matrix_id,))
def remove_x4matrix(matrix_id, upline, level, cur):
    cur.execute("DELETE FROM x4matrix WHERE id=? LIMIT 1", (matrix_id,))
    cur.execute(
        "UPDATE x4matrix SET partner_count=partner_count-1 WHERE owner=? AND level=? LIMIT 1", 
        (upline, level))
def get_x4matrix(user_id, level, cur):
    return cur.execute(
        "SELECT * FROM x4matrix WHERE owner=? AND level=? LIMIT 1",
        (user_id, level)).fetchone()
def get_x4_downline_matrix(matrix_id, cur):
    matrix = cur.execute("SELECT * FROM x4matrix WHERE id=? LIMIT 1", (matrix_id,)).fetchone()
    if matrix['_index'] == 0:
        npi = matrix['next_partner_index2'] + 1
        downline_matrix = cur.execute(
            f"SELECT * FROM x4matrix WHERE upline=? AND level=? AND id>=? LIMIT 1",
            (matrix['owner'], matrix['level'], npi)).fetchone()
        if downline_matrix is None:
            downline_matrix = cur.execute(
                "SELECT * FROM x4matrix WHERE upline=? AND level=? AND id<? LIMIT 1",
                (matrix['owner'], matrix['level'], npi)).fetchone()
        cur.execute(
            "UPDATE x4matrix SET next_partner_index2=?, _index=1 WHERE id=? LIMIT 1", 
            (downline_matrix['id'] if downline_matrix else 0, matrix_id))
    else:
        downline_matrix = cur.execute(
            "SELECT * FROM x4matrix WHERE id=? LIMIT 1", 
            (matrix["next_partner_index2"],)).fetchone()
        cur.execute(
            "UPDATE x4matrix SET _index=? WHERE id=? LIMIT 1",
            ((matrix['_index'] + 1) % 3, matrix_id))
    return downline_matrix

def set_x4(user_id, level, account_index, last_sponsor_index, next_partner_index, 
    next_partner_index2, partner_count, index, debt, cur):
    cur.execute(
        "UPDATE x4matrix SET account_index=?, last_sponsor_index=?, next_partner_index=?, "
        "next_partner_index2=?, partner_count=?, _index=?, debt=? "
        "WHERE owner=? AND level=? LIMIT 1",
        (account_index, last_sponsor_index, next_partner_index, next_partner_index2,
        partner_count, index, debt, user_id, level))

def set_x4_next_partner_index(matrix_id, value, cur):
    cur.execute(
        "UPDATE x4matrix SET next_partner_index=? WHERE id=? LIMIT 1",
        (value, matrix_id))
def make_f_slot_count(matrix_id, cur):
    cur.execute(
        "UPDATE x4matrix SET f_slot_count=f_slot_count+1 WHERE id=? LIMIT 1",
        (matrix_id,))
def make_s_slot_count(matrix_id, cur):
    cur.execute(
        "UPDATE x4matrix SET s_slot_count=s_slot_count+1 WHERE id=? LIMIT 1",
        (matrix_id,))
def set_payindex(matrix_id, value, cur):
    cur.execute(
        "UPDATE x4matrix SET payindex=? WHERE id=? LIMIT 1", (value, matrix_id))
def set_debt(matrix_id, value, cur):
    cur.execute(
        "UPDATE x4matrix SET debt=? WHERE id=? LIMIT 1", (value, matrix_id))
def make_x4_reopen_count(matrix_id, cur):
    cur.execute(
        "UPDATE x4matrix SET reopen_count=reopen_count+1, f_slot_count=0, "
        "s_slot_count=0, payindex=1 WHERE id=? LIMIT 1",
        (matrix_id,))
def set_debt_and_reopen(matrix_id, value, cur):
    cur.execute(
        "UPDATE x4matrix SET reopen_count=reopen_count+1, f_slot_count=0, "
        "s_slot_count=0, payindex=1, debt=? WHERE id=? LIMIT 1",
        (value, matrix_id))
def set_x4_last_sponsor_index(matrix_id, value, cur):
    cur.execute("UPDATE x4matrix SET last_sponsor_index=? WHERE id=? LIMIT 1", (value, matrix_id))
def set_x4_last_sponsor_index_and_reopen(matrix_id, value, cur):
    cur.execute(
        "UPDATE x4matrix SET last_sponsor_index=?, reopen_count=reopen_count+1, "
        "f_slot_count=0, s_slot_count=0, payindex=1 WHERE id=? LIMIT 1",
        (value, matrix_id))
