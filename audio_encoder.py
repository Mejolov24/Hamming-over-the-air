import audio_encoder
import encoder_decoder
import numpy as np
import itertools
import os

SAMPLE_RATE : int = 44100

#data transfer configuration
BITRATE : int = 300 # tones per second
BIT_RES : int = 8 # bit resolution
BPT : int = 2 # bits per tone
TS : int = 500 # tone spacing
TONES : dict = {} # each tone in hz, stored in a dictionary so we can look up the specific bits for example : [01] = 600  [00] = 650 

# Header configuration
HST : int = 350 # header start tone
HD_BAUD : int = 300
HD_BIT_RES : int = 8
HD_BPT : int = 2
HD_TS : int = 500
HD_TONES : dict






def set_header_config(bitrate : int = 300, bitres : int = 8, bpt : int = 2, ts : int = 500, hst : int = 350):
    HD_BAUD = bitrate
    HD_BIT_RES = bitres
    HD_BPT = bpt
    HD_TS = ts 
    HST = hst

def set_data_config(bitrate : int = 300, bitres : int = 8, bpt : int = 2, ts : int = 500,eop : int = 500):
    global BITRATE, BIT_RES, BPT, TS, TONES
    BITRATE = bitrate
    BIT_RES = bitres
    BPT = bpt
    TS = ts 
    TONES = calculate_tones(eop)
    configuration = [BITRATE,BIT_RES,BPT,TS]
    for i in range(4):
        configuration[i] = format(configuration[i] & 0xFFFF, '016b')
    return configuration


def calculate_tones(base_tone): # here we define the bit tones in relatiion to BPT, TS and BIT_RES
    stored_tones : dict = {}
    combinations = 2**BPT
    combinations = list(itertools.product([0,1], repeat=BPT) )
    stored_tones["EOP"] = base_tone
    stored_tones["EOD"] = base_tone * 2
    for i, combo in enumerate(combinations):
        binary_key = "".join(map(str,combo))
        f_offset = base_tone + ((i + 3) * TS)
        stored_tones[binary_key] = f_offset
    return stored_tones



def separate_data(data : bytearray ,chunk_size):
    data = np.array(data)
    # calculate missing space
    padding_needed = (chunk_size - (len(data) % chunk_size)) % chunk_size

    if padding_needed > 0:
        # Append the zeros to the end of the array
        data = np.concatenate([data, np.zeros(padding_needed, dtype=int)])

    # Reshape into BiteSize
    packets = data.reshape(-1, chunk_size)
    return packets




def encode_audio_packet(packet : bytearray):
    packet = encoder_decoder.encode_data(packet,BIT_RES)
    baud_rate = BITRATE / BPT
    symbol_duration = 1 / baud_rate

    encoder = SineGenerator()
    chunks = []

    for i in range(0,len(packet),BPT):
        bit_chunk = packet[i : i + BPT]
        bit_str = "".join(map(str,bit_chunk))
        if len(bit_str) < BPT:
            bit_str = bit_str.ljust(BPT, '0')
        freq = TONES[bit_str]
        chunks.append(encoder.generate_tone_array(freq, SAMPLE_RATE,symbol_duration ))

    chunks.append(encoder.generate_tone_array(TONES["EOP"] , SAMPLE_RATE, symbol_duration ))
    encoded_audio = np.concatenate(chunks)
    

    return encoded_audio

def file_to_bits(filename):

    filename = filename.strip()
    if filename.startswith("&"):
        filename = filename[1:].strip()
    
    # 2. Remove single or double quotes
    filename = filename.strip("'").strip('"')

    # 3. Normalize for Windows paths
    filename = os.path.normpath(filename)

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

def encode_file_to_audio(filepath : bytearray):
    raw_bits = audio_encoder.file_to_bits(filepath)
    separated_data = audio_encoder.separate_data(raw_bits, BIT_RES)
    data = []
    for packet in separated_data:
        encoded_audio =  audio_encoder.encode_audio_packet(packet)
        data.append(encoded_audio)
    data = np.concatenate(data)
    return data

class SineGenerator:
    def __init__(self):
        self.current_phase = 0.0

    def generate_tone_array(self, hz: int, sample_rate: int, duration_ms: int = 100):
        duration_sec = duration_ms #/ 1000.0
        num_samples = int(sample_rate * duration_sec)
        
        # 1. Calculate how much the phase moves per sample for this frequency
        # Phase increment = 2 * pi * frequency / sample_rate
        phase_step = 2 * np.pi * hz / sample_rate
        
        # 2. Create an array of phase steps
        phases = self.current_phase + np.arange(num_samples) * phase_step
        
        # 3. Generate the sine wave
        tone = 0.5 * np.sin(phases)
        
        # 4. Update the stored phase for the NEXT chunk
        # We use modulo 2*pi to keep the number from growing toward infinity
        self.current_phase = (phases[-1] + phase_step) % (2 * np.pi)
        
        return tone.astype(np.float32)






