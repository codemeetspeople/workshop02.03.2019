import time
import jwt
import hashlib
import uvloop
import asyncio
from sqlalchemy.util import classproperty

from config import settings


_EVENT_LOOP = None


def get_event_loop():
    """Override asyncio.loop policy with uvloop.EventLoopPolicy.

    :return: asyncio.loop

    """
    global _EVENT_LOOP
    if not _EVENT_LOOP:
        current_policy = asyncio.get_event_loop_policy()
        if not isinstance(current_policy, uvloop.EventLoopPolicy):
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        _EVENT_LOOP = asyncio.get_event_loop()

    return _EVENT_LOOP


def get_password(password):
    """Hash user password for secure storing in database. SHA-512 algorithm used.

    :param password: Non encrypted user password
    :type password: str
    :return: Encrypted user password
    :rtype: str

    """
    password_hash = hashlib.sha512()
    password_hash.update(f'{settings.salt}{password}{settings.salt}'.encode('utf-8'))

    return password_hash.hexdigest()


def generate_token(user_id):
    """Generate authorization token. JWT encryption used.

    :param user_id: User identifier
    :type user_id: int
    :return: Encrypted authorization token
    :rtype: str

    """
    return jwt.encode(
        {'user_id': user_id, 'created_at': int(time.time())},
        settings.salt,
        algorithm='HS256'
    ).decode('utf-8')


def encode_token(token):
    """Encode authorization token. JWT decryption used.

    :param token: Authorization token
    :type token:
    :return: Decrypted authorization token
    :rtype: dict

    """
    return jwt.encode(token, settings.salt, algorithms=['HS256'])



class Constants:
    """Class with property which returns all class attributes."""

    @classproperty
    def ALL(self):
        """Collect all settings in list."""
        return [getattr(self, i) for i in self.__dict__.keys() if i[:1] != '_' and not callable(getattr(self, i))]
