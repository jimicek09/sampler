import pyaudio

p = pyaudio.PyAudio()

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if "pulse" in info['name'].lower() and info['maxInputChannels'] > 0:
        print(i, info['name'], info['maxInputChannels'])