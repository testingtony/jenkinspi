# This file is executed on every boot (including wake-boot from deepsleep)
import esp
import gc
import webrepl

webrepl.stop()
esp.osdebug(None)

import uos, machine
uos.dupterm(machine.UART(0, 115200), 1)
gc.collect()


def connect_to_wifi(ssid, password):
    import network
    import time
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)
        i = 60
        while i > 0 and not wlan.isconnected():
            time.sleep(1)
            print("remain {0}".format(i))
            i -= 1
    print('network config:', wlan.ifconfig())
