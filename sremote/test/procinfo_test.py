import unittest
from time import time
from sremote.procinfo import ProcInfo

class ProcInfoTest(unittest.TestCase):
    def setUp(self):
        self.proc_0 = ProcInfo('soffice', 'soffice', None, 0, 'STOPPED', 1.000)
        self.proc_1 = ProcInfo('sremote', 'sremote', 9123, 0, 'STOPPED', 1.000)

    def tearDown(self):
        pass

    def test_get(self):
        self.assertEqual(self.proc_0, ProcInfo.get('soffice', 'soffice'), "get works")
        self.assertEqual(self.proc_1, ProcInfo.get('sremote', 'sremote'), "get works")

    def test_updateall(self):
        before_count_proc_0 = len(self.proc_0.cpu)
        before_count_proc_1 = len(self.proc_1.cpu)
        ProcInfo.updateall()
        ProcInfo.updateall()
        ProcInfo.updateall()
        after_count_proc_0 = len(self.proc_0.cpu)
        after_count_proc_1 = len(self.proc_1.cpu)
        self.assertEqual(before_count_proc_0 + 3, after_count_proc_0, "after_count_proc_0 is 3 more than before_count_proc_0")
        self.assertEqual(before_count_proc_1 + 3, after_count_proc_1, "after_count_proc_1 is 3 more than before_count_proc_1")

    def test_cpu_and_mem_filter(self):
        before_count_cpu = len(self.proc_0.cpu)
        before_count_mem = len(self.proc_0.mem)
        self.assertEqual(before_count_cpu, before_count_mem, "before_count_cpu == before_count_mem")
        timestamp = time()
        ProcInfo.updateall()
        ProcInfo.updateall()
        ProcInfo.updateall()
        self.assertEqual(len(self.proc_0.get_cpu(timestamp)), 3, "filtered cpu length == 3")
        self.assertEqual(len(self.proc_0.get_mem(timestamp)), 3, "filtered cpu length == 3")
 
    def test_statename_change(self):
        self.assertEqual(self.proc_0.state, 0, "state is 0")
        self.proc_0.statename = 'STARTING'
        self.assertEqual(self.proc_0.state, 10, "state is 10")
        self.proc_0.statename = 'RUNNING'
        self.assertEqual(self.proc_0.state, 20, "state is 20")
        self.proc_0.statename = 'BACKOFF'
        self.assertEqual(self.proc_0.state, 30, "state is 30")
        self.proc_0.statename = 'STOPPING'
        self.assertEqual(self.proc_0.state, 40, "state is 40")
        self.proc_0.statename = 'EXITED'
        self.assertEqual(self.proc_0.state, 100, "state is 100")
        self.proc_0.statename = 'FATAL'
        self.assertEqual(self.proc_0.state, 200, "state is 200")
        self.proc_0.statename = 'UNKNOWN'
        self.assertEqual(self.proc_0.state, 1000, "state is 200")
