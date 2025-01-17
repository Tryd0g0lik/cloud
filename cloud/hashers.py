"""
cloud_user/hashers.py
"""
# https://docs.djangoproject.com/en/4.2/topics/auth/passwords/#password-upgrading-without-requiring-a-login
from django.contrib.auth.hashers import ( md5,
    PBKDF2PasswordHasher,
    MD5PasswordHasher,
)
import bcrypt

from project.settings import MEDIA_ROOT


class PBKDF2WrappedMD5PasswordHasher(PBKDF2PasswordHasher):
    algorithm = "pbkdf2_wrapped_md5"

    def encode_md5_hash(self, md5_hash, salt, iterations=None):
        return super().encode(md5_hash, salt, iterations)

    def encode(self, secret_key, salt, iterations=None):
        _, _, md5_hash = MD5PasswordHasher().encode(secret_key, salt).split("$", 2)
        return self.encode_md5_hash(md5_hash, salt, iterations)

def hash_password(secret_key, encode='utf-8'):
    # salt generate
    salt = bcrypt.gensalt()
    # Password hash
    hashed_password = bcrypt.hashpw(secret_key.encode(encode), salt)
    
    return hashed_password
# PBKDF2$20000b'$2b$12$GIEoOMidkccZ1EJnO3oXf.uael00Q3BdOkewu3MfWBlrdTMpJG.5K'

def md5_chacker(link:str) -> str:
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
    new_link = f'{MEDIA_ROOT}{link}'.replace("/", '\\')
    with open(new_link, 'rb') as open_file:
        content = open_file.read()
        hasher.update(content)
        control_summ = hasher.hexdigest()
    return control_summ