'''
The MIT License (MIT)

Copyright (c) 2016 Tony Walker

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

import uuid
import nanomsg
import logging

from .error import DecodeError
from .error import RequestParseError
from .error import AuthenticateError
from .error import AuthenticatorInvalidSignature
from .encoder import MsgPackEncoder

from .core import Endpoint
from .core import Process
import threading

try:
    import queue
except ImportError:
    import Queue as queue

lock = threading.Lock()


class RequestCtx(dict):
    """ A dot access dictionary for Request """

    def __init__(self, *args, **kwargs):
        super(RequestCtx, self).__init__(self, *args, **kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        lock.acquire()
        self[key] = value
        lock.release()


class Responder(Endpoint, Process):
    """ A service which responds to requests """

    # pylint: disable=too-many-arguments
    # pylint: disable=no-member
    def __init__(self, address, encoder=None, authenticator=None,
                 socket=None, bind=True, timeouts=(None, None)):

        # Defaults
        socket = socket or nanomsg.Socket(nanomsg.REP)
        encoder = encoder or MsgPackEncoder()

        super(Responder, self).__init__(
            socket, address, bind, encoder, authenticator, timeouts)

        self.methods = {}
        self.descriptions = {}

    def get_cli_session(self, session_uuid, auth_token):
        """ Overide this method to provide session """
        raise Exception('Implement this method in your subclass')

    def execute(self, ctx, method, args):
        """ Execute the method with args """

        result = error = None
        fun = self.methods.get(method)
        if not fun:
            error = 'Method `{}` not found'.format(method)
        else:
            try:
                result = fun(*args)
            except Exception as exception:
                logging.error(
                    'Request {} exception {}'.format(ctx.ref, exception), exc_info=1)
                error = str(exception)
        response = dict(ref=ctx.ref)
        if error:
           response['error'] = error
        elif result:
           response['result'] = result
        if ctx.get('queued'):
            response['queued'] = True
        if ctx.get('content_type'):
            response['content_type'] = ctx.content_type
        return response

    def register(self, name, fun, description=None):
        """ Register function on this service """
        self.methods[name] = fun
        self.descriptions[name] = description

    @classmethod
    def parse(cls, payload):
        """ Parse client request """
        try:
            session = payload['ses']
            auth_token = payload['tok']
            method = payload['met']
            args = payload['arg']
            ref = payload['ref']
            version = payload['ver']
        except Exception as exception:
            raise RequestParseError(exception)
        else:
            return session, auth_token, method, args, ref, version

    # pylint: disable=logging-format-interpolation
    def process(self):
        """ Receive data from socket and process request """

        responses = None
        error_ref = ''
        error_msg = ''

        try:
            payload = self.receive()
            responses = []
            unique_sessions = {}
            for request in payload:
                try:
                    ref = None
                    session_uuid, auth_token, method, args, ref, version = self.parse(
                        request)
                    ctx = RequestCtx(
                        session=None,
                        session_uuid=session_uuid,
                        auth_token=auth_token,
                        ref=ref,
                        version=version
                    )
                    if session_uuid in unique_sessions:
                        ctx.session = unique_sessions[session_uuid]
                    elif session_uuid and auth_token:
                        ctx.session = self.get_cli_session(
                            ctx, session_uuid, auth_token)
                        unique_sessions[session_uuid] = ctx.session
                    else:
                        ctx.session = None
                    responses.append(self.execute(
                        ctx=ctx,
                        method=method,
                        args=args
                    ))
                except RequestParseError as exception:
                    error_ref = ref or str(uuid.uuid4())
                    logging.error(
                        'Service error while parsing request: {} {}'
                        .format(error_ref, exception), exc_info=1)
                    responses.append(dict(error=str(exception)))

                except AuthenticateError as exception:
                    error_ref = ref or str(uuid.uuid4())
                    logging.error(
                        'Service error while authenticating request: {} {}'
                        .format(error_ref, exception), exc_info=1)
                    responses.append(dict(ref=ref, error=str(exception)))

                except Exception as exception:
                    error_ref = ref or str(uuid.uuid4())
                    logging.error(
                        'Service error while excuting request: {} {}'
                        .format(error_ref, exception), exc_info=1)
                    responses.append(dict(ref=ref, error=str(exception)))

            for session in unique_sessions.values():
                i = 0
                try:
                    while i < 10:
                        qctx = session.queue.get_nowait()
                        response = dict(ref=qctx.ref)
                        try:
                            response['error'] = qctx.error
                        except AttributeError:
                            response['result'] = qctx.result
                        except AttributeError:
                            pass
                        if qctx.get('content_type'):
                            response['content_type'] = ctx.content_type
                        responses.append(response)
                        i += 1
                except queue.Empty:
                    continue
                except Exception as exception:
                    error_ref = ref or str(uuid.uuid4())
                    logging.error(
                        'Service error while excuting request: {} {}'
                        .format(error_ref, exception), exc_info=1)
                    responses.append(dict(ref=ref, error=str(exception)))
                    continue

        except AuthenticateError as exception:
            error_ref = str(uuid.uuid4())
            error_msg = 'Service error while authenticating request: {} {}'
            logging.error(
                error_msg.format(error_ref, exception), exc_info=1)

        except AuthenticatorInvalidSignature as exception:
            error_ref = str(uuid.uuid4())
            error_msg = 'Service error while authenticating request: {} {}'
            logging.error(
                error_msg.format(error_ref, exception), exc_info=1)

        except DecodeError as exception:
            error_ref = str(uuid.uuid4())
            error_msg = 'Service error while decoding request: {} {}'
            logging.error(
                error_msg.format(error_msg, exception), exc_info=1)

        except RequestParseError as exception:
            error_ref = str(uuid.uuid4())
            error_msg = 'Service error while parsing request: {} {}'
            logging.error(
                error_msg.format(error_msg, exception), exc_info=1)

        else:
            logging.debug('Service received payload: {}'.format(payload))

        if responses:
            self.send(responses)
        else:
            self.send([dict(error=error_msg)])


class Requester(Endpoint):
    """ A requester client """

    # pylint: disable=too-many-arguments
    # pylint: disable=no-member
    def __init__(self, address, encoder=None, authenticator=None,
                 socket=None, bind=False, timeouts=(None, None),
                 session_uuid=None, auth_token=None):
        self.session_uuid = session_uuid
        self.auth_token = auth_token
        # Defaults
        socket = socket or nanomsg.Socket(nanomsg.REQ)
        encoder = encoder or MsgPackEncoder()

        super(Requester, self).__init__(
            socket, address, bind, encoder, authenticator, timeouts)

    @classmethod
    def build_payload(cls, session_uuid, auth_token, method, args):
        """ Build the payload to be sent to a `Responder` """
        ref = str(uuid.uuid4())
        return ([(
            dict(
                ses=session_uuid,
                tok=auth_token,
                ver=1,
                met=method,
                arg=args,
                ref=ref
            )
        )])

    # pylint: disable=logging-format-interpolation
    def call(self, method, *args):
        """ Make a call to a `Responder` and return the result """

        payload = self.build_payload(
            self.session_uuid, self.auth_token, method, args
        )
        logging.debug('* Client will send payload: {}'.format(payload))
        self.send(payload)

        responses = self.receive()
        # logging.debug('Responses: {}'.format(responses))
        assert payload[0]['ref'] == responses[0]['ref']
        return responses
