import globals
import logging
from loggings import ColoredLogger
from os.path import exists
from os import remove

logging.setLoggerClass(ColoredLogger)
logger = logging.getLogger(__name__)

with open('config.csv', 'r') as f:
    first_line = True
    for i in f.read().split("\n"):
        i = i.replace("\r", "")
        if i == "":
            continue
        if i[0] == "#":
            continue
        if first_line:
            if i == "ip,meter,port":
                first_line = False
                continue
            else:
                logger.fatal("Config.csv Read ERROR")
                exit("CFG_ERROR")
        ip, meter_id, ser_port = tuple(i.replace("\"", "").split(","))

        globals.METERS_IP_MAP[ip] = [meter_id, ser_port]
del first_line

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
