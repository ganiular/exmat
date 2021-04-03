DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS x3matrix;
DROP TABLE IF EXISTS x4matrix;
DROP TABLE IF EXISTS holders;
DROP TABLE IF EXISTS confirmation;
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


CREATE TABLE user(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	email TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL,
	activated INT(1) DEFAULT 0,
	referring_id TEXT,
	sponsor_id INTEGER,
	name TEXT,
	last_login TIMESTAMP,
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	error_triers INT DEFAULT 0,
	address TEXT,
	private_key TEXT,
	public_key TEXT
);

CREATE TABLE confirmation(
    user_id INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    created TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------

