import time

now = time.ticks_ms()


def pause(time_to_pause=100):
    global now
    import time
    while time.ticks_diff(time.ticks_ms(), now) < time_to_pause:
        pass
    now = time.ticks_ms()
