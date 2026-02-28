import audio_encoder
import sounddevice as sd
import encoder_decoder
import os
sound_data = [] # represented in hz

def encode_audio_packets(packets : bytearray, baud : int = 300, bitres : int = 8, bpt : int = 2, ts : int = 500, hst : int = 350):
    pass
def file_to_bits(filename):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return []

    bits_list = []
    
    # "rb" stands for Read Binary - essential for non-text files
    with open(filename, "rb") as f:
        byte = f.read(1)
        while byte:
            # 1. Convert byte to integer
            byte_val = int.from_bytes(byte, byteorder='big')
            
            # 2. Convert to binary string, padded to 8 characters with zeros
            # '08b' means: 0-padded, 8-characters wide, binary format
            binary_str = format(byte_val, '08b')
            
            # 3. Add each bit as an integer to our list
            for bit in binary_str:
                bits_list.append(int(bit))
                
            byte = f.read(1)
            
    return bits_list


SAMPLE_RATE : int = 44100

devices = sd.query_devices()
for i in range(len(devices)):
    if  int(devices[i]['max_output_channels']) > 0:
        print("ID = " + str(i) + " Device : " + devices[i]['name'] ) 


selected_device = int(input("Output Device ID : "))

BAUDRATE : int = 300 # tones per second
BIT_RES : int = 8 # bit resolution
BPT : int = 2 # bits per tone
TS : int = 500 # tone spacing
EOP : int = 400 # end of packet, used as reference for other tones calculations


raw_bits : bytearray

#tone = audio_encoder.generate_tone_array(500,SAMPLE_RATE)

#sd.play(tone, SAMPLE_RATE, device=selected_device)
#sd.wait()
print("\n")

BAUDRATE = int(input("BaudRate : "))
BIT_RES = int(input("Bit resolution : "))
BPT = int(input("bits per tone : "))
TS = int(input("Tone spacing : "))
EOP = int(input("Base tone : "))
config = audio_encoder.set_data_config(BAUDRATE,BIT_RES,BPT,TS)
print(config)
tones = audio_encoder.calculate_tones(EOP,BIT_RES,BPT,TS)
print("\n")

print("tones : ")
print(tones)

print("\n")
text_input = input("Type Bytes sequence or drag file, then press enter.  ")
if text_input.isdigit() :
    raw_bits = [int(b) for b in text_input]
else:
    raw_bits = file_to_bits(text_input)

separated_data : dict = audio_encoder.separate_data(raw_bits, BIT_RES)
print("\n")
print("split data  :")
print(separated_data)
print("\n")
print("Encoded packets  :")
global data
data = []
for i in range(len(separated_data)):
    # 1. Get the row as a standard Python list
    data_as_bits = separated_data[i].tolist()
    
    # 2. Encode
    result = encoder_decoder.encode_data(data_as_bits, BIT_RES)
    
    # 3. Force the result into standard integers
    clean_result = [int(bit) for bit in result]
    data.append(clean_result)
    
print(data)


input("Press Any key to TX...")

#TODO : TX

input("Press Any key to exit...")









