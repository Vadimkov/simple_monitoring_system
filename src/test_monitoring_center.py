import unittest
import monitoring_center
import center_storage
import logging
import protocol


class TestMonitoringFunctions(unittest.TestCase):

    def test_parse_log_level(self):
        self.assertEqual(monitoring_center.parse_log_level('DEBUG'),
                         logging.DEBUG)
        self.assertEqual(monitoring_center.parse_log_level('INFO'),
                         logging.INFO)
        self.assertEqual(monitoring_center.parse_log_level('WARNING'),
                         logging.WARNING)
        self.assertEqual(monitoring_center.parse_log_level('ERROR'),
                         logging.ERROR)

    def test_update_files(self):
        center_storage.create_empty_monitoring_db()

        agent = monitoring_center.Agent('127.0.0.1', 5555)

        new_files = []
        new_files.append(['space1', 'obj1', 'content1'])
        new_files.append(['space2', 'obj2', 'content2'])
        new_files.append(['space3', 'obj3', 'content3'])

        golden_files = []
        golden_files.append(('127.0.0.1:5555', 'space1', 'obj1', 'content1'))
        golden_files.append(('127.0.0.1:5555', 'space2', 'obj2', 'content2'))
        golden_files.append(('127.0.0.1:5555', 'space3', 'obj3', 'content3'))

        mcm = monitoring_center.MonitoringCenterManager()
        mcm.update_files(agent, new_files)
        files_from_db = center_storage.get_full()

        self.assertEqual(len(files_from_db), len(golden_files))

        for f in files_from_db:
            self.assertTrue(f in golden_files)

    def test_two_update_files(self):
        center_storage.create_empty_monitoring_db()

        agent = monitoring_center.Agent('127.0.0.1', 5555)

        golden_files = []
        golden_files.append(('127.0.0.1:5555', 'space1', 'obj1', 'content1'))
        golden_files.append(('127.0.0.1:5555', 'space2', 'obj2', 'content2'))
        golden_files.append(('127.0.0.1:5555', 'space3', 'obj3', 'content3'))

        new_files = []
        new_files.append(['space1', 'obj1', 'contentFake1'])
        new_files.append(['space2', 'obj2', 'contentFake2'])
        new_files.append(['space3', 'obj3', 'contentFake3'])

        mcm = monitoring_center.MonitoringCenterManager()
        mcm.update_files(agent, new_files)

        new_files = []
        new_files.append(['space1', 'obj1', 'content1'])
        new_files.append(['space2', 'obj2', 'content2'])
        new_files.append(['space3', 'obj3', 'content3'])

        mcm = monitoring_center.MonitoringCenterManager()
        mcm.update_files(agent, new_files)

        files_from_db = center_storage.get_full()

        self.assertEqual(len(files_from_db), len(golden_files))

        for f in files_from_db:
            self.assertTrue(f in golden_files)


class TestAgentSecretary(unittest.TestCase):

    def test_agent_parse(self):
        agent_secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)
        agent = monitoring_center.Agent("127.0.0.1", 5557)

        reg_rquest = protocol.RegisterRequestMes()
        reg_rquest['Host'] = "127.0.0.1"
        reg_rquest['Port'] = 5557

        self.assertEqual(agent_secretary._agent_parse(reg_rquest), agent)

    def test_register_agent(self):
        center_storage.create_empty_monitoring_db()

        agent_secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)
        agent = monitoring_center.Agent("127.0.0.1", 5557)

        self.assertTrue(agent_secretary._register_agent(agent))
        self.assertTrue(center_storage.is_agent_exist(
                        agent.address, agent.port))

    def test_register_duplicated_agent(self):
        center_storage.create_empty_monitoring_db()

        agent_secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)
        agent = monitoring_center.Agent("127.0.0.1", 5557)

        self.assertTrue(agent_secretary._register_agent(agent))
        self.assertTrue(center_storage.is_agent_exist(
                        agent.address, agent.port))

        self.assertFalse(agent_secretary._register_agent(agent))
        self.assertTrue(center_storage.is_agent_exist(
                        agent.address, agent.port))


if __name__ == '__main__':
    unittest.main()
