import os
import datetime
import threading
import wave
import pyaudio
import subprocess
import time
from pynput import keyboard

# --- Config ---
SAVE_DIR = "recordings"
os.makedirs(SAVE_DIR, exist_ok=True)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
MIC_INDEX = None

p = pyaudio.PyAudio()

frames = []
recording = False
current_state = 0

def start_recording():
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=MIC_INDEX,
        frames_per_buffer=CHUNK
    )

#dedicating a new thread just for the start recording function
threading.Thread(target=start_recording, daemon=True).start()


def save_and_play():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.abspath(os.path.join(SAVE_DIR, f"Recording_{timestamp}.wav"))

    try:
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
        print(f"Saved: {filename}")

        print("Playing back...")

        start_playback = time.perf_counter()  # Start the timer
        subprocess.run(["aplay", filename])  # This blocks until finished
        end_playback = time.perf_counter()  # End the timer

        duration = end_playback - start_playback
        print(f"Playback time: {duration:.2f} seconds")
        print("Press SPACE one more time to exit.")

    except Exception as e:
        print(f"Error: {e}")


def on_press(key):
    global recording, current_state

    if key == keyboard.Key.space:
        if current_state == 0:
            print("Recording... (Press SPACE to stop)")
            current_state = 1
            recording = True
            frames.clear()

        elif current_state == 1:
            print("Stopping...")
            recording = False
            current_state = 2
            threading.Thread(target=save_and_play, daemon=True).start()

        elif current_state == 2:
            print("Exiting program...")
            return False


print("Sequence: [SPACE] Record -> [SPACE] Playback -> [SPACE] Exit")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

p.terminate()