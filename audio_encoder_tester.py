import audio_encoder
import sounddevice as sd
import time
import numpy as np
devices = sd.query_devices()
for i in range(len(devices)):
    if  int(devices[i]['max_output_channels']) > 0:
        print("ID = " + str(i) + " Device : " + devices[i]['name'] ) 

selected_device = int(input("Output Device ID : "))

print("\n")


raw_bits : bytearray

BAUDRATE : int = 300 # tones per second
BIT_RES : int = 8 # bit resolution
BPT : int = 2 # bits per tone
TS : int = 500 # tone spacing
EOP : int = 400 # end of packet, used as reference for other tones calculations

BAUDRATE = int(input("BitRate : "))
BIT_RES = int(input("Bit resolution : "))
BPT = int(input("bits per tone : "))
TS = int(input("Tone spacing : "))
EOP = int(input("Base tone : "))
config = audio_encoder.set_data_config(BAUDRATE,BIT_RES,BPT,TS,EOP)
print(config)
print("\n")

print("tones : ")
print(audio_encoder.TONES)

print("\n")

text_input = input("Drag a file, then press enter.  ")
data = audio_encoder.encode_file_to_audio(text_input)

print("\n")
input("Press Any key to TX...")




sd.play(data, audio_encoder.SAMPLE_RATE, device=selected_device)
sd.wait()

input("Press Any key to exit...")