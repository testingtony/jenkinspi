import display
import time


def connect_me():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    for sid in [str(x[0], 'utf-8') for x in wlan.scan()]:
        print(sid)
        if sid == 'A_SID':
            wlan.connect('A_SIDD', 'a sidd password')
            return wlan
        elif sid == 'ANOTHER_SIDD':
            wlan.connect('ANOTHER_SIDD', 'ANOTHER_SIDD_PASSWORD')
            return wlan
    return None


while True:
    wlan = connect_me()
    if wlan is not None:
        display.main()
        wlan.disconnect()
        wlan.active(False)

