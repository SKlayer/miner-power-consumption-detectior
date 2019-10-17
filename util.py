import globals
import logging
from loggings import ColoredLogger

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

