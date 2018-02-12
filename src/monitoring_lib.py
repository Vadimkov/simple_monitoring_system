from concurrent.futures import ThreadPoolExecutor
from time import sleep
from agent_storage import *
from logger import log
import os


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


def run_monitoring(dirnames):
    # dirnames = ["monitoring"]
    threadPool = ThreadPoolExecutor(5)
    create_monitoring_db()

    while True:
        for dirname in dirnames:
            threadPool.submit(check_dir, dirname)
        sleep(10)
