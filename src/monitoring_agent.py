from logger import log
from agent_storage import *
from protocol import *
from socket import *


class MonitoringAgent():
    """Register in the center and send diff responses to center."""

    def __init__(self, agent_host, agent_port, center_host, center_port):
        self.agent_host = agent_host
        self.agent_port = agent_port
        self.center_host = center_host
        self.center_port = center_port

    def _register_to_center(self, centerHost, centerPort):
        """Send register request to center."""

        regRequest = RegisterRequestMes()
        regRequest['Host'] = self.agent_host
        regRequest['Port'] = self.agent_port
        sock = send_message_by_address(regRequest, (centerHost, centerPort))
        regResponse = get_message(sock)

        if regResponse['Status']:
            log.info("Registration passed")
        else:
            log.error("Registration failed")

    def run(self, center_host, center_port):
        """Run agent for center center_host:center_port."""

        self._register_to_center(self.center_host, self.center_port)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind((self.agent_host, self.agent_port))
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
        diffResponseMes['DiffUpdate'] = response
        send_message(diffResponseMes, sock)


def run_agent(agent_host, agent_port, center_host, center_port):
    agent = MonitoringAgent(agent_host, agent_port,
                            center_host, center_port)
    agent.run("localhost", 8080)
