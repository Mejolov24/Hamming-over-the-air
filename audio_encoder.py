import sounddevice as sd
import numpy as np


SAMPLE_RATE = 44100
TONES = {
    "00": 1000,
    "01": 1400,
    "10": 1800,
    "11": 2200
}

def tone(hz : int):
    fs = SAMPLE_RATE
    t = np.linspace(0, 1, fs)
    tone = 0.5 * np.sin(2 * np.pi * hz * t)

    sd.play(tone, samplerate=fs, device=selected_device)
    sd.wait()

def encode_audio(data : bytearray ,chunk_size):
    # calculate missing space
    padding_needed = (chunk_size - (len(data) % chunk_size)) % chunk_size

    if padding_needed > 0:
        # Append the zeros to the end of the array
        data = np.concatenate([data, np.zeros(padding_needed, dtype=int)])

    # Reshape into BiteSize
    packets = data.reshape(-1, chunk_size)
    print(packets)




devices = sd.query_devices()
for i in range(len(devices)):
    if  int(devices[i]['max_output_channels']) > 0:
        print("ID = " + str(i) + " Device : " + devices[i]['name'] ) 


selected_device = int(input("Output Device ID : "))

BAUDRATE = int(input("Baudrate : "))
BITSIZE = int(input("BitSize : "))
BIT_DURATION = 1.0 / BAUDRATE
encode_audio(np.array([0] * 32),BITSIZE)

tone(500)
tone(600)


