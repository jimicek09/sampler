import os
import datetime
import wave
import threading
from pynput import keyboard
import pyaudio

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SAVE_DIR = "recordings"

os.makedirs(SAVE_DIR, exist_ok=True)

frames = []
recording = False
p = pyaudio.PyAudio()


def record_task():
    global recording, frames
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER
    )

    while recording:
        data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()


def save_file():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SAVE_DIR, f"Recording_{timestamp}.wav")

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

    print(f"Saved: {filename}")


def on_release(key):
    global recording, frames

    if key == keyboard.Key.space:
        if not recording:
            print("Recording started... (Press Space to stop)")
            recording = True
            frames = []
            threading.Thread(target=record_task).start()
        else:
            print("Recording stopped.")
            recording = False
            save_file()
            return False


print("Press SPACE to start/stop recording.")
with keyboard.Listener(on_release=on_release) as listener:
    listener.join()

p.terminate()



