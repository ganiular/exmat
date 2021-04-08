from random import randint

c = """9^pEdB]%Hx\\fcnOw|qDyPW'_t`<zIR2[Ss.5b=a+1mV{&76C?l4kNLrA8UY$-hFKo:Z*v0),>e#;jX!uT(~/@g"J3}QMGi"""
insert_interval = 9
remove_interval = insert_interval + 1

def encrypt(hexa):
	dc = int(hexa, 16)
	crypt = ''
	i = 0
	while dc != 0:
		if i % insert_interval == 0:
			crypt = c[randint(0, 93)] + crypt
		crypt = c[dc % 94] + crypt
		dc = dc // 94
		i += 1
	return crypt

def decrypt(cypher):
	cypher = cypher[::-1]
	dc = 0
	k = len(cypher) - 1
	j = k - (k // remove_interval + 1)
	for i in range(k, -1, -1):
		if i % remove_interval == 0:
			continue
		dc += c.index(cypher[i]) * 94 ** j
		j -= 1
	hexa = hex(dc)[2:]
	return hexa
