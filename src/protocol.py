import json
import struct
from socket import *
from logger import log


def get_message(conn):
    size = read_lenght(conn)
    data = read(conn, size)
    frmt = "=%ds" % size
    data = struct.unpack(frmt, data)
    data = data[0]

    data = json.loads(data)
    log.debug("data:\n" + str(data))
    mes = None

    if data['MessageType'] == 'RegisterRequestMes':
        mes = RegisterRequestMes()
        mes['Host'] = data['Host']
        mes['Port'] = data['Port']
    elif data['MessageType'] == 'RegisterResponseMes':
        mes = RegisterResponseMes()
        mes['Status'] = data['Status']
    elif data['MessageType'] == 'DiffRequestMes':
        mes = DiffRequestMes()
    elif data['MessageType'] == 'DiffResponseMes':
        mes = DiffResponseMes()
        mes['DiffUpdate'] = data['DiffUpdate']
    elif data['MessageType'] == 'ExpressionRequestMes':
        mes = ExpressionRequestMes()
        mes['Expression'] = data['Expression']
        mes['Type'] = data['Type']
    elif data['MessageType'] == 'ExpressionsLenghtMes':
        mes = ExpressionsLenghtMes()
        mes['Lenght'] = data['Lenght']
    elif data['MessageType'] == 'ExpressionUnitMes':
        mes = ExpressionUnitMes()
        mes['Agent'] = data['Agent']
        mes['Space'] = data['Space']
        mes['Object'] = data['Object']
        mes['String'] = data['String']
    elif data['MessageType'] == 'ExpressionStatusMes':
        mes = ExpressionStatusMes()
    else:
        raise UnsupportedMessageTypeException(data['MessageType'])

    log.debug("Got message:\n" + str(mes))

    return mes


def read_lenght(sock):
    data = read(sock, (4,))
    return struct.unpack('=I', data)


def read(sock, size):
    data = bytes('', 'utf-8')
    size = size[0]
    while len(data) < size:
        dataTemp = sock.recv(size - len(data))
        data += dataTemp
        if dataTemp == '':
            raise RuntimeError("socket connection broken")

    return data


def send_message_by_address(mes, addr):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(addr)
    return send_message(mes, sock)


def send_message(mes, sock):
    log.info("Sent message:\n" + str(mes))

    frmt = "=%ds" % len(bytes(mes._to_json(), 'utf-8'))
    packedMes = struct.pack(frmt, bytes(mes._to_json(), 'utf-8'))
    packedHed = struct.pack("=I", len(packedMes))

    send(packedHed, sock)
    send(packedMes, sock)
    return sock


def send(mes, sock):
    sent = 0
    log.debug("Send: %s)" % (str(mes)))
    while sent < len(mes):
        sent += sock.send(mes[sent:])


class Message:

    def __init__(self):
        self.messageBody = {}

    def __str__(self):
        return json.dumps(self.messageBody, indent=4)

    def __repr__(self):
        return json.dumps(self.messageBody, indent=4)

    def __eq__(self, other):
        if len(self) != len(other):
            return False

        for field in self.messageBody:
            if self[field] != other[field]:
                return False

        return True

    def __len__(self):
        return len(self.messageBody)

    def __getitem__(self, key):
        return self._get_field(key)

    def __setitem__(self, key, value):
        self._set_field(key, value)

    def _to_json(self):
        return json.dumps(self.messageBody)

    def _set_field(self, field, value):
        if field not in self.messageBody:
            raise UndefinedFieldException(self, field)
        if field == 'MessageType':
            raise ChangeMessageTypeException()

        self.messageBody[field] = value

    def _get_field(self, field):
        if field not in self.messageBody:
            raise UndefinedFieldException(self, field)

        return self.messageBody[field]

    def get_type(self):
        return self['MessageType']


class RegisterRequestMes(Message):

    def __init__(self):
        self.messageBody = {}
        self.messageBody['MessageType'] = 'RegisterRequestMes'
        self.messageBody['Host'] = None
        self.messageBody['Port'] = None


class RegisterResponseMes(Message):

    def __init__(self):
        self.messageBody = {}
        self.messageBody['MessageType'] = 'RegisterResponseMes'
        self.messageBody['Status'] = None


class DiffRequestMes(Message):

    def __init__(self):
        self.messageBody = {}
        self.messageBody['MessageType'] = 'DiffRequestMes'


class DiffResponseMes(Message):

    def __init__(self):
        self.messageBody = {}
        self.messageBody['MessageType'] = 'DiffResponseMes'
        self.messageBody['DiffUpdate'] = None


class ExpressionRequestMes(Message):

    def __init__(self):
        self.messageBody = {}
        self.messageBody['MessageType'] = 'ExpressionRequestMes'
        self.messageBody['Expression'] = None
        self.messageBody['Type'] = None


class ExpressionsLenghtMes(Message):

    def __init__(self):
        self.messageBody = {}
        self.messageBody['MessageType'] = 'ExpressionsLenghtMes'
        self.messageBody['Lenght'] = None


class ExpressionUnitMes(Message):

    def __init__(self):
        self.messageBody = {}
        self.messageBody['MessageType'] = 'ExpressionUnitMes'
        self.messageBody['Agent'] = None
        self.messageBody['Space'] = None
        self.messageBody['Object'] = None
        self.messageBody['String'] = None


class ExpressionStatusMes(Message):

    def __init__(self):
        self.messageBody = {}
        self.messageBody['MessageType'] = 'ExpressionStatusMes'


# Exceptions
class ProtocolException(Exception):

    def __init__(self, ExceptionMessage):
        super(ProtocolException, self).__init__(ExceptionMessage)


class ChangeMessageTypeException(ProtocolException):

    def __init__(self):
        super(ChangeMessageTypeException,
              self).__init__("You can't change message type!")


class UndefinedFieldException(ProtocolException):

    def __init__(self, message, field):
        super(UndefinedFieldException, self).__init__(
              "Field '%s' don't exist in the message '%s'"
              % (field, type(message)))


class UnsupportedMessageTypeException(ProtocolException):

    def __init__(self, messageType):
        super(UnsupportedMessageTypeException, self).__init__(
              "Message type '%s' is incorrect" % (messageType))
