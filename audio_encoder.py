import audio_encoder
import encoder_decoder
import numpy as np
import itertools
import os
import zlib
import struct

SAMPLE_RATE : int = 44100

#data transfer configuration
BAUDRATE : int = 300 # tones per second
BIT_RES : int = 8 # bit resolution
BPT : int = 2 # bits per tone
TS : int = 500 # tone spacing
RT : int = 0 # refrerence tone
TONES : dict = {} # each tone in hz, stored in a dictionary so we can look up the specific bits for example : [01] = 600  [00] = 650 


METADATA : bytearray = []

# Header configuration
HST : int = 500 # header start tone
HD_BAUD : int = 10
HD_BIT_RES : int = 16
HD_BPT : int = 2
HD_TS : int = 500
HD_RT : int = 600
HD_TONES : dict = {}

# Header structure:
# header tone is sent for 1.2 seconds, in the reciever side its only marked as header if it lasts more than 0.8 seconds, so the tone is free for data
# we send configuration data on a universal and robust way for compatibility that contains this : File metadata(Name,size,checksum) and protocol config 
# we send data in selected configuration
# we send the reference tone, also 0.8 threshold and 1.2 duration
# end of data tone, also 0.8 threshold and 1.2 duration
# 
#





def set_protocol_config(baudrate : int = 300, bitres : int = 8, bpt : int = 2, ts : int = 500,reference_tone : int = 300):
    global BAUDRATE, BIT_RES, BPT, TS, TONES, HD_TONES, RT, HD_RT
    BAUDRATE = baudrate
    BIT_RES = bitres
    BPT = bpt
    TS = ts 
    RT = reference_tone
    HD_TONES = calculate_tones(HD_RT,HD_BPT)
    TONES = calculate_tones(RT,BPT)



def calculate_tones(base_tone,bpt : int ): # here we define the bit tones in relatiion to BPT, TS and BIT_RES
    stored_tones : dict = {}
    combinations = 2**bpt
    combinations = list(itertools.product([0,1], repeat=bpt) )
    for i, combo in enumerate(combinations):
        binary_key = "".join(map(str,combo))
        f_offset = base_tone + (i * TS)
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




def encode_audio_packet(packet : bytearray,baudrate : int = BAUDRATE, bpt : int = BPT,tones : dict = {} ):
    symbol_duration = 1 / baudrate

    chunks = []

    for i in range(0,len(packet),bpt):
        bit_chunk = packet[i : i + bpt]
        bit_str = "".join(map(str,bit_chunk))
        if len(bit_str) < bpt:
            bit_str = bit_str.ljust(bpt, '0')
        freq = tones[bit_str]
        chunks.append(generate_tone_array(freq, SAMPLE_RATE,symbol_duration ))

    encoded_audio = np.concatenate(chunks)
    

    return encoded_audio

def file_to_bits(filepath):
    global METADATA

    filepath = filepath.strip()
    if filepath.startswith("&"):
        filepath = filepath[1:].strip()
    
    # 2. Remove single or double quotes
    filepath = filepath.strip("'").strip('"')

    # 3. Normalize for Windows paths
    filepath = os.path.normpath(filepath)

    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return []
    
    bits_list : bytearray = []

    with open(filepath, "rb") as f:
        data = f.read()  # read entire file at once
        for byte_val in data:
            binary_str = format(byte_val, '08b')
            bits_list.extend(int(bit) for bit in binary_str)
        
    # CRC32
    crc = zlib.crc32(data) & 0xffffffff
    crc_bytes = crc.to_bytes(4, "big")  # 4 bytes
    crc_bits = bytes_to_bits(crc_bytes)

    # File size
    file_size = len(data)
    file_size_bytes = file_size.to_bytes(4, "big")  # 4 bytes
    file_size_bits = bytes_to_bits(file_size_bytes)

    # Filename
    FILENAME_SIZE = 32
    filename = os.path.basename(filepath)
    filename_bytes = filename.encode("utf-8")
    if len(filename_bytes) > FILENAME_SIZE:
        raise ValueError("Filename too long")
    filename_bytes = filename_bytes.ljust(FILENAME_SIZE, b'\x00')
    filename_bits = bytes_to_bits(filename_bytes)

    
    METADATA.extend(crc_bits)
    METADATA.extend(file_size_bits)
    METADATA.extend(filename_bits)
    
            
    return bits_list

def interleave(blocks, depth):
    blocks = np.array(blocks)

    total_blocks = len(blocks)

    # Only interleave in groups of `depth`
    output = []

    for start in range(0, total_blocks, depth):
        group = blocks[start:start+depth]

        # If last group is smaller than depth, just append it unchanged
        if len(group) < depth:
            output.extend(group)
            break

        # Transpose (this is the interleave step)
        transposed = group.T

        # Rebuild blocks row-wise again
        for row in transposed:
            output.append(row)

    return np.array(output)

def int_to_bits(value, bit_count):
    return [(value >> i) & 1 for i in reversed(range(bit_count))]

def bytes_to_bits(data_bytes):
    """Convert a bytes object to a list of bits"""
    bits = []
    for b in data_bytes:
        bits.extend(int_to_bits(b, 8))
    return bits

def create_header():
    configuration = [BAUDRATE,BIT_RES,BPT,TS]
    for i in range(4):
        configuration[i] = int_to_bits(configuration[i],16)
    
    configuration.append(METADATA)

    
    raw_bits = []

    for field in configuration:
        raw_bits.extend(field)
    separated_data = audio_encoder.separate_data(raw_bits, HD_BIT_RES)

    encoded_blocks = []

    for block in separated_data:
        encoded = encoder_decoder.encode_data(block,HD_BIT_RES)
        encoded_blocks.append(encoded)
    
    fused_data = np.concatenate(encoded_blocks)

    interleaved_data = interleave(fused_data,16)

    return interleaved_data








def encode_file_to_audio(filepath : bytearray):
    raw_bits = audio_encoder.file_to_bits(filepath)
    separated_data = audio_encoder.separate_data(raw_bits, BIT_RES)

    encoded_blocks = []

    for block in separated_data:
        encoded = encoder_decoder.encode_data(block,BIT_RES)
        encoded_blocks.append(encoded)
    
    fused_data = np.concatenate(encoded_blocks)

    interleaved_data = interleave(fused_data,16)

    header_start_tone = generate_tone_array(HST,SAMPLE_RATE,1.2)
    header_audio = encode_audio_packet(create_header(),HD_BAUD,HD_BPT,HD_TONES)
    reference_tone = generate_tone_array(HST,SAMPLE_RATE,1.2)
    data_audio = encode_audio_packet(interleaved_data,BAUDRATE,BPT,TONES)
    final_audio = np.concatenate([header_start_tone, header_audio, reference_tone , data_audio])

    return final_audio

import numpy as np

CURRENT_PHASE = 0.0

def generate_tone_array(hz: int, sample_rate: int, duration_sec: float):
    global CURRENT_PHASE
    
    num_samples = int(sample_rate * duration_sec)
    if num_samples <= 0:
        return np.array([], dtype=np.float32)
    
    # 1. Calculate phase steps
    phase_step = 2 * np.pi * hz / sample_rate
    indices = np.arange(num_samples)
    
    # 2. Generate phases starting from the global offset
    phases = CURRENT_PHASE + (indices * phase_step)
    tone = 0.5 * np.sin(phases)
    
    # 3. Smooth the transitions (Windowing)
    # Applying a tiny 1-2ms fade at the start and end of every symbol
    # This prevents the "slope change" click.
    if num_samples > 200: # only if the symbol is long enough
        fade_len = int(sample_rate * 0.002) # 2ms fade
        fade_in = np.linspace(0, 1, fade_len)
        fade_out = np.linspace(1, 0, fade_len)
        
        tone[:fade_len] *= fade_in
        tone[-fade_len:] *= fade_out

    # 4. Update the global variable for the next call
    CURRENT_PHASE = (phases[-1] + phase_step) % (2 * np.pi)
    
    return tone.astype(np.float32)






