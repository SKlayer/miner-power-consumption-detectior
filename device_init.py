from util import *
import globals
import meter_drv


def self_check_n_init_ports():
    COMports = []
    print(globals.METERS_IP_MAP)
    for i in globals.METERS_IP_MAP:
        if globals.METERS_IP_MAP[i][1] not in COMports:
            COMports.append(globals.METERS_IP_MAP[i][1])
    for i in COMports:
        meter = meter_drv.Meters()
        meter.COM_PORT = i
        try:
            if not meter.init():
                logger.fatal("COM port %s init fail")
                exit("COM_INIT_FAIL")
        except Exception as e:
            logger.fatal("COM port %s init fail, %s" % e)
            exit("COM_INIT_FAIL")
        globals.COM_SHARD[i] = meter

    for i in globals.COM_SHARD:
        if not globals.COM_SHARD[i].chn.isOpen():
            logger.error("COM open fail! %s" % globals.COM_SHARD[i].COM_PORT)
            exit("COM_INIT_FAIL")
    for i in globals.METERS_IP_MAP:
        sn, dev = tuple(globals.METERS_IP_MAP[i])
        meter = globals.COM_SHARD[dev]
        power = meter.read_power(sn)
        if not power is None:
            logger.info("Serial %s-%s-Check OK, Power %sW" % (dev, sn, power))
        else:
            logger.fatal("Serial %s-%s-Check FAIL will retry another baud rate.!" % (dev, sn))
            #exit("SELF_CHECK_FAIL")
    for i in globals.METERS_IP_MAP:
        sn, dev = tuple(globals.METERS_IP_MAP[i])
        meter = globals.COM_SHARD[dev]
        result = meter.change_bps(sn)
        if not result:
            logger.fatal("Meter %s-%s-baud rate change fail!" % (dev, sn))
            #exit("SELF_CHECK_FAIL")
    for i in globals.COM_SHARD:
        result = globals.COM_SHARD[i].change_ser_baud()
        if not result:
            logger.fatal("Serial %s-baud rate change fail! exit.!" % (i))
            exit("SELF_CHECK_FAIL")
    for i in globals.COM_SHARD:
        if not globals.COM_SHARD[i].chn.isOpen():
            logger.error("COM open fail after change baud! %s" % globals.COM_SHARD[i].COM_PORT)
            exit("COM_INIT_FAIL")
    for i in globals.METERS_IP_MAP:
        sn, dev = tuple(globals.METERS_IP_MAP[i])
        meter = globals.COM_SHARD[dev]
        power = meter.read_power(sn)
        if not power is None:
            logger.info("Serial %s-%s-Check OK, Power %sW" % (dev, sn, power))
        else:
            logger.fatal("Serial %s-%s-Check FAIL exit.!" % (dev, sn))
            exit("SELF_CHECK_FAIL")
    import time
    for i in globals.METERS_IP_MAP:
        sn, dev = tuple(globals.METERS_IP_MAP[i])
        meter = globals.COM_SHARD[dev]
        elapsed = time.time()
        power = meter.read_power(sn)
        elapsed = time.time()-elapsed

        if not power is None:
            logger.info("Serial %s-%s-Check OK, Power %sW     TIME %sms" % (dev, sn, power, elapsed*1000))
        else:
            logger.fatal("Serial %s-%s-Check FAIL exit.!" % (dev, sn))
            exit("SELF_CHECK_FAIL")


    logger.critical("All device check OK!!")






