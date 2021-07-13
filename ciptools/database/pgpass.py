"""
Generate the password hashes/verifiers for use in PostgreSQL.

How to use this:

    pw = EncryptPassword(
        user="username",
        password="securepassword",
        algorithm="scram-sha-256",
    )
    print(pw.encrypt())

The output of the "encrypt" function can be stored directly into the catalog
as the user's password. This code was shamelessly stolen from Jonathan Katz:

    https://gist.github.com/jkatz/e0a1f52f66fa03b732945f6eb94d9c21

"""

import base64
import hashlib
import hmac
import secrets
import stringprep
import unicodedata


class PasswordHasher:
    ALGORITHMS = {
        "scram-sha-256": {
            "encryptor": "encrypt_scram_sha_256",
            "digest": hashlib.sha256,
            "defaults": {
                "salt_length": 16,
                "iterations": 4096,
            },
        }
    }

    # list of characters that are prohibited to be used per postgres-SASLprep
    SASLPREP_STEP3 = (
        stringprep.in_table_a1,  # postgres treats this as prohibited
        stringprep.in_table_c12,
        stringprep.in_table_c21_c22,
        stringprep.in_table_c3,
        stringprep.in_table_c4,
        stringprep.in_table_c5,
        stringprep.in_table_c6,
        stringprep.in_table_c7,
        stringprep.in_table_c8,
        stringprep.in_table_c9,
    )

    def __init__(self, user, password, algorithm="scram-sha-256"):
        self.user = user
        self.password = password
        self.algorithm = algorithm
        self.salt = None
        self.encrypted_password = None

    def encrypt(self):
        try:
            algorithm = self.ALGORITHMS[self.algorithm]
        except KeyError:
            raise Exception("algorithm '{}' not supported".format(self.algorithm))

        kwargs = algorithm["defaults"].copy()
        return getattr(self, algorithm["encryptor"])(algorithm["digest"], **kwargs)

    def encrypt_scram_sha_256(self, digest, **kwargs):
        iterations = kwargs["iterations"]
        salt_length = kwargs["salt_length"]
        salted_password = self._scram_sha_256_generate_salted_password(self.password, salt_length, iterations, digest)
        client_key = hmac.HMAC(salted_password, b"Client Key", digest)
        stored_key = digest(client_key.digest()).digest()
        server_key = hmac.HMAC(salted_password, b"Server Key", digest)
        self.encrypted_password = self.algorithm.upper().encode("utf-8") + b"$" + ("{}".format(iterations)).encode("utf-8") + b":" + base64.b64encode(self.salt) + b"$" + base64.b64encode(stored_key) + b":" + base64.b64encode(server_key.digest())
        return self.encrypted_password

    def _scram_sha_256_generate_salted_password(self, password, salt_length, iterations, digest):
        """This follows the "Hi" algorithm specified in RFC5802"""

        # need to normalize the password using postgres-flavored SASLprep
        normalized_password = self._normalize_password(password)

        # convert the password to a binary string. UTF8 is safe for SASL.
        p = normalized_password.encode("utf8")

        # generate a salt
        self.salt = secrets.token_bytes(salt_length)

        # the initial signature is the salt with a terminator of a 32-bit
        # string ending in 1
        ui = hmac.new(p, self.salt + b"\x00\x00\x00\x01", digest)

        # grab the initial digest
        u = ui.digest()

        # for X number of iterations, recompute the HMAC signature against the
        # password and the latest iteration of the hash, and XOR it with the
        # previous version
        for _ in range(iterations - 1):
            ui = hmac.new(p, ui.digest(), hashlib.sha256)
            # this is a fancy way of XORing two byte strings together
            u = self._bytes_xor(u, ui.digest())
        return u

    def _normalize_password(self, password):
        """Normalize the password using PostgreSQL-flavored SASLprep.

        For reference, using the pg_saslprep function:

            https://git.postgresql.org/gitweb/?p=postgresql.git;a=blob;f=src/common/saslprep.c

        Implementation borrowed from asyncpg implementation:

            https://github.com/MagicStack/asyncpg/blob/master/asyncpg/protocol/scram.pyx#L263
        """
        normalized_password = password

        # if the password is an ASCII string or fails to encode as an UTF8
        # string, we can return.
        try:
            normalized_password.encode("ascii")
        except UnicodeEncodeError:
            pass
        else:
            return normalized_password

        # step 1 of SASLPrep: Map. per the algorithm, we map non-ascii space
        # characters to ASCII spaces (\x20 or \u0020, but we will use ' ') and
        # commonly mapped to nothing characters are removed.
        # Table C.1.2 -- non-ASCII spaces
        # Table B.1 -- "Commonly mapped to nothing"
        normalized_password = u"".join(
            [' ' if stringprep.in_table_c12(c) else c
             for c in normalized_password if not stringprep.in_table_b1(c)])

        # if at this point the password is empty, postgres uses the original
        # password.
        if not normalized_password:
            return password

        # step 2 of SASLPrep: normalize the password using the unicode
        # normalization algorithm to NFKC form.
        normalized_password = unicodedata.normalize("NFKC", normalized_password)

        # if the password is not empty, postgres uses the original password.
        if not normalized_password:
            return password

        # step 3 of SASLPrep: if postgres detects any of the prohibited
        # characters in SASLPrep, it will use the original password. we also
        # include "unassigned code points" in the prohibited character category
        # as postgres does the same.
        for c in normalized_password:
            if any(in_prohibited_table(c) for in_prohibited_table in self.SASLPREP_STEP3):
                return password

        # step 4 of SASLPrep: postgres follows the rules for bi-directional
        # characters laid on in RFC3454 Sec. 6 which are:
        #   1. characters in RFC 3454 Sec 5.8 are prohibited (C.8).
        #   2. if a string contains a RandALCat character, it cannot contain
        #      any LCat character.
        #   3. if the string contains any RandALCat character, an RandALCat
        #      character must be the first and last character of the string.
        # RandALCat characters are found in table D.1, whereas LCat are in D.2
        if any(stringprep.in_table_d1(c) for c in normalized_password):
            # if the first character or the last character are not in D.1,
            # return the original password
            if not (stringprep.in_table_d1(normalized_password[0]) and stringprep.in_table_d1(normalized_password[-1])):
                return password

            # if any characters are in D.2, use the original password
            if any(stringprep.in_table_d2(c) for c in normalized_password):
                return password

        # return the normalized password
        return normalized_password

    @staticmethod
    def _bytes_xor(a, b):
        """XOR two bytestrings together"""
        return bytes(a_i ^ b_i for a_i, b_i in zip(a, b))
