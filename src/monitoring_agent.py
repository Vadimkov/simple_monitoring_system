from logger import log
from agent_storage import *
from protocol import *
from socket import *


def handleRequest(mes, sock):
    if mes.getType() == 'DiffRequestMes':
        handleDiffRequest(sock)
    else:
        raise UnsupportedMessageTypeException(mes.getType())


def handleDiffRequest(sock):
    response = get_full_diff()
    update_last_requested_from_last_version()

    log.warning("Try to write diff: %s" % (str(response)))

    diffResponseMes = DiffResponseMes()
    diffResponseMes.setField('DiffUpdate', response)
    send_message(diffResponseMes, sock)


class MonitoringAgent():

    def __init__(self):
        self.thisHost = "localhost"
        self.thisPort = 8085

    def _registerToCenter(self, centerHost, centerPort):
        regRequest = RegisterRequestMes()
        regRequest.setField('Host', self.thisHost)
        regRequest.setField('Port', self.thisPort)
        sock = send_message_by_address(regRequest, (centerHost, centerPort))
        regResponse = get_message(sock)

        if regResponse.getField('Status'):
            log.info("Registration passed")
        else:
            log.error("Registration failed")

    def run(self, centerHost, centerPort):
        self._registerToCenter(centerHost, centerPort)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind((self.thisHost, self.thisPort))
        sock.listen(5)

        log.info("Agent has been started!")

        while True:
            (conn, addr) = sock.accept()
            log.info("Connection from '%s'" % (str(addr)))

            mes = get_message(conn)
            handleRequest(mes, conn)


def run_agent():
    print("RUN AGENT!!!!!!!!\n\n\n")
    agent = MonitoringAgent()
    agent.run("localhost", 8080)
