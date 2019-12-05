import time
import traceback
from concurrent.futures import ThreadPoolExecutor

import tornado.ioloop
import tornado.options
import tornado.web
from tornado import gen
from tornado.concurrent import run_on_executor

import globals
import init
from util import logger


class api_v1_power(tornado.web.RequestHandler):
    if len(globals.COM_SHARD) <= 0:
        executor = ThreadPoolExecutor(1)
    else:
        executor = ThreadPoolExecutor(len(globals.COM_SHARD) * 2)

    @run_on_executor
    def read_power_by_IP(self, ip):
        if ip in globals.METERS_IP_MAP:
            SN = globals.METERS_IP_MAP[ip][0]
            SER = globals.METERS_IP_MAP[ip][1]
            return globals.COM_SHARD[SER].read_power(SN)
        else:
            logger.error("IP %s record not found" % ip)

    @gen.coroutine
    def get(self):
        start_point = time.time()
        if "ip" in self.request.arguments:
            ipaddr = self.get_argument("ip")
        else:
            ipaddr = self.request.remote_ip

        e = None

        if ipaddr not in globals.METERS_IP_MAP:
            elapsed = round(time.time() - start_point, 3)

            self.write({'time': time.time(),
                        "version": "0.0",
                        "power": -1,
                        "error": True,
                        "msg": "IP Not Found",
                        "ipaddr": ipaddr,
                        "elapsed": elapsed,
                        })
        else:
            try:
                power = yield self.read_power_by_IP(ipaddr)
                elapsed = round(time.time() - start_point, 3)
                if power is None:
                    self.write({'time': time.time(),
                                "version": "0.0",
                                "power": -1,
                                "error": True,
                                "msg": "broken data",
                                "ipaddr": ipaddr,
                                "elapsed": elapsed,
                                })
                else:
                    self.write({
                        'time': time.time(),
                        "version": "0.0",
                        "power": power,
                        "error": False,
                        "msg": "success",
                        "ipaddr": ipaddr,
                        "elapsed": elapsed,
                    })
                logger.debug("Request %s , cost %sms." % (ipaddr, round(elapsed * 1000, 3)))
            except Exception as excepts:
                traceback.print_exc()
                e = excepts
                pass
        if e:
            elapsed = round(time.time() - start_point, 3)
            logger.exception("Meters read error:%s" % traceback.format_exc())
            self.write({'time': time.time(),
                        "version": "0.0",
                        "power": -1,
                        "error": True,
                        "msg": e,
                        "ipaddr": ipaddr,
                        "elapsed": elapsed,
                        })
        self.finish()


class ra9(tornado.web.RequestHandler):
    def get(self):
        self.write("I am alive")
        self.finish()


def make_app():
    return tornado.web.Application([
        (r"/api/v1/power", api_v1_power),
        (r"/ra9", ra9),
    ], autoreload=False)


def run():
    app = make_app()
    logger.info("Server listening on %s:%s" % (init.LISTEN_IP, init.LISTEN_PORT,))
    app.listen(init.LISTEN_PORT, address=init.LISTEN_IP)
    tornado.ioloop.IOLoop.current().start()
