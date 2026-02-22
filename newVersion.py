import os
import datetime
import threading
import wave
import pyaudio
import subprocess
import shutil
import sys
import time
from pynput import keyboard
import numpy as np
import sounddevice as sd
import mido

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
recording = True
current_state = 0
stream = None
initializedTime = -1
stop_playback = threading.Event()
playback_thread = None

def start_recording():
    global stream, recording, initializedTime

    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=MIC_INDEX,
            frames_per_buffer=CHUNK
        )

        initializedTime = time.time()
        print("Sequence: [SPACE] Record -> [SPACE] Playback -> [SPACE] Exit")

        while recording:
            try:
                data = stream.read(CHUNK)
            except Exception:
                # Some PyAudio builds don't accept exception_on_overflow kwarg
                # and may raise on overflow — append silence as a fallback.
                data = b"\x00" * (CHUNK * 2 * CHANNELS)
            frames.append(data)

        stream.stop_stream()
        stream.close()
    except Exception as e:
        print(f"Recording Error: {e}")
        recording = False

#dedicating a new thread just for the start recording function
threading.Thread(target=start_recording, daemon=True).start()


def save_and_play():
    filename = os.path.abspath(os.path.join(SAVE_DIR, f"sample1.wav"))
    if os.path.exists(filename):
        os.remove(filename)

    try:
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
        print(f"Saved: {filename}")

        print("Playing back...")

        stop_playback.clear()
        data = b"".join(frames)
        if not data:
            print("No audio to play.")
            return

        # convert raw bytes to numpy int16 array for sounddevice
        audio = np.frombuffer(data, dtype=np.int16)
        if CHANNELS > 1:
            audio = audio.reshape(-1, CHANNELS)

        start_playback = time.perf_counter()

        # gapless looping via callback
        idx = 0
        total_frames = len(audio) if CHANNELS == 1 else audio.shape[0]

        def callback(outdata, frames_count, time_info, status):
            nonlocal idx
            if stop_playback.is_set():
                raise sd.CallbackStop()
            end = idx + frames_count
            if end <= total_frames:
                chunk = audio[idx:end]
            else:
                # wrap-around to achieve seamless loop
                first = audio[idx:total_frames]
                second = audio[0:(end % total_frames)]
                chunk = np.concatenate((first, second), axis=0)
            idx = end % total_frames
            # ensure correct shape for stereo/mono
            if CHANNELS == 1:
                outdata[:] = chunk.reshape(-1, 1)
            else:
                outdata[:] = chunk

        with sd.OutputStream(
            samplerate=RATE,
            channels=CHANNELS,
            blocksize=CHUNK,
            dtype='int16',
            callback=callback
        ):
            # keep running until stop_playback is set
            while not stop_playback.is_set():
                time.sleep(0.1)

        end_playback = time.perf_counter()
        duration = end_playback - start_playback
        print(f"Playback time: {duration:.2f} seconds")
        print("Press SPACE one more time to exit.")

    except Exception as e:
        print(f"Error: {e}")

def on_press(key):
    pass

def midi_listener():
    global recording, current_state, startTime, playback_thread

    ports = mido.get_input_names()
    port_name = None
    for p_name in ports:
        if "FBV Express Mk II" in p_name:
            port_name = p_name
            break
    if port_name is None:
        port_name = ports[0] if ports else None
    if port_name is None:
        print("No MIDI input ports found. Install 'mido' and an RTMIDI backend, or connect your device.")
        return

    print(f"Using MIDI input: {port_name}")
    with mido.open_input(port_name) as inport:
        for msg in inport:
            # CC 16 on MIDI channel 1 (mido channels are 0-based)
            if msg.type == 'control_change' and msg.control == 16 and msg.channel == 0:
                val = msg.value
                # press (127): start recording (if idle) or exit (if in playback)
                if val == 127:
                    if current_state == 0 and initializedTime != -1:
                        print("Recording... (hold switch to record)")
                        startTime = time.time()
                        current_state = 1
                        frames.clear()
                    elif current_state == 2:
                        print("Exiting program...")
                        stop_playback.set()
                        if playback_thread is not None and playback_thread.is_alive():
                            playback_thread.join(timeout=5)
                        return
                # release (0): stop recording and start playback
                elif val == 0:
                    if current_state == 1:
                        print("Stopping...")
                        recording = False
                        # delete_excess(startTime)
                        current_state = 2
                        playback_thread = threading.Thread(target=save_and_play)
                        playback_thread.start()

# listen for MIDI CC16 from FBV Express Mk II (blocks until exit)
midi_listener()
 
 # ensure playback thread finished before terminating PyAudio
if playback_thread is not None and playback_thread.is_alive():
     stop_playback.set()
     playback_thread.join(timeout=5)
 
p.terminate()
