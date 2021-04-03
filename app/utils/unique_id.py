cypher = 'acen8w4h0dyrlzfb3x2k79vi61ogjmu5tsqp'
c = cypher
l = len(c)
m = l - 1
N = l **5 + l **6
p = 13
def generate_id(n):
	if n >= 0 and n < l ** 5:
		n = (n // p) + (l**5 // p * (n % p))
		i4, i5 = n // l, n % l
		i3, i4 = i4 // l, i4 % l
		i2, i3 = i3 // l, i3 % l
		i1, i2 = i2 // l, i2 % l
		
		if (n % m) % 5 == 4:
			id = c[i1]+c[i2]+c[i3]+c[i4]+c[i5]
		elif (n%m) % 5 == 1:
			id = c[i2]+c[i3]+c[i4]+c[i5]+c[i1]
		elif (n%m) % 5 == 2:
			id = c[i3]+c[i4]+c[i5]+c[i1]+c[i2]
		elif (n%m) % 5 == 0:
			id = c[i4]+c[i5]+c[i1]+c[i2]+c[i3]
		else:
			id = c[i5]+c[i1]+c[i2]+c[i3]+c[i4]
	elif n < N:
		n -= l**5
		n = (n // p) + (l**6 // p * (n % p))
		i5, i6 = n // l, n % l
		i4, i5 = i5 // l, i5 % l
		i3, i4 = i4 // l, i4 % l
		i2, i3 = i3 // l, i3 % l
		i1, i2 = i2 // l, i2 % l
		
		if (n % m) % 6 == 2:
			id = c[i1]+c[i2]+c[i3]+c[i4]+c[i5]+c[i6]
		elif (n%m) % 6 == 5:
			id = c[i2]+c[i3]+c[i4]+c[i5]+c[i6]+c[i1]
		elif (n%m) % 6 == 4:
			id = c[i3]+c[i4]+c[i5]+c[i6]+c[i1]+c[i2]
		elif (n%m) % 6 == 0:
			id = c[i4]+c[i5]+c[i6]+c[i1]+c[i2]+c[i3]
		elif (n%m) % 6 == 3:
			id = c[i5]+c[i6]+c[i1]+c[i2]+c[i3]+c[i4]
		else:
			id = c[i6]+c[i1]+c[i2]+c[i3]+c[i4]+c[i5]
	else:
		raise Exception
	return id

