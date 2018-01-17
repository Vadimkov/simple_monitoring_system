import asyncore, pickle
import logging
import time
from socket import *
from threading import Thread
from center_storage import *


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
        log.info("send last version request")
        request_message = pickle.dumps(['request'])
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
        try:
            self._send_last_version_req()
            new_files = self._recv_last_version()
        except Exception as e:
            log.error("Failed agent logger: %s: %s " % (type(e).__name__, e))
        return new_files
    

class ActiveAgents(object):
    
    def __init__(self):
        self._activeAgents = []

    def addAgent(self, agent):
        if agent not in self._activeAgents:
            self._activeAgents.append(agent)
            return True
        else:
            return False


class AgentLogger(Thread):

    def __init__(self, host, port):
        super(AgentLogger, self).__init__()
        self.host = host
        self.port = port
    
    def run(self):
        agent_logger_socket = socket(AF_INET, SOCK_STREAM)
        agent_logger_socket.bind((self.host, self.port))
        agent_logger_socket.listen(5)

        log.info("Agent logger starting up.")

        try:
            while True:
                (conn, addr) = agent_logger_socket.accept()
                log.info("Connected agent from %s" % (str(addr)))
                data = conn.recv(1024)
                
                if not data:
                    break
                
                agent = self._agentParse(data)
                if self._registerAgent(agent):
                    self._sendConfirm(conn)
                else:
                    self._sendReject(conn)
                    
                conn.close()
        except Exception as e:
            log.error("Failed agent logger: %s: %s " % (type(e).__name__, e))
        finally:
            agent_logger_socket.close()


    def _agentParse(self, agent):
        agent = pickle.loads(agent)
        address = agent[0]
        port = agent[1]
        return Agent(address, port)

    def _registerAgent(self, agent):
        if agent in active_agents:
            log.warning("Agent %s already registered" % (str(agent)))
            return False
        else:
            active_agents.append(agent)
            return True
        
    def _sendConfirm(self, sock):
        sock.send(pickle.dumps(("Ok")))
        
    def _sendReject(self, sock):
        sock.send(pickle.dumps(("Fail")))


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
    #p = Process(target=run_center)
    #p.start() 

    logger = AgentLogger("127.0.0.1", 8080)
    logger.start()
    
    run_monitoring()
    

if __name__ == "__main__":
    logging.basicConfig(datefmt='[%H:%M:%S]')
    log = logging.getLogger("CenterLogger")
    log.setLevel(logging.INFO)
    log.info("Logger created")

    main()
