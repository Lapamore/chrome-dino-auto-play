from pynput.keyboard import Key, Controller
import time
import threading

class KeyboardController:
    def __init__(self):
        self.controller = Controller()
        self.thread = None
        self.stop_event = threading.Event()

    def _press_key(self, key, hold_duration):
        self.controller.press(key)
        time.sleep(hold_duration)
        self.controller.release(key)

    def start_thread(self, key_sequence):
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._key_sequence_loop, args=(key_sequence,))
            self.thread.start()

    def _key_sequence_loop(self, key_sequence):
        for key, duration in key_sequence:
            if self.stop_event.is_set():
                break
            self._press_key(key, duration)

    def stop_thread(self):
        self.stop_event.set()

    def jump_and_crouch(self, jump_duration=0.3, crouch_duration=0.2):
        key_sequence = [(Key.space, jump_duration), (Key.down, crouch_duration)]
        self.start_thread(key_sequence)
    
    def jump(self, duration=0.3):
        key_sequence = [(Key.space, duration)] 
        self.start_thread(key_sequence)

    def crouch(self, duration=0.4):
        key_sequence = [(Key.down, duration)]
        self.start_thread(key_sequence)