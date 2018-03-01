#!/usr/bin/env python3

import subprocess
import pid

proc = subprocess.Popen(['lsof -P'], shell=True, stdout=subprocess.PIPE)
num_same_pid = 0

# Dummy Read Header
line = proc.stdout.readline()
prev_pid = '1'
pids = dict()

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
            pids[int(prev_pid)] = num_same_pid
            prev_pid = cur_pid
            num_same_pid = 0
proc.wait()

print("PID", '\t', "Connections")
for x in sorted(pids.keys()):
    print(x, '\t\t' if int(x) < 100 else '\t', pids[x])

