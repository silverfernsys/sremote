#! /usr/bin/env python
import sys, subprocess

class CPUStats():
    pid = 0
    utime_before = 0
    stime_before = 0
    time_total_before = 0

    def __init__(self, pid):
        self.pid = pid
        (self.utime_before,
        self.stime_before,
        self.time_total_before) = self.__stat__()

    def cpu_percent(self):
        (utime_after,
        stime_after,
        time_total_after) = self.__stat__()

        if time_total_after > 0:
            user_util = 100.0 * float(utime_after) / time_total_after
            sys_util = 100.0 * float(stime_after) / time_total_after
        else:
            user_util = 0.0
            sys_util = 0.0

        return (user_util, sys_util)


    def cpu_percent_change(self):
        (utime_after,
        stime_after,
        time_total_after) = self.__stat__()

        if (time_total_after - self.time_total_before != 0.0):
            user_util = 100.0 * float(utime_after - self.utime_before) / (time_total_after - self.time_total_before)
            sys_util = 100.0 * float(stime_after - self.stime_before) / (time_total_after - self.time_total_before)
        else:
            user_util = 0.0
            sys_util = 0.0
        
        self.utime_before = utime_after
        self.stime_before = stime_after
        self.time_total_before = time_total_after

        return (user_util, sys_util)

    def stat(self):
        return self.__stat__()

    def __stat__(self):
        try:
            # cat /proc/<pid>/stat
            command = ['cat', '/proc/%s/stat' % self.pid]
            p = subprocess.Popen(command, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            out, err = p.communicate()
            stat_list = out.split(' ')
            utime = int(stat_list[13])
            stime = int(stat_list[14])
            # cat /proc/stat
            command = ['cat', '/proc/stat']
            p = subprocess.Popen(command, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            out, err = p.communicate()
            stat_list = out.split('\n')
            cpu_timings = stat_list[0].split(' ')[1:]
            time_total = 0
            for timing in cpu_timings:
                try:
                    time_total += int(timing)
                except:
                    pass
            return utime, stime, time_total
        except Exception as e:
            # print("CPUStats.__stat__ Exception: %s" % e)
            return 0, 0, 0


class MemoryStats():
    pid = 0

    def __init__(self, pid):
        self.pid = pid

    def memory_percent(self):
        (memory_used, memory_total,
        free_mem, cached, cached_swap,
        total_swap, free_swap) = self.__stat__()

        percent = 100.0 * float(memory_used) / memory_total

        return percent

    def stat(self):
        return self.__stat__()

    def __stat__(self):
        try:
            # cat /proc/<pid>/smaps
            command = ['cat', '/proc/%s/smaps' % self.pid]
            p = subprocess.Popen(command, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            out, err = p.communicate()
            stat_list = out.split('\n')
            total_process_mem = 0
            for stat in stat_list:
                if stat.startswith('Size:'):
                    split_stat = stat.split(' ')
                    mem = int(split_stat[-2])
                    total_process_mem += mem
                else:
                    pass

            # http://www.cyberciti.biz/faq/linux-check-memory-usage/
            # egrep --color 'Mem|Cache|Swap' /proc/meminfo
            command = ['egrep', '--color', 'Mem|Cache|Swap', '/proc/meminfo']
            p = subprocess.Popen(command, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            out, err = p.communicate()
            stat_list = out.split('\n')

            total_mem = 0
            free_mem = 0
            cached = 0
            cached_swap = 0
            total_swap = 0
            free_swap = 0

            for stat in stat_list:
                if stat.startswith('MemTotal:'):
                    split_stat = stat.split(' ')
                    mem = int(split_stat[-2])
                    total_mem = mem
                elif stat.startswith('MemFree:'):
                    split_stat = stat.split(' ')
                    mem = int(split_stat[-2])
                    free_mem = mem
                elif stat.startswith('Cached:'):
                    split_stat = stat.split(' ')
                    mem = int(split_stat[-2])
                    cached = mem
                elif stat.startswith('SwapCached:'):
                    split_stat = stat.split(' ')
                    mem = int(split_stat[-2])
                    cached_swap = mem
                elif stat.startswith('SwapTotal:'):
                    split_stat = stat.split(' ')
                    mem = int(split_stat[-2])
                    total_swap = mem
                elif stat.startswith('SwapFree:'):
                    split_stat = stat.split(' ')
                    mem = int(split_stat[-2])
                    free_swap = mem

            return (total_process_mem,
                total_mem, free_mem, cached,
                cached_swap, total_swap, free_swap)
        except Exception as e:
            print(e)
            return (0, 0, 0, 0, 0, 0, 0)


def main():
    try:
        arg = sys.argv[1]
        if arg.isdigit():
            cpu_stats = CPUStats(int(arg))
            print(cpu_stats.stat())
            print(cpu_stats.cpu_percent())
            print(cpu_stats.cpu_percent_change())

            memory_stats = MemoryStats(int(arg))
            print(memory_stats.stat())
            print(memory_stats.memory_percent())
        else:
            print("usage: <pid> must be an integer")
    except IndexError:
        print "usage: ./process_cpu.py <pid>"
        sys.exit(1)


if __name__ == '__main__':
    main()
