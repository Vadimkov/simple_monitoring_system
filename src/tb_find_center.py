import asyncore, pickle
import time
import logging
from socket import *
from threading import Thread
from center_storage import *
from protocol import *
from logger import *

active_agents = []


def parse_file_update(data):
    files = pickle.loads(data)
    return files[1:]


class Agent(object):
    
    def __init__(self, address, port):
        self.address = address
        self.port = port

    def __eq__(self, other):
        if self.address == other.address and self.port == other.port:
            return True
        else:
            return False

    def __str__(self):
        agentName = self.address + ":" + str(self.port)
        return agentName

    def _send_last_version_req(self):
        diffReqMes = DiffRequestMes()
        
        self._agent_socket = socket(AF_INET, SOCK_STREAM)
        self._agent_socket.connect((self.address, self.port))
        self._agent_socket.send(request_message)

    def _recv_last_version(self):
        log.info("Get last version")

        data = self._agent_socket.recv(4048)
        log.info("Read data")
        if not data:
            return None

        new_files = parse_file_update(data)
        if new_files:
            log.warning("New files:\n%s" % str(new_files))

        self._agent_socket.close()
        self._agent_socket = None

        return new_files

    def getLastVersion(self):
        new_files = []
#        try:
        log.info("send last version request")
        diffRequestMes = DiffRequestMes()
        diffResponseMes = get_message(send_message_by_address(diffRequestMes, (self.address, self.port)))
 #       except Exception as e:
        #log.error("Failed agent logger: %s: %s " % (type(e).__name__, e))
        return diffResponseMes.getField('DiffUpdate')
    

class ActiveAgents(object):
    
    def __init__(self):
        self._activeAgents = []

    def addAgent(self, agent):
        if agent not in self._activeAgents:
            self._activeAgents.append(agent)
            return True
        else:
            return False


class AgentSecretary(Thread):

    def __init__(self, host, port):
        super(AgentSecretary, self).__init__()
        self.host = host
        self.port = port
    
    def run(self):
        agent_logger_socket = socket(AF_INET, SOCK_STREAM)
        agent_logger_socket.bind((self.host, self.port))
        agent_logger_socket.listen(5)

        log.info("Agent logger starting up.")

        while True:
            (conn, addr) = agent_logger_socket.accept()
            log.info("Connected agent from %s" % (str(addr)))
            mes = get_message(conn)
            
            agent = self._agentParse(mes)
            if self._registerAgent(agent):
                self._sendConfirm(conn)
            else:
                self._sendReject(conn)
                
            conn.close()
        agent_logger_socket.close()


    def _agentParse(self, regRequest):
        address = regRequest.getField('Host')
        port = regRequest.getField('Port')
        return Agent(address, port)

    def _registerAgent(self, agent):
        if agent in active_agents:
            log.warning("Agent %s already registered" % (str(agent)))
            return False
        else:
            active_agents.append(agent)
            return True
        
    def _sendConfirm(self, sock):
        resp = RegisterResponseMes()
        resp.setField('Status', True)
        send_message(resp, sock=sock)
        
    def _sendReject(self, sock):
        resp = RegisterResponseMes()
        resp.setField('Status', False)
        send_message(resp, sock=sock)


def update_files(agent, new_files):
    log.info("Try to update for files agent '%s' files:\n%s" % (agent, new_files))
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


def run_center():
    server = TbFindCenter('localhost', 8080)
    server.run()


def run_monitoring():
    create_monitoring_db()

    while True:
        for agent in active_agents:
            log.info("Request last files from %s" % agent)
            new_files = agent.getLastVersion()
            update_files(agent, new_files)
            log.info("Finish with %s" % agent)
        time.sleep(5)


def main():
    secretary = AgentSecretary("127.0.0.1", 8080)
    secretary.start()
    
    run_monitoring()
    

if __name__ == "__main__":

    main()
