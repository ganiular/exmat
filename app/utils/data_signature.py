from hashlib import blake2b
from hmac import compare_digest

SECRET_KEY = b'\xa1\xa0\x19\xf1c\x10S\x8dAX@\xb04\x07f\xa2'
AUTH_SIZE = 16
SMALL_SALT = b'\[-*-]'

def sign(data: bytes) -> str:
	h = blake2b(key=SECRET_KEY, digest_size=AUTH_SIZE)
	h.update(data + SMALL_SALT)
	return h.hexdigest()

def verify(data: bytes, data_sig: str) -> bool:
	real_sig = sign(data)
	return compare_digest(real_sig, data_sig)

if __name__ == '__main__':
	msg = b'hello world'
	sig = sign(msg)
	print(sig)
	print(verify(msg, sig))
