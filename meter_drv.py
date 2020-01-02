import time
import traceback
import serial.rs485
import serial

import init
from util import logger

bauds = {600: 0b00000010,
         1200: 0b00000100,
         2400: 0b00001000,
         4800: 0b00010000,
         9600: 0b00100000,
         19200: 0b01000000
         }


def _crc16(data):
    wCRCTable = [
        0X0000, 0XC0C1, 0XC181, 0X0140, 0XC301, 0X03C0, 0X0280, 0XC241,
        0XC601, 0X06C0, 0X0780, 0XC741, 0X0500, 0XC5C1, 0XC481, 0X0440,
        0XCC01, 0X0CC0, 0X0D80, 0XCD41, 0X0F00, 0XCFC1, 0XCE81, 0X0E40,
        0X0A00, 0XCAC1, 0XCB81, 0X0B40, 0XC901, 0X09C0, 0X0880, 0XC841,
        0XD801, 0X18C0, 0X1980, 0XD941, 0X1B00, 0XDBC1, 0XDA81, 0X1A40,
        0X1E00, 0XDEC1, 0XDF81, 0X1F40, 0XDD01, 0X1DC0, 0X1C80, 0XDC41,
        0X1400, 0XD4C1, 0XD581, 0X1540, 0XD701, 0X17C0, 0X1680, 0XD641,
        0XD201, 0X12C0, 0X1380, 0XD341, 0X1100, 0XD1C1, 0XD081, 0X1040,
        0XF001, 0X30C0, 0X3180, 0XF141, 0X3300, 0XF3C1, 0XF281, 0X3240,
        0X3600, 0XF6C1, 0XF781, 0X3740, 0XF501, 0X35C0, 0X3480, 0XF441,
        0X3C00, 0XFCC1, 0XFD81, 0X3D40, 0XFF01, 0X3FC0, 0X3E80, 0XFE41,
        0XFA01, 0X3AC0, 0X3B80, 0XFB41, 0X3900, 0XF9C1, 0XF881, 0X3840,
        0X2800, 0XE8C1, 0XE981, 0X2940, 0XEB01, 0X2BC0, 0X2A80, 0XEA41,
        0XEE01, 0X2EC0, 0X2F80, 0XEF41, 0X2D00, 0XEDC1, 0XEC81, 0X2C40,
        0XE401, 0X24C0, 0X2580, 0XE541, 0X2700, 0XE7C1, 0XE681, 0X2640,
        0X2200, 0XE2C1, 0XE381, 0X2340, 0XE101, 0X21C0, 0X2080, 0XE041,
        0XA001, 0X60C0, 0X6180, 0XA141, 0X6300, 0XA3C1, 0XA281, 0X6240,
        0X6600, 0XA6C1, 0XA781, 0X6740, 0XA501, 0X65C0, 0X6480, 0XA441,
        0X6C00, 0XACC1, 0XAD81, 0X6D40, 0XAF01, 0X6FC0, 0X6E80, 0XAE41,
        0XAA01, 0X6AC0, 0X6B80, 0XAB41, 0X6900, 0XA9C1, 0XA881, 0X6840,
        0X7800, 0XB8C1, 0XB981, 0X7940, 0XBB01, 0X7BC0, 0X7A80, 0XBA41,
        0XBE01, 0X7EC0, 0X7F80, 0XBF41, 0X7D00, 0XBDC1, 0XBC81, 0X7C40,
        0XB401, 0X74C0, 0X7580, 0XB541, 0X7700, 0XB7C1, 0XB681, 0X7640,
        0X7200, 0XB2C1, 0XB381, 0X7340, 0XB101, 0X71C0, 0X7080, 0XB041,
        0X5000, 0X90C1, 0X9181, 0X5140, 0X9301, 0X53C0, 0X5280, 0X9241,
        0X9601, 0X56C0, 0X5780, 0X9741, 0X5500, 0X95C1, 0X9481, 0X5440,
        0X9C01, 0X5CC0, 0X5D80, 0X9D41, 0X5F00, 0X9FC1, 0X9E81, 0X5E40,
        0X5A00, 0X9AC1, 0X9B81, 0X5B40, 0X9901, 0X59C0, 0X5880, 0X9841,
        0X8801, 0X48C0, 0X4980, 0X8941, 0X4B00, 0X8BC1, 0X8A81, 0X4A40,
        0X4E00, 0X8EC1, 0X8F81, 0X4F40, 0X8D01, 0X4DC0, 0X4C80, 0X8C41,
        0X4400, 0X84C1, 0X8581, 0X4540, 0X8701, 0X47C0, 0X4680, 0X8641,
        0X8201, 0X42C0, 0X4380, 0X8341, 0X4100, 0X81C1, 0X8081, 0X4040]
    crc_hi = 0xFF
    crc_lo = 0xFF

    for w in data:
        index = crc_lo ^ w
        crc_val = wCRCTable[index]
        crc_temp = int(crc_val / 256)
        crc_val_low = crc_val - (crc_temp * 256)
        crc_lo = crc_val_low ^ crc_hi
        crc_hi = crc_temp

    crc = crc_hi * 256 + crc_lo
    return crc


def get_power_string(p):
    s = "%x%02x%02x" % (p[-1], p[-2], p[-3])
    l = list(s)
    l.insert(-4, '.')
    s = ''.join(l)
    s = float(s)
    return s


class DLFrame:
    def __init__(self):
        self.tx_addr = []
        self.tx_ctrl = 0x0
        self.tx_payload = []

        self.rx_addr = []
        self.rx_ctrl = 0x0
        self.rx_payload = []

        self.tx_frame = []
        self.rx_frame = []
        self.tx_bytes = bytearray()
        self.rx_bytes = bytearray()

    def rx_append(self, data):
        self.rx_bytes = self.rx_bytes + bytearray([data])

    def eof(self):
        self.rx_frame = [c for c in self.rx_bytes]

    def encode(self, addr, ctrl, payload=None):
        if payload is None:
            payload = []
        self.tx_addr = addr
        self.tx_ctrl = ctrl
        self.tx_payload = payload
        self.tx_frame = [0xfe, 0xfe, 0x68] + list(reversed(self.tx_addr))
        self.tx_frame = self.tx_frame + [0x68, self.tx_ctrl]
        self.tx_frame = self.tx_frame + [len(self.tx_payload)] + [((p + 0x33) & 0xff) for p in self.tx_payload]
        self.tx_frame = self.tx_frame + [sum(self.tx_frame[2:]) & 0xff] + [0x16]
        self.tx_bytes = bytearray(self.tx_frame)

    def decode(self):
        self.rx_addr = [c for c in self.rx_frame[1:7]]
        self.rx_addr.reverse()
        self.rx_ctrl = self.rx_frame[8]
        self.rx_payload = [((p - 0x33) & 0xff) for p in self.rx_frame[10:-2]]

        return (sum(self.rx_frame[0:-2]) & 0xff) == self.rx_frame[-2]

class Channel:
    def __init__(self):
        self.ser = serial.Serial()
        self.ser.port = "Null"
        self.ser.baudrate = 0
        self.ser.parity = serial.PARITY_EVEN
        self.ser.timeout = 0
        self.ser.rs485_mode = serial.rs485.RS485Settings()
        self.timeout = 200
        # real time out = self.timeout*2

    def _open(self):
        try:
            self.ser.open()
            return True
        except serial.SerialException:
            logger.error("Channel %s init fail,reason:\"%s\"" % (self.ser.port, traceback.format_exc()))
            return False

    def _close(self):
        if self.ser.isOpen():
            self.ser.close()

    def open(self, port, baud):
        self._close()
        self.ser.port = str(port)
        self.ser.baudrate = int(baud)
        return self._open()

    def change_baud(self, baud):
        self._close()
        logger.info("Change channel %s from %s to %s" % (self.ser.port, self.ser.baudrate, int(baud)))
        self.ser.baudrate = int(baud)
        return self._open()

    def read_power(self, addr):
        frame = DLFrame()
        frame.encode(addr, 0x11, [0x0, 0x0, 0x3, 0x2])
        frame, rsp = self.transmite_frame(frame)
        if rsp:
            s = get_power_string(frame.rx_payload)
            return int(s * 1000)
        else:
            return None

    def change_meter_baud(self, addr, target_baud):
        target_baud = int(target_baud)
        if not target_baud in bauds:
            logger.error("meters doesn't support %s baudrate" % target_baud)
            return False
        frame = DLFrame()
        frame.encode(addr, 0x17, [bauds[target_baud]])
        frame, rsp = self.transmite_frame(frame)
        if rsp:
            return True
        else:
            return False

    def transmite_frame(self, frame):
        self.write_frame(frame)
        frame, rsp = self.read_frame(frame)

        if rsp:
            frame.decode()
        return frame, rsp

    def read_temp(self, addr):
        try:
            tx_frame = [addr, 0x03, 0x00, 0x00, 0x00, 0x02]
            c16 = _crc16(tx_frame)
            h = c16 >> 8
            l = c16 & 0xff
            tx_frame += [l, h]

            self.ser.write(tx_frame)
            rsp = b""
            n = 0
            while 1:
                if n > self.timeout:
                    logger.warn("Temp meter No resp,port %s ID%s" % (self.ser.port, addr))
                    break

                rsp += self.ser.read(11)
                if len(rsp) >= 9:
                    break
                else:
                    time.sleep(1 / 1000)
                    n += 1
            if len(rsp) < 9:
                return None, None
            rsp_c16 = _crc16(rsp[:7])
            h = rsp_c16 >> 8
            l = rsp_c16 & 0xff

            if not (rsp[7] == l and rsp[8] == h):
                logger.warn("CRC16 check fail, not %s should be %s" % (rsp[7:], [l, h]))

            temp = rsp[5] * 256 + rsp[6]
            if temp >= 32768:
                temp -= 65536
            humi = rsp[3] * 256 + rsp[4]

            temp = round(temp / 10, 2)
            humi = round(humi / 10, 2)
            return temp, humi
        except:
            traceback.print_exc()
            return None,None

    def isOpen(self):
        return self.ser.isOpen()

    def close(self):
        self.ser.close()

    def write_frame(self, frame):
        rsp = self.ser.write(frame.tx_bytes)
        time.sleep(20/1000)
        return rsp

    def in_waiting(self):
        return self.ser.inWaiting()

    def read_frame(self, frame):
        timeout_count = 0
        time.sleep(0.08)
        state = 'ST_FSTART'
        state_count = 0
        while 1:
            if self.in_waiting() == 0:
                timeout_count += 1
                time.sleep(0.001)
                if timeout_count > self.timeout:
                    return frame, False
            else:
                read_data = bytearray(self.ser.read(self.in_waiting()))
                for c in read_data:
                    if state == 'ST_FSTART':
                        if c == 0x68:
                            frame.rx_append(c)
                            state = 'ST_ADDR'
                            state_count = 6
                    elif state == 'ST_ADDR':
                        frame.rx_append(c)
                        state_count = state_count - 1
                        if state_count == 0:
                            state = 'ST_SSTART'
                    elif state == 'ST_SSTART':
                        frame.rx_append(c)
                        state = 'ST_CTRL'
                    elif state == 'ST_CTRL':
                        frame.rx_append(c)
                        state = 'ST_LEN'
                    elif state == 'ST_LEN':
                        frame.rx_append(c)
                        if c > 0:
                            state = 'ST_PAYLOAD'
                            state_count = c
                        else:
                            state = 'ST_CKSUM'

                    elif state == 'ST_PAYLOAD':
                        frame.rx_append(c)
                        state_count = state_count - 1
                        if state_count == 0:
                            state = 'ST_CKSUM'

                    elif state == 'ST_CKSUM':
                        frame.rx_append(c)
                        state = 'ST_EOF'

                    elif state == 'ST_EOF':
                        frame.rx_append(c)
                        frame.eof()
                        return frame, True


class Meters:
    def __init__(self):
        self.COM_PORT = ""
        self.chn = None
        self.verbose = False
        self.ser_lock = False
        self.caches_time = {}
        self.caches_val = {}

    def read_env(self, id):
        self.ser_lock = True
        temp, humi = self.chn.read_temp(int(id))
        self.ser_lock = False
        return temp, humi

    def read_power(self, SerialNumber):
        # page 53, table A3
        if not SerialNumber in self.caches_time:
            self.caches_time[SerialNumber] = 0
            self.caches_val[SerialNumber] = 0
        if not time.time() - self.caches_time[SerialNumber] > init.SERIAL_CACHE_TTL:
            # logger.info("CACHE HINT!!")
            return self.caches_val[SerialNumber]
        if self.ser_lock:
            while 1:
                if self.ser_lock:
                    # logger.info("Request Jamd")
                    time.sleep(init.SER_LOCK_RECHECK_TIME)
                else:
                    break

        addr = self.ser2addr(SerialNumber)

        self.ser_lock = True
        rsp = self.chn.read_power(addr)
        self.ser_lock = False

        if not rsp is None:
            self.caches_val[SerialNumber] = rsp
            self.caches_time[SerialNumber] = time.time()
            return rsp
        else:
            logger.error("COM %s, Addr %s no resp!" % (self.COM_PORT, SerialNumber))
            return None

    def ser2addr(self, SerialNumber):
        addr = []
        for i in [0, 2, 4, 6, 8, 10]:
            addr.append(int("0x%s" % SerialNumber[i:i + 2], 16))
        return addr

    def init(self,port, baud):
        self.COM_PORT = port
        self.chn = Channel()
        self.chn.open(port, int(baud))
        logger.info("Open %s ,baudrate is %s" % (port, baud))
        if not self.chn.isOpen():
            logger.error("Serial port %s open fail!" % port)
            return False
        return True

    def change_meter_baud(self, addr, target_baud):
        addr = self.ser2addr(addr)
        return self.chn.change_meter_baud(addr, int(target_baud))

    def change_ser_baud(self, target_baud):
        return self.chn.change_baud(int(target_baud))
