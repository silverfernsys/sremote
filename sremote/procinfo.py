#!/usr/bin/env python
from procstats import CPUStats, MemoryStats
from time import time

STATE_MAP = {
    'STOPPED': 0,
    'STARTING': 10,
    'RUNNING': 20,
    'BACKOFF': 30,
    'STOPPING': 40,
    'EXITED': 100,
    'FATAL': 200,
    'UNKNOWN': 1000 
}

class ProcInfo(object):
    processes = {}

    def __init__(self, name, group, pid, state, statename, start):
        self.name = name
        self.group = group
        self._pid = pid
        self._state = state
        self._statename = statename
        self.start = start
        self.cpu = []
        self.mem = []
        self.cpu_stats = CPUStats(self.pid)
        self.mem_stats = MemoryStats(self.pid)

        ProcInfo.add(self)

    @property
    def state(self):
        return self._state

    @property
    def statename(self):
        return self._statename
    
    @statename.setter
    def statename(self, val):
        try:
            self._statename = val
            self._state = STATE_MAP[val]
        except Exception as e:
            print(e)

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, val):
        self._pid = val
        self.cpu_stats.pid = val
        self.mem_stats.pid = val

    def update(self):
        timestamp = time()
        user_util, sys_util = self.cpu_stats.cpu_percent_change()
        memory_percent = self.mem_stats.memory_percent()
        self.cpu.append([timestamp, user_util])
        self.mem.append([timestamp, memory_percent])

    def __str__(self):
        return 'name: %s, group: %s, pid: %s, cpu: %s, mem: %s' % (self.name, self.group, self._pid, self.cpu, self.mem)

    def to_dict(self):
        return {'name': self.name,
        'group': self.group,
        'pid': self._pid,
        'state': self._state,
        'statename': self._statename,
        'start': self.start,
        'cpu': self.cpu,
        'mem': self.mem,
        }

    @classmethod
    def get(self, group, name):
        try:
            return ProcInfo.processes[group][name]
        except:
            None

    @classmethod
    def add(self, proc):
        if proc.group not in ProcInfo.processes:
            ProcInfo.processes[proc.group] = {}
        ProcInfo.processes[proc.group][proc.name] = proc

    # A class method generator that yields the contents of the 'processes' dictionary
    @classmethod
    def all(self):
        for group in ProcInfo.processes:
            for name in ProcInfo.processes[group]:
                yield ProcInfo.processes[group][name]
        raise StopIteration()

    @classmethod
    def updateall(self):
        for p in ProcInfo.all():
            p.update()


import unittest

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

    def test_cpu_and_mem_equal_length(self):
        before_count_cpu = len(self.proc_0.cpu)
        before_count_mem = len(self.proc_0.mem)
        self.assertEqual(before_count_cpu, before_count_mem, "before_count_cpu == before_count_mem")
        ProcInfo.updateall()
        ProcInfo.updateall()
        ProcInfo.updateall()
        after_count_cpu = len(self.proc_0.cpu)
        after_count_mem = len(self.proc_0.mem)
        self.assertEqual(after_count_cpu, after_count_mem, "after_count_cpu == after_count_mem")
 
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

if __name__ == '__main__':
    unittest.main()
