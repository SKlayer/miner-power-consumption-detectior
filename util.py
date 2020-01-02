import globals
import logging
from loggings import ColoredLogger
from os.path import exists
from os import remove

logging.setLoggerClass(ColoredLogger)
logger = logging.getLogger(__name__)

def csv_loadin(file_name):
    out = []

    with open(file_name, 'r') as f:
        first_line = True
        for i in f.read().split("\n"):
            i = i.replace("\r", "")
            if i == "":
                continue
            if i[0] == "#":
                continue
            if first_line:
                first_line = False
                continue
            ip, meter_id, ser_port = tuple(i.replace("\"", "").split(",")[:3])
            out.append([ip, meter_id, ser_port])
    return out




def set_meter_done_flag(flag):
    if flag:
        with open('meter_done.flg', 'wb') as f:
            f.write(b"")
    else:
        remove("./meter_done.flg")
    return True

def read_meter_done_flag():
    if exists("./meter_done.flg"):
        return True
    return False
def read_ignore_self_check():
    if exists("./ignore_self_check"):
        return True
    return False



for i in csv_loadin("config.csv"):
    globals.METERS_IP_MAP[i[0]] = [i[1], i[2]]
for i in csv_loadin("temp_config.csv"):
    globals.TEMP_MAP[i[0]] = [int(i[1],16), i[2]]
