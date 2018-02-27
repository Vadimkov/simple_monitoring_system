import unittest
import monitoring_center
import center_storage
import logging
import protocol
from unittest.mock import MagicMock
from unittest.mock import call
from socket import *


class TestMonitoringCenterManager(unittest.TestCase):
    """Unit tests for MonitoringCenterManager."""

    def setUp(self):
        center_storage.create_empty_monitoring_db()

    def test_parse_log_level(self):
        """Check parsing string to log level."""

        self.assertEqual(monitoring_center.parse_log_level('DEBUG'),
                         logging.DEBUG)
        self.assertEqual(monitoring_center.parse_log_level('INFO'),
                         logging.INFO)
        self.assertEqual(monitoring_center.parse_log_level('WARNING'),
                         logging.WARNING)
        self.assertEqual(monitoring_center.parse_log_level('ERROR'),
                         logging.ERROR)

    def test_update_files(self):
        """Check update_files () method for create new objects in monitoring DB:
        1. Create list of objects;
        2. Save these objects in the DB;
        3. Compare these objects with golden list."""

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
        """Check update_files () method for update objects in monitoring DB:
        1. Create list of objects;
        2. Save these objects in the DB;
        3. Update objects in the DB;
        4. Compare these objects with golden list."""

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
    """Unit tests for AgentSecretary class."""

    def setUp(self):
        center_storage.create_empty_monitoring_db()

        self.new_files = []
        self.new_files.append(['space1', 'obj1', '123456'])
        self.new_files.append(['space2', 'obj2', '123456789'])
        self.new_files.append(['space3', 'obj3', '7890'])

        self.agent = monitoring_center.Agent('127.0.0.1', 5557)
        mcm = monitoring_center.MonitoringCenterManager()
        mcm.update_files(self.agent, self.new_files)

    def test_agent_parse(self):
        """Check _agent_parse(req) method:
        1. Create RegisterRequest();
        2. Execute _agent_parse(req) for this request;
        3. Compare with golden Agent object."""

        agent_secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)

        reg_rquest = protocol.RegisterRequestMes()
        reg_rquest['Host'] = "127.0.0.1"
        reg_rquest['Port'] = 5557

        self.assertEqual(agent_secretary._agent_parse(reg_rquest), self.agent)

    def test_register_agent(self):
        """Check _register_agent(agent) method:
        1. Create Agent object;
        2. agent_secretary._register_agent(agent) for write it to DB;
        3. Check, is agent exists in the list active agents;"""

        agent_secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)

        self.assertTrue(agent_secretary._register_agent(self.agent))
        self.assertTrue(center_storage.is_agent_exist(
                        self.agent.address, self.agent.port))

    def test_register_duplicated_agent(self):
        """Check _register_agent(agent) method for handle duplicates:
        1. Create Agent object;
        2. agent_secretary._register_agent(agent) for write it to DB;
        3. Check, is agent exists in the list active agents;
        4. Register same agent again and check, that _register_agent(agent)
           return False;
        5. Check, that agent is still exists in the list active agents."""

        agent_secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)

        self.assertTrue(agent_secretary._register_agent(self.agent))
        self.assertTrue(center_storage.is_agent_exist(
                        self.agent.address, self.agent.port))

        self.assertFalse(agent_secretary._register_agent(self.agent))
        self.assertTrue(center_storage.is_agent_exist(
                        self.agent.address, self.agent.port))

    def test_handle_request_register_request(self):
        """Check _handle_request methiod for handle RegisterRequestMes():
        1. Call _handle_request(RegisterRequestMes);
        2. Check that method _handle_register_request is called."""

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
        """Check _handle_request methiod for handle ExpressionRequestMes():
        1. Call _handle_request(ExpressionRequestMes);
        2. Check that method _handle_expression_request is called."""

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
        """Check _handle_request methiod for handle Incorrect messages:
        1. Call _handle_request(DiffRequestMes);
        2. Check that exception UnsupportedMessageTypeException was raised."""

        secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)
        secretary._handle_register_request = MagicMock()
        secretary._handle_expression_request = MagicMock()

        unsupported_req = protocol.DiffRequestMes()

        sock = None

        with self.assertRaises(protocol.UnsupportedMessageTypeException):
            secretary._handle_request(unsupported_req, sock)

    def test_handle_expression_request_match_two_objects(self):
        """Check _handle_expression_request method:
        1. Create DB with some objects;
        2. Execute _handle_expression_request with expression, matched 2
           objects.
        3. _handle_expression_request should send 3 messages:
            1) ExpressionsLenghtMes;
            2) ExpressionUnitMes for first object;
            3) ExpressionUnitMes for second object;"""

        secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)
        protocol.send_message = MagicMock()

        sock = socket(AF_INET, SOCK_STREAM)

        expr_req = protocol.ExpressionRequestMes()
        expr_req['Expression'] = '123456'
        expr_req['Type'] = 'Any'

        secretary._handle_expression_request(expr_req, sock)

        expr_lenght_mes = protocol.ExpressionsLenghtMes()
        expr_lenght_mes['Lenght'] = 2
        calls = [call(expr_lenght_mes, sock)]

        uMes = protocol.ExpressionUnitMes()
        uMes['Agent'] = str(self.agent)
        uMes['Space'] = self.new_files[0][0]
        uMes['Object'] = self.new_files[0][1]
        uMes['String'] = self.new_files[0][2]
        calls.append(call(uMes, sock))

        uMes = protocol.ExpressionUnitMes()
        uMes['Agent'] = str(self.agent)
        uMes['Space'] = self.new_files[1][0]
        uMes['Object'] = self.new_files[1][1]
        uMes['String'] = self.new_files[1][2]
        calls.append(call(uMes, sock))

        protocol.send_message.assert_has_calls(calls, any_order=True)

    def test_handle_expression_request_match_zero_objects(self):
        """Check _handle_expression_request method:
        1. Create DB with some objects;
        2. Execute _handle_expression_request with expression, matched 0
           objects.
        3. _handle_expression_request should send ExpressionsLenghtMes with
           Lenght=0 only."""

        secretary = monitoring_center.AgentSecretary("127.0.0.1", 5555)
        protocol.send_message = MagicMock()

        sock = socket(AF_INET, SOCK_STREAM)

        expr_req = protocol.ExpressionRequestMes()
        expr_req['Expression'] = '1234567890123456'
        expr_req['Type'] = 'Any'

        secretary._handle_expression_request(expr_req, sock)

        expr_lenght_mes = protocol.ExpressionsLenghtMes()
        expr_lenght_mes['Lenght'] = 0
        calls = [call(expr_lenght_mes, sock)]

        protocol.send_message.assert_has_calls(calls, any_order=True)


if __name__ == '__main__':
    unittest.main()
