import pyaudio
import wave
from pynput import keyboard

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100

p = pyaudio.PyAudio()
recording = False

def on_press(key):
    global recording
    if key == keyboard.Key.space:
        recording = not recording
        print("Recording:", recording)
        stream = p.open(
            format = FORMAT,
            channels = CHANNEL,
            rate = RATE,
            input = True,
            frames_per_buffer = 3200
        )


with keyboard.Listener(on_press=on_press) as listener:
    listener.join()



