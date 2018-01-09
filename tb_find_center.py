import asyncore, pickle
import logging


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

class ActiveAgents(object):
    
    def __init__(self):
        self._activeAgents = []

    def addAgent(self, agent):
        if agent not in self._activeAgents:
            self._activeAgents.append(agent)
            return True
        else:
            return False


class TbFindCenter(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self._activeAgents = ActiveAgents()

    def handle_accepted(self, sock, addr):
        log.info("connected")
        
        try:
            data = sock.recv(8192)
            agent = self._agentParse(data)
            if self._activeAgents.addAgent(agent):
                log.info("New agent " + str(agent))
            else:
                log.warning("Agent " + str(agent) + " already exist")
            self._sendConfirm(sock)
        except Exception as e:
            print(e)
            self._sendReject(sock)
    
    def run(self):
        asyncore.loop()

    def _agentParse(self, agent):
        agent = pickle.loads(agent)
        address = agent[0]
        port = agent[1]
        agent = Agent(address, port)
        log.info("Address: " + address + " Port: " + str(port))
        return agent
        
    def _sendConfirm(self, sock):
        sock.send(pickle.dumps(("Ok")))
        
    def _sendReject(self, sock):
        sock.send(pickle.dumps(("Fail")))


def run_center():
    server = TbFindCenter('localhost', 8080)
    server.run()


def main():
    logging.basicConfig(datefmt='[%H:%M:%S]')
    log = logging.getLogger("CenterLogger")
    log.setLevel(logging.INFO)
    log.info("Logger created")

    p = Process(target=run_center)
    p.start() 


if __name__ == "__main__":
    main()
