#!/usr/bin/env python3

import subprocess
import pid

proc = subprocess.Popen(['lsof -P'], shell=True, stdout=subprocess.PIPE)
num_same_pid = 0

# Dummy Read Header
line = proc.stdout.readline()
prev_pid = '1'
print("PID", '\t', "Connections")

while True:
    line = proc.stdout.readline()
    line = line.decode()

    if line == '' and proc.poll() is not None:
        break
    else:
        cur_pid = pid.get_pid_from_str(line)
        if cur_pid == prev_pid:
            num_same_pid += 1
        else:
            print(prev_pid, '\t\t' if int(prev_pid) < 100 else '\t', num_same_pid)
            prev_pid = cur_pid
            num_same_pid = 0

proc.wait()