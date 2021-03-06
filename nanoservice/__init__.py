"""Main module for nanoservice"""

import logging

from nanoservice.reqrep import Requester, Responder
from nanoservice.pubsub import Subscriber, Publisher
from nanoservice.crypto import Authenticator
from nanoservice.error import (
    NanoServiceError,
    ServiceError,
    ClientError,
    ConfigError,
    AuthenticatorInvalidSignature,
    RequestParseError,
    PublisherError,
    SubscriberError,
    EncodeError,
    DecodeError,
    AuthenticateError
)

__all__ = [
    'Requester', 'Responder', 'Subscriber', 'Publisher', 'Authenticator',
    'NanoServiceError', 'ServiceError', 'ClientError', 'ConfigError',
    'AuthenticatorInvalidSignature', 'RequestParseError',
    'PublisherError', 'SubscriberError', 'EncodeError',
    'DecodeError', 'AuthenticateError'
]

__version__ = '0.7.2-3'


######################################################################
# Emit warnings for deprecated components
######################################################################


class Service(Responder):

    def __init__(self, program, address, encoder=None, authenticator=None,
                 socket=None, bind=True):
        logging.warning('Service is deprecated; use Responder instead.')
        super(Service, self).__init__(
            address, encoder, authenticator, socket, bind)


class Client(Requester):

    def __init__(self, address, encoder=None, authenticator=None,
                 socket=None, bind=False):
        logging.warning('Client is deprecated; use Requester instead.')
        super(Client, self).__init__(
            address, encoder, authenticator, socket, bind)
