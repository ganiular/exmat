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
    return pay_count > 2 and (datetime.today() - last_login).days > current_app.config["ACTIVE_PERIOD"] \

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
        "SELECT * FROM slot WHERE owner=? AND matrix=? AND level=?",
        (owner, matrix, level))
    
def add_slot(owner, filler, matrix, level, position, paytype, cur):
    cur.execute(
        "INSERT INTO slot(owner, filler, matrix, level, position, paytype) "
        "VALUES(?,?,?,?,?,?)", (owner, filler, matrix, level, position, paytype))
def get_x3matrix(user_id, level, cur):
    return cur.execute(
        "SELECT * FROM x3matrix WHERE owner=? AND level=? LIMIT 1",
        (user_id, level)).fetchone()
def add_x3matrix(user_id, upline, level, cur):
    cur.execute(
        "INSERT INTO x3matrix(owner, upline, level) VALUES(?,?,?)",
        (user_id, upline, level))
def remove_x3matrix(matrix_id, cur):
    cur.execute("DELETE FROM x3matrix WHERE id=?", (matrix_id,))
def set_x3_slot_count(user_id, level, value, cur):
    cur.execute(
        "UPDATE x3matrix SET slot_count=? WHERE owner=? AND level=? LIMIT 1",
        (value, user_id, level))
def set_x3_next_sponsor_index(user_id, level, value, cur):
    cur.execute(
        "UPDATE x3matrix SET next_sponsor_index=? WHERE owner=? AND level=? LIMIT 1",
        (value, user_id, level))
def set_x3_next_partner_index(user_id, level, value, cur):
    cur.execute(
        "UPDATE x3matrix SET next_partner_index=? WHERE owner=? AND level=? LIMIT 1",
        (value, user_id, level))
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
    if matrix == 1:
        downline = cur.execute(
            "SELECT owner, id FROM x3matrix WHERE upline=? AND level=? AND id>=? LIMIT 1",
            (upline, level, index)).fetchone()
        if downline is None:
            downline = cur.execute(
                "SELECT owner, id FROM x3matrix WHERE upline=? AND level=? AND id<? LIMIT 1",
                (upline, level, index)).fetchone()
    else:
        pass
    return downline

def remove_partner_by_upline(upline, matrix, level, index, cur):
    cur.execute(
        "DELETE FROM partner WHERE upline=?, matrix=?, level=?, _index=? LIMIT 1",
        (upline, matrix, level, index))
def remove_partner_by_downline(downline, matrix, level, index, cur):
    cur.execute(
        "DELETE FROM partner WHERE downline=? AND matrix=? AND level=? AND _index=? LIMIT 1",
        (downline, matrix, level, index))
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
    