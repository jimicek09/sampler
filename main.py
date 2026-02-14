import os
import datetime
import wave
import threading
import pyaudio
from pynput import keyboard
import time
import simpleaudio as sa

start = time.time()
end = None

SAVE_DIR = "recordings"
os.makedirs(SAVE_DIR, exist_ok=True)
pressCount = 0

frames = []
recording = False
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=3200)

stream.start_stream()

def playAudio(filename):
    global start
    try:
        print(f"Playing: {filename}")
        wave_obj = sa.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        length = (time.time() - start) * 1000
        print("Playback finished.")
        print(f"Playback latency: {length:.2f} ms")
    except FileNotFoundError:
        print("Error: 'aplay' not found. Try 'sudo apt install alsa-utils'")


def recordLoop():
    global recording, frames
    try:
        while recording:
            data = stream.read(3200, exception_on_overflow=False)
            frames.append(data)
    except Exception as e:
        print(f"Recording Error: {e}")


def saveAndPlay():
    global frames
    if not frames: return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.abspath(os.path.join(SAVE_DIR, f"Recording_{timestamp}.wav"))

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b"".join(frames))

    print(f"Saved: {filename}")
    # Play in background
    threading.Thread(target=playAudio, args=(filename,), daemon=True).start()


def onPress(key):
    global recording, start, pressCount
    if key == keyboard.Key.space:

        pressCount += 1

        if pressCount == 1:
            print("Recording...")
            recording = True
            frames.clear()
            threading.Thread(target=recordLoop, daemon=True).start()
        elif pressCount == 2:
            print("Stopping...")
            recording = False
            start = time.time()
            saveAndPlay()
        elif pressCount == 3:
            latency = (time.time() - start) * 1000
            print(f"it took the program circa {latency:.2f}ms to playback")
            return False

    if key == keyboard.Key.esc:
        return False


print("Controls: [SPACE] Record/Stop | [ESC] Quit")
with keyboard.Listener(on_press=onPress) as listener:
    listener.join()

stream.stop_stream()
stream.close()
p.terminate()



