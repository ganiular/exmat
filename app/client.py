import http.client as client


def test():
	conn = client.HTTPConnection("localhost", 5000)
	conn.request('GET', '/')
	res = conn.getresponse()
	conn.close()
	print(res.read())

while True:
	opt = input("Enter: ")
	if opt:
		test()
	else:
		break
