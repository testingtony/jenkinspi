# This file is executed on every boot (including wake-boot from deepsleep)
import esp
import gc
import webrepl
webrepl.start()
esp.osdebug(None)
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


def rm_rf(dir="fonts"):
    import os
    for f in ["fonts/{}".format(f) for f in os.listdir('fonts')]:
        os.remove(f)
    os.rmdir('fonts')

