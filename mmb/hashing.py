import hashlib
import random


NUMBER_OF_ITERATIONS = 100001


def get_salt(user: bytes):
    random.seed(user)
    h = hashlib.sha256()
    h.update(user)
    return h.digest() + bytes(str(random.uniform(-1024.0, 1023.0)), encoding='utf8')


def hash_password(password: bytes, user: bytes):
    salt = get_salt(user)
    return hashlib.pbkdf2_hmac('sha256', password, salt, NUMBER_OF_ITERATIONS)


if __name__ == '__main__':
    print(get_salt(b'lalalal'))
    print(hash_password(b'temppass', b'sanchopanca'))