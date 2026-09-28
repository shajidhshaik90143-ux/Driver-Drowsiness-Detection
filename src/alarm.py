"""Non-blocking-ish audible alarm using pygame."""

import threading
import time

try:
    import pygame
except Exception:
    pygame = None


class Alarm:
    def __init__(self, cooldown_seconds=4.0):
        self.cooldown_seconds = cooldown_seconds
        self.last_play = 0.0
        self.lock = threading.Lock()
        self.ready = False

        if pygame is not None:
            try:
                pygame.mixer.init()
                self.ready = True
            except Exception:
                self.ready = False

    def trigger(self):
        now = time.monotonic()
        with self.lock:
            if now - self.last_play < self.cooldown_seconds:
                return False
            self.last_play = now

        if self.ready:
            threading.Thread(target=self._beep, daemon=True).start()
        else:
            self._system_beep()
        return True

    def _beep(self):
        try:
            # Generate a short sine-like tone without an external audio file.
            import numpy as np
            sample_rate = 44100
            duration = 0.35
            frequency = 900
            samples = np.arange(int(sample_rate * duration))
            wave = (0.35 * np.sin(2 * np.pi * frequency * samples / sample_rate))
            audio = (wave * 32767).astype(np.int16)
            stereo = np.column_stack((audio, audio))
            sound = pygame.sndarray.make_sound(stereo)
            sound.play()
            time.sleep(duration)
        except Exception:
            self._system_beep()

    @staticmethod
    def _system_beep():
        try:
            import winsound
            winsound.Beep(1000, 350)
        except Exception:
            print("\a", end="", flush=True)

    def close(self):
        if self.ready and pygame is not None:
            try:
                pygame.mixer.quit()
            except Exception:
                pass
