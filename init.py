import device_init

THREAD_POOL_MULTIPLE = 3
# 4 threads per COM port
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 6080
# tornado listen
INIT_BAUD = 2400
TARGET_BAUD = 9600
TARGET_BAUD_BIT = 0x20
DELAY_FOR_READ = 0.085
SER_LOCK_RECHECK_TIME = 0.03
SER_WAIT_FOR_READ = 0.005
METER_MAX_RETRY = 5
SERIAL_CACHE_TTL = 0.2

if __name__ == '__main__':
    device_init.self_check_n_init_ports()
    import power_server
    power_server.run()
