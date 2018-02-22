import os
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from agent_storage import *
from logger import log
from abc import ABCMeta, abstractmethod


def configure():
    parser = argparse.ArgumentParser(description='Monitoring agent.')
    parser.add_argument('agent_interface')
    parser.add_argument('agent_port', type=int)
    parser.add_argument('center_interface')
    parser.add_argument('center_port', type=int)
    parser.add_argument('log_level')
    parser.add_argument('directories', nargs='+',
                        help='List of objects for monitoring')

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
