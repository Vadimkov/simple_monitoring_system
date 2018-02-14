from concurrent.futures import ThreadPoolExecutor
from time import sleep
from agent_storage import *
from logger import log
from abc import ABCMeta, abstractmethod
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


def check_space(monitoring_space):
    monitoring_space.check_space()


class BaseMonitoring:

    def __init__(self, space_name):
        self.space_name = space_name

    @abstractmethod
    def get_objects(self):
        """Return list of objects in the space 'self.space_name'."""

        pass

    @abstractmethod
    def get_object_content(self, object_name):
        """Return content of object 'object_name'."""

        pass

    def check_object(self, object_name):
        """Compare current version of 'object_name' with last requested."""

        current_object_content = self.get_object_content(object_name)
        last_requested_content = get_last_version_object(
                                    self.space_name, object_name)

        # compare objects
        if last_requested_content:
            last_requested_content = last_requested_content[0][0]

        log.debug("Last requested:\n" + str(last_requested_content))
        log.debug("Current:\n" + str(current_object_content))

        if current_object_content != last_requested_content:
            log.info("Update object %s" % (object_name))
            update_diff_object(self.space_name,
                               object_name, current_object_content)

        update_last_version_object(self.space_name,
                                   object_name, current_object_content)

    def check_space(self):
        """Check every object in the space and save updates."""

        objects = self.get_objects()

        for object_name in objects:
            self.check_object(object_name)


class VirtualMethodException(Exception):
    """Called method should be overrided."""

    def __init__(self, method_name):
        super(ProtocolException, self).__init__(
              "Method \"%s\" should be overrided." % (method_name))
