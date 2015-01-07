import unittest

from mmb import hashing


class TestHashing(unittest.TestCase):

    def setUp(self):
        pass

    def test_salt(self):
        email = b'user@example.org'
        salt1 = hashing.get_salt(email)
        salt2 = hashing.get_salt(email)
        self.assertEqual(salt1, salt2, 'Salt function returns different salt for the same argument')

    def test_hash(self):
        email = b'user@example'
        password = b'password'
        hash1 = hashing.hash_password(password, email)
        hash2 = hashing.hash_password(password, email)
        self.assertEqual(hash1, hash2, 'Salt function returns different hash for the same arguments')
