import sys
import os
import sys
sys.stderr = open(os.devnull, 'w')
import wave
from pynput import keyboard
import pyaudio


FRAMES_PER_BUFFER = 3200
FORMAT = None
CHANNEL = 1
RATE = 44100

recording = False
stream = None
p = None

def on_press(key):
    global recording, p, stream
    if key == keyboard.Key.space:
        recording = not recording
        if recording:
            global FORMAT
            FORMAT = pyaudio.paInt16

            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNEL,
                rate=RATE,
                input=True,
                frames_per_buffer=FRAMES_PER_BUFFER
            )

            print("Recording:", recording)

            frames = []
            for i in range(0, int(RATE/FRAMES_PER_BUFFER * seconds)):
        else:
            print("Recording:", recording)
            stream.stop_stream()
            stream.close()
            stream = None
            p.terminate()
            p = None





with keyboard.Listener(on_press=on_press) as listener:
    listener.join()



