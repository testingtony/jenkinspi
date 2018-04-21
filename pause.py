class Pause:
    import time

    __now = time.ticks_ms()

    @classmethod
    def pause(cls, time_to_pause=100):
        import time
        import machine
        while time.ticks_diff(time.ticks_ms(), Pause.__now) < time_to_pause:
            pass
        Pause.__now = time.ticks_ms()
