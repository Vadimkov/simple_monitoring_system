import os, asyncore, pickle, logging
from protocol import *
from socket import *
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process
from time import sleep, time
from agent_storage import *
from logger import log


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
    

class CommandHandler(asyncore.dispatcher):

    write_buffer = None

    def handle_read(self):
        log.info("Try to read command")
        mes = getMessage(self)
        
        if mes.getType() == "DiffRequestMessage":
            self._send_diff()
        else:
            log.error("Unsupported message:\n%s" % (str(mes)))

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
        send_message(self.write_buffer, self)
        self.write_buffer = None
    
    def _send_diff(self):
        self.write_buffer = diffResponseMes

        #log.info("_send_diff AFTER:\n" + str(mUnit))
        log.info("Write response to write buffer")


class TbFindAgent():
 
    def __init__(self):
        self.thisHost = "127.0.0.1"
        self.thisPort = 8085 
        
    def _registerToCenter(self, centerHost, centerPort):
        regRequest = RegisterRequestMes()
        regRequest.setField('Host', self.thisHost)
        regRequest.setField('Port', self.thisPort)

        regResponse = get_message(send_message_by_address(regRequest, (centerHost, centerPort)))

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
    log.setLevel(logging.INFO)
    main()
