import sqlite3

c = sqlite3.connect(':memory:')
c.execute('''
create table user(
    id integer primary key autoincrement,
    name Text,
    age INT)''')
c.execute('''
create table payment(
    payee integer,
    payer integer,
    age INT,
    foreign key (payee,payer) refferences user(id, id))''')
c.execute('''
insert into user(name Text,age INT)
    values''')
