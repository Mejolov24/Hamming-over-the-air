import audio_encoder
import sounddevice as sd
import time
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
text_input = input("Type Bytes sequence or drag file, then press enter.  ")
if text_input.isdigit() :
    raw_bits = [int(b) for b in text_input]
else:
    raw_bits = audio_encoder.file_to_bits(text_input)

separated_data : dict = audio_encoder.separate_data(raw_bits, BIT_RES)
print("\n")
print("split data  :")
print(separated_data)
print("\n")
print("Encoded packets  :")



input("Press Any key to TX...")



encoded_audio =  audio_encoder.encode_audio_packet(separated_data[0])
sd.play(encoded_audio, audio_encoder.SAMPLE_RATE, device=selected_device)
sd.wait()

input("Press Any key to exit...")