import os, logging
from socket import *
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process
from time import sleep, time
from agent_storage import *
import asyncore, pickle


class CommandHandler(asyncore.dispatcher):

    write_buffer = None

    def handle_read(self):
        log.info("Try to read command")
        data = self.recv(1024)
        if not data:
            log.warning("Empty data")
            return None

        message = _parse(data)
        if len(message) == 0:
            log.warning("Empty message")
            return None
        
        messageType = message[0]
        log.info("Message type: " + messageType)
        if messageType == "command":
            self._execute_command(message[1])
        elif messageType == "request":
            self._send_diff()

    def handle_close(self):
        log.info("Close!!!")
        self.close()

    def writable(self):
        log.info("Handler: Is writeble")
        is_writable = False
        if self.write_buffer:
            is_writable = (len(self.write_buffer) > 0)
        return is_writable
    
    def handle_write(self):
        log.info("Try write: " + str(self.write_buffer))
        sent = self.send(pickle.dumps((self.write_buffer)))
        self.write_buffer = None
        log.debug("Sent: " + str(sent))

    def _execute_command(self, command):
        log.info("_execute_comman: " + command)
        self.write_buffer = "Command '" + command + " executed"
        log.info("Last: " + str(lastFiles))
        log.info("Diff: " + str(lastFiles))
    
    def _send_diff(self):
        responce = get_full_diff() 
        update_last_requested_from_last_version()

        responce = [len(responce)] + responce
        log.warning("Try to write diff: %s" % (str(responce)))
        self.write_buffer = responce

        #log.info("_send_diff AFTER:\n" + str(mUnit))
        log.info("Write responce to write buffer")


class TbFindAgent(asyncore.dispatcher):

    handler = CommandHandler
 
    def __init__(self):
        self.thisHost = "127.0.0.1"
        self.thisPort = 8085 
        asyncore.dispatcher.__init__(self)
        self.create_socket(AF_INET, SOCK_STREAM)
        self.bind((self.thisHost, self.thisPort))
        self.listen(1)
        

    def _registerToCenter(self, centerHost, centerPort):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((centerHost, centerPort))
        sock.send(pickle.dumps([self.thisHost, self.thisPort]))
        data = sock.recv(1024)
        if not data:
            log.critical("Failed. Didn't get responce from center")
            raise Exception("Didn't get responce from center")

        responce = _parse(data)
        if len(responce) > 0:
            log.info("Responce for registration: " + responce[0])
        else:
            log.error("Registration failed")
    
    def handle_accepted(self, sock, addr):
        global mUnit
        log.info("Accepted")
        handler = self.handler(sock)

    def run(self, centerHost, centerPort):
        self._registerToCenter(centerHost, centerPort)
        asyncore.loop()

    def handle_close(self):
        log.info("Close!!!")
        self.close()
    

def _parse(data):

    message = pickle.loads(data)
    # log.info("_parse: Translate " + str(data) + " to " +  str(message))
    return message


def handler_check_dir(fur):
    try:
        fut.result()
    except Exception as e:
        print("Failed: %s: %s " % (type(e).__name__, e)) 


def check_dir(dirname):
    log.info("Check dir %s" % (dirname))
    filenames = os.listdir(dirname)
    log.debug("In the %s detected:\n%s" % (dirname, str(filenames)))
    
    for filename in filenames:
        log.debug("Check file %s" % (filename))

        filepath = dirname + "/" + filename
        log.debug("Read file " + filename)
        currentFileContent = ''.join(open(filepath).readlines())
        lastRequestedFileContent = get_last_version_file(dirname, filename)

        # compare files
        if lastRequestedFileContent:
            lastRequestedFileContent = lastRequestedFileContent[0][0]
        log.debug("Last requested:\n" + str(lastRequestedFileContent))
        log.debug("Current:\n" + str(currentFileContent))

        if currentFileContent != lastRequestedFileContent:
            log.info("Update file %s" % (filepath))
            update_diff_file(dirname, filename, currentFileContent)
        
        update_last_version_file(dirname, filename, currentFileContent)


def run_server():
    print("RUN SERVER!!!!!!!!\n\n\n")
    agent = TbFindAgent()
    agent.run("127.0.0.1", 8080)


def main():
    p = Process(target=run_server)
    p.start()
    
    dirnames = ["monitoring", "monitoring1", "monitoring2"]
    # dirnames = ["monitoring"]
    threadPool = ThreadPoolExecutor(5)
    create_monitoring_db()
    
    while True:
        for dirname in dirnames:
            threadPool.submit(check_dir, dirname)
        sleep(10)
    

if __name__ == "__main__":
    logging.basicConfig(datefmt='[%H:%M:%S]')
    log = logging.getLogger("AgentLogger")
    log.setLevel(logging.INFO)
    log.info("Logger created")

    counter = 0

    main()
