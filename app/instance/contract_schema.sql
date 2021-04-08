DROP TABLE IF EXISTS x3matrix;
DROP TABLE IF EXISTS x4matrix;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS partner;
DROP TABLE IF EXISTS miss_payment;
DROP TABLE IF EXISTS paytypes;
DROP TABLE IF EXISTS reasons;
DROP TABLE IF EXISTS slot;
DROP TABLE IF EXISTS upgrade;
DROP TABLE IF EXISTS downline;
DROP TABLE IF EXISTS upline;

-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------

CREATE TABLE x3matrix(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
	owner INTEGER,
	upline INTEGER NOT NULL,
	-- partner_id INTEGER,
	level INT,
    slot_count INT DEFAULT 0,
    reopen_count INTEGER DEFAULT 0,
    partner_count INTEGER DEFAULT 0,
    last_sponsor_index INT DEFAULT -1,
    next_partner_index INTEGER DEFAULT 0,
    account_index INT DEFAULT 0,
    FOREIGN KEY (owner, upline) REFERENCES user(id, id),
    FOREIGN KEY (last_sponsor_index, account_index) REFERENCES account(_index, _index),
    FOREIGN KEY (next_partner_index) REFERENCES x3matrix(id)
    -- FOREIGN KEY (partner_id) REFERENCES partner(id)
);

CREATE TABLE x4matrix(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner INTEGER NOT NULL,
    upline INTEGER NOT NULL,
    level INT,
    f_slot_count INT DEFAULT 0,
    s_slot_count INT DEFAULT 0,
    reopen_count INTEGER DEFAULT 0,
    partner_count INTEGER DEFAULT 0,
    last_sponsor_index INT DEFAULT -1,
    next_partner_index INTEGER DEFAULT 0,
    next_partner_index2 INTEGER DEFAULT 0,
    _index INT DEFAULT 0,
    account_index INT DEFAULT 0,
    payindex INT DEFAULT 1,
    debt INT DEFAULT 0,
    FOREIGN KEY (owner, upline) REFERENCES user(id, id),
    FOREIGN KEY (last_sponsor_index, account_index) REFERENCES account(_index, _index),
    FOREIGN KEY (next_partner_index, next_partner_index2) REFERENCES x4matrix(id, id)
);

CREATE TABLE account(
	sponsor INTEGER NOT NULL,
	partner INTEGER NOT NULL,
	_index INTEGER NOT NULL,
	PRIMARY KEY (sponsor, partner),
	FOREIGN KEY (sponsor, partner) REFERENCES user(id, id)
);

CREATE TABLE payment(
    payee INTEGER NOT NULL,
    payer INTEGER NOT NULL,
    matrix INT,
    level INT,
    paytype INT,
    txn_id TEXT NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payee, payer) REFERENCES user(id, id),
    FOREIGN KEY (paytype) REFERENCES paytypes(id)
);

CREATE TABLE miss_payment(
    payee INTEGER NOT NULL,
    payer INTEGER NOT NULL,
    matrix INT,
    level INT,
    paytype INT,
    reason INT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payee, payer) REFERENCES user(id, id),
    FOREIGN KEY (paytype) REFERENCES paytypes(id),
    FOREIGN KEY (reason) REFERENCES reasons(id)
);

CREATE TABLE paytypes(
    flag INT NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE reasons(
    flag INT NOT NULL,
    name TEXT NOT NULL
);

INSERT INTO paytypes VALUES
(1, 'direct'), (2, 'overtaken'), (3, 'reopen'),
(4, 'thanksgiven'), (5, 'direct from downline'),
(6, 'direct from upline'), (7, 'from upline'),
(8, 'from downline'), (9, 'forward'), (10, 'reflect');

INSERT INTO reasons VALUES
(1, 'not activated'), (2, 'offline'),
(3, 'account full'), (4, 'maximum debt attained');

CREATE TABLE slot(
    owner INTEGER NOT NULL,
    filler INTEGER NOT NULL,
    matrix INT,
    level INT,
    position INT,
    paytype INT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paytype) REFERENCES paytypes(id)
);

CREATE TABLE upgrade(
    by INTEGER NOT NULL,
    beneficiary INTEGER NOT NULL,
    matrix INT,
    level INT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (by, beneficiary) REFERENCES user(id, id)
);
/*
CREATE TABLE partner(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- owner INTEGER NOT NULL, REFERENCES
    upline INTEGER NOT NULL,
    downline INTEGER NOT NULL,
    matrix INT,
    level INT,
    FOREIGN KEY (upline, downline) REFERENCES user(id, id)
);
*/
CREATE TABLE downline(
    owner INTEGER NOT NULL,
    partner INTEGER NOT NULL,
    matrix INT,
    level INT,
    _index INTEGER NOT NULL,
    FOREIGN KEY (owner, partner) REFERENCES user(id, id)
);

CREATE TABLE upline(
    owner INTEGER NOT NULL,
    partner INTEGER NOT NULL,
    matrix INT,
    level INT,
    _index INTEGER NOT NULL,
    FOREIGN KEY (owner, partner) REFERENCES user(id, id)
);