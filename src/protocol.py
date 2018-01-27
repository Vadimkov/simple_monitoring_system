import json, pickle
from socket import *
from logger import log


def get_message(conn):
    data = json.loads(pickle.loads(conn.recv(1024)))
    log.debug("data:\n" + str(data))
    mes = None
    
    if data['MessageType'] == 'RegisterRequestMes':
        mes = RegisterRequestMes()
        mes.setField('Host', data['Host'])
        mes.setField('Port', data['Port'])
    elif data['MessageType'] == 'RegisterResponseMes':
        mes = RegisterResponseMes()
        mes.setField('Status', data['Status'])
    elif data['MessageType'] == 'DiffRequestMes':
        mes = DiffRequestMes()
    elif data['MessageType'] == 'DiffResponseMes':
        mes = DiffResponseMes()
        mes.setField('DiffUpdate', data['DiffUpdate'])
    else:
        raise UnsupportedMessageTypeException(data['MessageType']) 
    
    log.debug("Got message:\n" + str(mes))

    return mes

def send_message_by_address(mes, addr):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(addr)
    return send_message(mes, sock)

def send_message(mes, sock):
    log.info("Sent message:\n" + str(mes))
    sock.send(pickle.dumps(mes._toJson()))
    return sock


class Message:
    
    def __init__(self):
        self.messageBody = {}

    def __str__(self):
        return json.dumps(self.messageBody, indent=4)

    def _toJson(self):
        return json.dumps(self.messageBody)

    def setField(self, field, value):
        if field not in self.messageBody:
            raise UndefinedFieldException(self, field)
        if field == 'MessageType':
            raise ChangeMessageTypeException()

        self.messageBody[field] = value

    def getField(self, field):
        if field not in self.messageBody:
            raise UndefinedFieldException(self, field)

        return self.messageBody[field]

    def getType(self):
        return self.getField('MessageType')


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


# Exceptions
class ProtocolException(Exception):

    def __init__(self, ExceptionMessage):
        super(ProtocolException, self).__init__(ExceptionMessage)


class ChangeMessageTypeException(ProtocolException):

    def __init__(self):
        super(ChangeMessageTypeException, self).__init__("You can't change message type!")


class UndefinedFieldException(ProtocolException):

    def __init__(self, message, field):
        super(UndefinedFieldException, self).__init__("Field '%s' don't exist in the message '%s'" % (field, type(message)))


class UnsupportedMessageTypeException(ProtocolException):

    def __init__(self, messageType):
        super(UnsupportedMessageTypeException, self).__init__("Message type '%s' is incorrect" % (messageType))
