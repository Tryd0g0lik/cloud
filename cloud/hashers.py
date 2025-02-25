"""
cloud_user/hashers.py
"""

import bcrypt
# https://docs.djangoproject.com/en/4.2/topics/auth/passwords/#password-upgrading-without-requiring-a-login
from django.contrib.auth.hashers import (MD5PasswordHasher,
                                         PBKDF2PasswordHasher, md5)

from project.settings import MEDIA_ROOT


class PBKDF2WrappedMD5PasswordHasher(PBKDF2PasswordHasher):
    """
    Class for a hashing password with PBKDF2 and MD5.
    """

    algorithm = "pbkdf2_wrapped_md5"

    def encode_md5_hash(self, md5_hash, salt, iterations=None):
        """
        Method for the encoding MD5 hash.
        :param md5_hash: The value hash received from the MD5 algorithm
        :param salt: The handom valued for the serv hash. It's secret key.
        :param iterations: This a operation's quantity for the hashing process.
        :return: THe encoded value/
        """
        return super().encode(md5_hash, salt, iterations)

    def encode(self, secret_key, salt, iterations=None):
        """
        Method for the encoding.
        :param secret_key: The message wich will be hashing. It is simple\
a password text of user.
        :param salt: The handom valued for the serv hash. It's secret key.
        :param iterations: This a operation's quantity for the hashing process.
        :return:
        """
        _, _, md5_hash = MD5PasswordHasher().encode(secret_key, salt).split("$", 2)
        return self.encode_md5_hash(md5_hash, salt, iterations)


def hashpw_password(secret_key, encode="utf-8"):
    """
    This the function for hashing password.
    :param secret_key: The message wich will be hashing. It is simple '\
a password text of user.
    :param encode:
    :return:
    """
    # salt generate
    salt = bcrypt.gensalt()
    # Password hash
    hashed_password = bcrypt.hashpw(secret_key.encode(encode), salt)

    return hashed_password


def md5_chacker(link: str) -> str:
    """
	 TODO:This function is the double file's checker\
     First - do the hashing a file from db and new file.\
     'md5' will be hashing both files.\
     After - check to the equality of files. If hash from files is equal, \
    means they (files) is equally.
	 :link: Relative link to the file
	 :return: str It is a hash of a single file.
    """
    hasher = md5()
    new_link = f"{MEDIA_ROOT}{link}".replace("/", "\\")
    with open(new_link, "rb") as open_file:
        content = open_file.read()
        hasher.update(content)
        control_summ = hasher.hexdigest()
    return control_summ
