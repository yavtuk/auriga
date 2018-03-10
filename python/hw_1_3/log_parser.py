#!/usr/bin/env python3
import re


def log_parser(file_name):
    start_dict = dict()
    finish_dict = dict()
    error_dict = dict()

    with open(file_name, "r") as fin:
        for line in fin:
            data = re.sub('[<>\[\]]', '', line).split()
            if data[2] == "INFO":
                if data[3] == "Started":
                    start_dict[int(data[-1])] = data[1]
                elif data[3] == "Finished":
                    finish_dict[int(data[-1])] = data[1]
            else:
                error_dict[int(data[-1])] = data[-1]
    fin.close()

    exec_time_print(start_dict, finish_dict)
    err_msg_print(error_dict)


def exec_time_print(stime, etime):
    for x in stime:
        try:
            s = stime[int(x)]
            e = etime[int(x)]
            print("Request {0}: {1: 8.6f}".format(x, get_period_in_sec(s, e)))
        except:
            pass

def err_msg_print(errors_dict):
    print("Errors")
    for x in errors_dict:
        print("Request %d: Calculation failed" % x)

def get_period_in_sec(stm, etm):
    precision = 1000000
    hs, ms, ss = re.sub('[:]', ' ', stm).split()
    ss, mss = re.sub('[.]', ' ', ss).split()
    he, me, se = re.sub('[:]', ' ', etm).split()
    se, mse = re.sub('[.]', ' ', se).split()
    mss = (((int(hs) * 3600) + (int(ms) * 60) + (int(ss))) * precision) + int(mss)
    mse = (((int(he) * 3600) + (int(me) * 60) + (int(se))) * precision) + int(mse)
    delta = mse - mss
    sec = delta / precision
    ms = (delta % precision) / precision
    return sec + ms

if __name__ == "__main__":
    log_parser("logs/task_1_2.log")