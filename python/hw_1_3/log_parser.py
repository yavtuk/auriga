#!/usr/bin/env python3
import re
from datetime import datetime, timedelta


def log_parser(file_name):
    stats = dict()

    l = list()
    with open(file_name, "r") as fin:
        l.clear()
        for line in fin:
            data = re.sub('[<>\[\]]', '', line).split()
            packed_list = prepare_list(data)
            add_data_to_dict(packed_list, stats)
    fin.close()
    exec_time_print(stats)
    err_msg_print(stats)

def add_data_to_dict(data, res):
    indx = int(data.pop(0))

    try:
        d = res[indx]
    except:
        d = {'sDate': None, 'eDate': None, 'sTime': None, 'eTime': None, 'res_msg': None, 'err_msg': None}

    msg = data.pop()
    if data.pop(0) == 'INFO':
        if 0 == msg.find('Started'):
            d['sDate'] = data.pop(0)
            d['sTime'] = data.pop(0)
        elif 0 == msg.find('Finished'):
            d['eDate'] = data.pop(0)
            d['eTime'] = data.pop(0)
    else:
        d['err_msg'] = msg

    res[indx] = d

def prepare_list(data):
    """
    [0] = id req
    [1] = type msg
    [2] = date
    [3] = time
    [4] = msg
    :return: packed list
    """
    pack_list = list()
    pack_list.append(data[-1])
    pack_list.append(data[2])
    pack_list.append(data[0])
    pack_list.append(data[1])

    msg = ""
    for x in range(3, len(data) - 3):
        msg += data[x]
        msg += ' '

    pack_list.append(msg)
    return pack_list

def exec_time_print(data):
    for x in data:
        info = data[x]
        if info['eDate'] and info['sDate']:
            syear, smonth, sday = re.sub('[-]', ' ', info['sDate']).split()
            shour, sminute, ssecond = re.sub('[:]', ' ', info['sTime']).split()
            ssecond, smicrosec = re.sub('[.]', ' ', ssecond).split()
            s = datetime(year=int(syear), month=int(smonth), day=int(sday), hour=int(shour),
                          minute=int(sminute), second=int(ssecond), microsecond=int(smicrosec))

            eyear, emonth, eday = re.sub('[-]', ' ', info['eDate']).split()
            ehour, eminute, esecond = re.sub('[:]', ' ', info['eTime']).split()
            esecond, emicrosec = re.sub('[.]', ' ', esecond).split()
            e = datetime(year=int(eyear), month=int(emonth), day=int(eday), hour=int(ehour),
                          minute=int(eminute), second=int(esecond), microsecond=int(emicrosec))
            print("Request %d: %s"%(x, (e-s).total_seconds()))
        else:
            print("Request %d: -1"%x)

def err_msg_print(data):
    print("")
    print("Errors")
    for x in data:
        info = data[x]
        if info['err_msg'] is not None:
            print("Request %d: %s"%(x, info['err_msg']))

if __name__ == "__main__":
    log_parser("logs/task_1_2.log")
