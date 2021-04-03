import re
import urllib.parse as parse
import random

def is_email(email):
	EMAIL_PATTERN = """(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
	return re.fullmatch(EMAIL_PATTERN, email) is not None

def is_text_id(text_id):
	return re.fullmatch('[a-z0-9]{4,6}', text_id) is not None

def parse_args(data):
	return "?" + parse.urlencode(data)

def make_code():
    return "".join(random.sample('01234567890123456789', 6))

if __name__ == "__main__":
	while True:
		email = input("Enter email: ")
		if email:
			print( is_email(email))
		else:
			break
