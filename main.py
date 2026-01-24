import pyaudio
import wave
import keyboard

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100

p = pyaudio.PyAudio()

while True:
    recording = False

    if keyboard.is_pressed("space"):
        recording = not recording

    if recording:
        print(recording)
        # stream = p.open(
        #     format=FORMAT,
        #     channels=CHANNEL,
        #     rate=RATE,
        #     input=True,
        #     frames_per_buffer=3200
        # )


