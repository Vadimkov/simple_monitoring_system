import unittest
import monitoring_center
import center_storage
import logging


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

        monitoring_center.update_files(agent, new_files)
        files_from_db = center_storage.get_full()

        print("Files from db:", str(files_from_db))
        print("Golden files:", str(golden_files))

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

        monitoring_center.update_files(agent, new_files)

        new_files = []
        new_files.append(['space1', 'obj1', 'content1'])
        new_files.append(['space2', 'obj2', 'content2'])
        new_files.append(['space3', 'obj3', 'content3'])

        monitoring_center.update_files(agent, new_files)

        files_from_db = center_storage.get_full()

        print("Files from db:", str(files_from_db))
        print("Golden files:", str(golden_files))

        self.assertEqual(len(files_from_db), len(golden_files))

        for f in files_from_db:
            self.assertTrue(f in golden_files)


if __name__ == '__main__':
    unittest.main()
