import display
import time

while True:
    try:
        display.main(server="raspberrypi")
    except OSError:
        time.sleep(6)

