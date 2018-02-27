import unittest
import monitoring_center
import center_storage
import logging
import protocol
from unittest.mock import MagicMock


class TestMonitoringFunctions(unittest.TestCase):

    def setUp(self):
        center_storage.create_empty_monitoring_db()

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

    def setUp(self):
        center_storage.create_empty_monitoring_db()

    def test_agent_parse(self):
        agent_secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)
        agent = monitoring_center.Agent("127.0.0.1", 5557)

        reg_rquest = protocol.RegisterRequestMes()
        reg_rquest['Host'] = "127.0.0.1"
        reg_rquest['Port'] = 5557

        self.assertEqual(agent_secretary._agent_parse(reg_rquest), agent)

    def test_register_agent(self):
        agent_secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)
        agent = monitoring_center.Agent("127.0.0.1", 5557)

        self.assertTrue(agent_secretary._register_agent(agent))
        self.assertTrue(center_storage.is_agent_exist(
                        agent.address, agent.port))

    def test_register_duplicated_agent(self):
        agent_secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)
        agent = monitoring_center.Agent("127.0.0.1", 5557)

        self.assertTrue(agent_secretary._register_agent(agent))
        self.assertTrue(center_storage.is_agent_exist(
                        agent.address, agent.port))

        self.assertFalse(agent_secretary._register_agent(agent))
        self.assertTrue(center_storage.is_agent_exist(
                        agent.address, agent.port))

    def test_handle_request_register_request(self):
        secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)
        secretary._handle_register_request = MagicMock()
        secretary._handle_expression_request = MagicMock()

        register_req = protocol.RegisterRequestMes()
        register_req['Host'] = '127.0.0.1'
        register_req['Port'] = 5557

        sock = None

        secretary._handle_request(register_req, sock)

        secretary._handle_register_request.assert_called()
        secretary._handle_expression_request.assert_not_called()

    def test_handle_request_expression_request(self):
        secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)
        secretary._handle_register_request = MagicMock()
        secretary._handle_expression_request = MagicMock()

        expression_req = protocol.ExpressionRequestMes()
        expression_req['Expression'] = 'Any Expression'
        expression_req['Type'] = 'Any Type'

        sock = None

        secretary._handle_request(expression_req, sock)

        secretary._handle_register_request.assert_not_called()
        secretary._handle_expression_request.assert_called()

    def test_handle_request_unsupported_request(self):
        secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)
        secretary._handle_register_request = MagicMock()
        secretary._handle_expression_request = MagicMock()

        unsupported_req = protocol.DiffRequestMes()

        sock = None

        with self.assertRaises(protocol.UnsupportedMessageTypeException):
            secretary._handle_request(unsupported_req, sock)


if __name__ == '__main__':
    unittest.main()
