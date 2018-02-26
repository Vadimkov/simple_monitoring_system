import time
import logging
import argparse
from socket import *
from threading import Thread
from center_storage import *
from protocol import *
from logger import *

active_agents = []
failed_attempts = {}  # key - agent name, value - failed attempts to connect

NUMBER_ATTEMPTS = 3


class Agent(object):
    """Object for communicate with monitoring_agent."""

    def __init__(self, address, port):
        """Address and ord of monitoring_agent."""

        self.address = address
        self.port = port

    def __eq__(self, other):
        """Compare address and port of agents."""

        if self.address == other.address and self.port == other.port:
            return True
        else:
            return False

    def __str__(self):
        agentName = self.address + ":" + str(self.port)
        return agentName

    def __repr__(self):
        agentName = self.address + ":" + str(self.port)
        return agentName

    def get_last_version(self):
        """Get last version of files from agent.

        Return List of Tuples:
        [(agent, space, file, string),
         (agent, space, file, string),
         ...]
        """

        log.info("send last version request")

        diffRequestMes = DiffRequestMes()
        sock = send_message_by_address(diffRequestMes,
                                       (self.address, self.port))
        diffResponseMes = get_message(sock)

        return diffResponseMes.get_field('DiffUpdate')


class AgentSecretary(Thread):
    """Register agent and listen client requests."""

    def __init__(self, host, port):
        """Host and port of monitoring center."""

        super(AgentSecretary, self).__init__()
        self.host = host
        self.port = port

    def run(self):
        """Start monitoring center. Listen register and client's requests."""

        agent_logger_socket = socket(AF_INET, SOCK_STREAM)
        agent_logger_socket.bind((self.host, self.port))
        agent_logger_socket.listen(5)

        log.info("Agent logger starting up.")

        while True:
            (conn, addr) = agent_logger_socket.accept()
            log.info("Connected from %s" % (str(addr)))
            mes = get_message(conn)

            self._handle_request(mes, conn)

            conn.close()
        agent_logger_socket.close()

    def _handle_request(self, req, sock):
        if req.get_type() == "RegisterRequestMes":
            self._handle_register_request(req, sock)
        elif req.get_type() == "ExpressionRequestMes":
            self._handleExpressionRequest(req, sock)
        else:
            raise UnsupportedMessageTypeException(req.get_type())

    def _handle_register_request(self, registerRequest, sock):
        """Handle register request from agent and send response.
        Confirm agent if this agent is not exists.
        Reject agent if agent already registeres.
        """

        agent = self._agent_parse(registerRequest)
        if self._register_agent(agent):
            self._send_confirm(sock)
        else:
            self._send_reject(sock)

    def _handleExpressionRequest(self, exprRequest, sock):
        """Get all units from DB, matched by exprRequest and send response."""

        expr = exprRequest.get_field('Expression')
        object_type = exprRequest.get_field('Type')

        report = get_matched_records(object_type, expr)

        try:
            expressionsLenghtMes = ExpressionsLenghtMes()
            expressionsLenghtMes.set_field('Lenght', len(report))
            send_message(expressionsLenghtMes, sock)

            for record in report:
                uMes = ExpressionUnitMes()
                uMes.set_field('Agent', record[0])
                uMes.set_field('Space', record[1])
                uMes.set_field('Object', record[2])
                uMes.set_field('String', record[3])

                send_message(uMes, sock)
        except Exception as e:
            log.error("Can't send report: %s" % (e))
        finally:
            sock.close()

    def _agent_parse(self, regRequest):
        address = regRequest.get_field('Host')
        port = regRequest.get_field('Port')
        return Agent(address, port)

    def _register_agent(self, agent):
        if agent in active_agents:
            log.warning("Agent %s already registered" % (str(agent)))
            return False
        else:
            active_agents.append(agent)
            return True

    def _send_confirm(self, sock):
        resp = RegisterResponseMes()
        resp.set_field('Status', True)
        send_message(resp, sock=sock)

    def _send_reject(self, sock):
        resp = RegisterResponseMes()
        resp.set_field('Status', False)
        send_message(resp, sock=sock)


def update_files(agent, new_files):
    """Save updated files, received from agent."""

    log.info("Try to update for files agent '%s' files:\n%s"
             % (agent, new_files))
    log.info("Type: %s" % (type(new_files)))

    agentname = str(agent)
    for new_file in new_files:
        if (len(new_file) < 3):
            log.error("Incorrect file '%s'" % (str(new_file)))
            continue

        log.info("Update file %s" % (str(new_file)))
        dirname = new_file[0]
        filename = new_file[1]
        content = new_file[2]

        update_file(agentname, dirname, filename, content)

    log.info("Files for agent '%s' has been updated." % (agent))


def run_monitoring(active_agents):
    """Every X seconds update monitoring files from agent."""

    create_monitoring_db()

    while True:
        for agent in active_agents:
            try:
                log.info("Request last files from %s" % agent)
                new_files = agent.get_last_version()
                update_files(agent, new_files)
                log.info("Finish with %s" % agent)
            except ConnectionRefusedError:
                handle_failed_connection(agent)
        time.sleep(5)


def handle_failed_connection(agent):
    """If connection to agent failed more then NUMBER_ATTEMPTS - remove it."""

    if str(agent) not in failed_attempts:
        failed_attempts[str(agent)] = 1
    else:
        failed_attempts[str(agent)] += 1

    log.warning("Failed '%s' attempts connect to '%s'"
                % (failed_attempts[str(agent)], str(agent)))

    if failed_attempts[str(agent)] >= NUMBER_ATTEMPTS:
        log.error("Remove agent '%s' from list active agents" % (str(agent)))
        active_agents.remove(agent)


def configure():
    parser = argparse.ArgumentParser(description='Monitoring center.')
    parser.add_argument('interface')
    parser.add_argument('port', type=int)
    parser.add_argument('log_level')

    args = parser.parse_args()
    args = args.__dict__

    args['log_level'] = parse_log_level(args['log_level'])

    return args


def parse_log_level(log_level_str):
    log_level = logging.INFO
    log_level_str = log_level_str.upper()

    if log_level_str == "DEBUG":
        log_level = logging.DEBUG
    elif log_level_str == "INFO":
        log_level = logging.INFO
    elif log_level_str == "WARNING":
        log_level = logging.WARNING
    elif log_level_str == "ERROR":
        log_level = logging.ERROR

    return log_level


def main():
    args = configure()
    logging.getLogger("CenterLogger")
    log.setLevel(args['log_level'])

    secretary = AgentSecretary(args['interface'], args['port'])
    secretary.start()

    run_monitoring(active_agents)


if __name__ == "__main__":
    main()
