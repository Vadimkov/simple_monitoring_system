from logger import log
from agent_storage import *
from protocol import *
from socket import *


class MonitoringAgent():
    """Register in the center and send diff responses to center."""

    def __init__(self):
        self.this_host = "localhost"
        self.this_port = 8085

    def _register_to_center(self, centerHost, centerPort):
        """Send register request to center."""

        regRequest = RegisterRequestMes()
        regRequest.set_field('Host', self.this_host)
        regRequest.set_field('Port', self.this_port)
        sock = send_message_by_address(regRequest, (centerHost, centerPort))
        regResponse = get_message(sock)

        if regResponse.get_field('Status'):
            log.info("Registration passed")
        else:
            log.error("Registration failed")

    def run(self, center_host, center_port):
        """Run agent for center center_host:center_port."""

        self._register_to_center(center_host, center_port)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind((self.this_host, self.this_port))
        sock.listen(5)

        log.info("Agent has been started!")

        while True:
            (conn, addr) = sock.accept()
            log.info("Connection from '%s'" % (str(addr)))

            mes = get_message(conn)
            self.handle_request(mes, conn)

    def handle_request(self, mes, sock):
        if mes.get_type() == 'DiffRequestMes':
            self.handle_diff_request(sock)
        else:
            raise UnsupportedMessageTypeException(mes.get_type())

    def handle_diff_request(self, sock):
        response = get_full_diff()
        update_last_requested_from_last_version()

        log.warning("Try to write diff: %s" % (str(response)))

        diffResponseMes = DiffResponseMes()
        diffResponseMes.set_field('DiffUpdate', response)
        send_message(diffResponseMes, sock)


def run_agent():
    agent = MonitoringAgent()
    agent.run("localhost", 8080)
