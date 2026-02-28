import numpy as np
import itertools



#data transfer configuration
BAUDRATE : int = 300 # tones per second
BIT_RES : int = 8 # bit resolution
BPT : int = 2 # bits per tone
TS : int = 500 # tone spacing
TONES : dict # each tone in hz, stored in a dictionary so we can look up the specific bits for example : [01] = 600  [00] = 650 

# Header configuration
HST : int = 350 # header start tone
HD_BAUD : int = 300
HD_BIT_RES : int = 8
HD_BPT : int = 2
HD_TS : int = 500
HD_TONES : dict






def set_header_config(baud : int = 300, bitres : int = 8, bpt : int = 2, ts : int = 500, hst : int = 350):
    HD_BAUD = baud
    HD_BIT_RES = bitres
    HD_BPT = bpt
    HD_TS = ts 
    HST = hst

def set_data_config(baud : int = 300, bitres : int = 8, bpt : int = 2, ts : int = 500):
    BAUDRATE = baud
    BIT_RES = bitres
    BPT = bpt
    TS = ts 
    configuration = [BAUDRATE,BIT_RES,BPT,TS]
    for i in range(4):
        configuration[i] = format(configuration[i] & 0xFFFF, '016b')
    return configuration


def calculate_tones(eop : int,bits : int , bits_per_tone : int, interval : int): # here we define the bit tones in relatiion to BPT, TS and BIT_RES
    stored_tones : dict = {}
    combinations = 2**bits_per_tone
    combinations = list(itertools.product([0,1], repeat=bits_per_tone) )
    stored_tones["EOP"] = eop
    stored_tones["EOD"] = eop * 2
    for i, combo in enumerate(combinations):
        binary_key = "".join(map(str,combo))
        f_offset = ((i + 3) * interval)
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

def generate_tone_array(hz : int,sample_rate):
    t = np.linspace(0, 1, sample_rate)
    return  0.5 * np.sin(2 * np.pi * hz * t)






