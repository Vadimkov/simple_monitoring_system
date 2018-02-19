import logging
import os
from multiprocessing import Process
from logger import log
from monitoring_lib import BaseMonitoring, check_space
from monitoring_agent import run_agent
from time import sleep


class MonitoringDir(BaseMonitoring):

    def __init__(self, space_name):
        super(MonitoringDir, self).__init__(space_name)

    def get_objects(self):
        log.info("Check dir %s" % (self.space_name))

        file_names = os.listdir(self.space_name)
        log.debug("In the %s detected:\n%s"
                  % (self.space_name, str(file_names)))

        return file_names

    def get_object_content(self, object_name):
        log.debug("Check file %s" % (object_name))

        filepath = self.space_name + "/" + object_name
        log.debug("Read file " + object_name)
        current_file_content = ''.join(open(filepath).readlines())

        return current_file_content


def main():
    p = Process(target=run_agent)
    p.start()

    dir_names = ("monitoring", "monitoring1", "monitoring2")
    spaces = []

    for dir_name in dir_names:
        spaces.append(MonitoringDir(dir_name))

    while True:
        for space_obj in spaces:
            monitoringProc = Process(target=check_space, args=(space_obj,))
            monitoringProc.start()
        sleep(10)


if __name__ == "__main__":
    log.setLevel(logging.INFO)
    main()
