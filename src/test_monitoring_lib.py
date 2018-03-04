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

        for obj in self.golden_objects:
            agent_storage.update_last_requested_object(obj[0], obj[1], obj[2])

    def test_check_space(self):
        """Test write objects to DB:
        1. Execute check_space for fake objects;
        2. Verify, that objects saved is correct."""

        db_objects = agent_storage.get_full_last_version()
        self.assertTrue(self.golden_objects == db_objects)

    def test_check_space_update_objects(self):
        """Test update already exists objects:
        1. Execute check_space for fake objects;
        2. Change objects and execute check_space again;
        3. Verify that objects updated correct."""

        self.monitoring_agent.suffix = " mdf"
        self.monitoring_agent.check_space()

        golden_objects = [('space1', 'object1', 'Content of object1 mdf'),
                          ('space1', 'object2', 'Content of object2 mdf'),
                          ('space1', 'object3', 'Content of object3 mdf')]

        db_objects = agent_storage.get_full_last_version()
        self.assertTrue(golden_objects == db_objects)

    def test_update_diff(self):
        """Test how check_space update diff:
        1. Execute check_space for fake objects;
        2. Fill 'last_requested' table;
        3. Change objects and execute check_space again;
        4. Execute check_space again;
        5. Verify that all updated objects has been wrote to 'diff' table."""

        self.monitoring_agent.suffix = " mdf"
        self.monitoring_agent.check_space()

        golden_objects = [('space1', 'object1', 'Content of object1 mdf'),
                          ('space1', 'object2', 'Content of object2 mdf'),
                          ('space1', 'object3', 'Content of object3 mdf')]

        db_objects = agent_storage.get_full_diff()
        self.assertTrue(golden_objects == db_objects)

    def test_remove_object(self):
        """Test remove one object:
        1. Execute check_space for fake objects;
        2. Fill 'last_requested' table;
        3. Remove object3 and create object4;
        4. Check that we sent empty content for object3."""
        objects = ['object1', 'object2', 'object4']
        self.monitoring_agent.get_objects = MagicMock(return_value=objects)

        self.monitoring_agent.suffix = " mdf"
        self.monitoring_agent.check_space()

        golden_objects = [('space1', 'object1', 'Content of object1 mdf'),
                          ('space1', 'object2', 'Content of object2 mdf'),
                          ('space1', 'object3', ''),
                          ('space1', 'object4', 'Content of object4 mdf')]

        db_objects = agent_storage.get_full_diff()
        self.assertTrue(golden_objects == db_objects)


if __name__ == "__main__":
    unittest.main()
