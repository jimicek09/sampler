import os
import datetime
import wave
import threading
import pyaudio
from pynput import keyboard

# Configuration
SAVE_DIR = "recordings"
os.makedirs(SAVE_DIR, exist_ok=True)

# Global variables
frames = []
recording = False
p = pyaudio.PyAudio()


def play_audio(filename):
    """Opens a WAV file and plays it through the default output."""
    print(f"Playing back: {filename}")
    with wave.open(filename, 'rb') as wf:
        # Open a stream for output
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )

        # Read and play data in chunks
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)

        stream.stop_stream()
        stream.close()
    print("Playback finished.")


def record_loop():
    global recording, frames
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100,
                    input=True, frames_per_buffer=3200)
    while recording:
        data = stream.read(3200, exception_on_overflow=False)
        frames.append(data)
    stream.stop_stream()
    stream.close()


def save_and_play():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SAVE_DIR, f"Recording_{timestamp}.wav")

    # 1. Save the file
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b"".join(frames))
    print(f"Saved: {filename}")

    # 2. Play it back instantly in a new thread
    threading.Thread(target=play_audio, args=(filename,), daemon=True).start()


def on_press(key):
    global recording, frames
    if key == keyboard.Key.space:
        if not recording:
            print("Recording started...")
            recording = True
            frames = []
            threading.Thread(target=record_loop, daemon=True).start()
        else:
            print("Recording stopped.")
            recording = False
            # Save and then trigger playback
            save_and_play()

    if key == keyboard.Key.esc:
        return False


print("Controls: [SPACE] Record/Stop | [ESC] Quit")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

p.terminate()



