import json


class Message:
    
    messageBody = {}

    def __init__(self):
        pass

    def __str__(self):
        return self._toJson()

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


class RegisterRequestMes(Message):

    def __init__(self):
        self.messageBody['MessageType'] = 'RegisterRequestMes'
        self.messageBody['Host'] = None
        self.messageBody['Port'] = None

class Mes(Message):

    def __init__(self):
        self.messageBody['MessageType'] = ''
        self.messageBody[''] = None


class RegisterResponseMes(Message):

    def __init__(self):
        self.messageBody['MessageType'] = 'RegisterResponseMes'
        self.messageBody['Status'] = None


class DiffRequestMes(Message):

    def __init__(self):
        self.messageBody['MessageType'] = 'DiffRequestMes'


class DiffResponseMes(Message):

    def __init__(self):
        self.messageBody['MessageType'] = 'DiffResponceMes'
        self.messageBody['Update'] = None


# Exceptions
class ProtocolException(Exception):

    def __init__(self, message):
        super(ProtocolException, self).__init__(message)


class ChangeMessageTypeException(ProtocolException):

    def __init__(self):
        super(ChangeMessageTypeException, self).__init__("You can't change message type!")

class UndefinedFieldException(ProtocolException):

    def __init__(self, message, field):
        super(UndefinedFieldException, self).__init__("Field '%s' don't exist in the message '%s'" % (field, type(message)))
