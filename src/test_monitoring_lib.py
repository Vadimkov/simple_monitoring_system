import unittest
import agent_storage
from monitoring_lib import BaseMonitoring
from unittest.mock import MagicMock


class FakeBaseMonitoring(BaseMonitoring):

    def __init__(self, space_name):
        self.suffix = ""
        super(FakeBaseMonitoring, self).__init__(space_name)

    def get_objects(self):
        pass

    def get_object_content(self, object_name):
        return "Content of %s%s" % (object_name, self.suffix)


class TestBaseMonitoring(unittest.TestCase):

    def setUp(self):
        self.monitoring_agent = FakeBaseMonitoring('space1')

        objects = ['object1', 'object2', 'object3']
        self.monitoring_agent.get_objects = MagicMock(return_value=objects)

        self.golden_objects = [('space1', 'object1', 'Content of object1'),
                               ('space1', 'object2', 'Content of object2'),
                               ('space1', 'object3', 'Content of object3')]

        agent_storage.create_empty_monitoring_db()
        self.monitoring_agent.check_space()

    def test_check_space(self):
        db_objects = agent_storage.get_full_last_version()
        self.assertTrue(self.golden_objects == db_objects)

    def test_check_space_update_objects(self):
        self.monitoring_agent.suffix = " mdf"
        self.monitoring_agent.check_space()

        golden_objects = [('space1', 'object1', 'Content of object1 mdf'),
                          ('space1', 'object2', 'Content of object2 mdf'),
                          ('space1', 'object3', 'Content of object3 mdf')]

        db_objects = agent_storage.get_full_last_version()
        self.assertTrue(golden_objects == db_objects)


if __name__ == "__main__":
    unittest.main()
