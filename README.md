# Hamming over the air
protocol to transefer digital data of any type using Highly CPFSK modulation and SEC-DED error correction, specifically designed to be used in ham radio.

## Protocol information :

CPFSK stands for:
Continous Phase Frequency Shift Keying.

Since this is a highly customizable protocol, We send a Header that determines these important settings:

### Header : 

We send at a standard predefined tone and tonemap (customizable but not recomended to keep standardization) wich marks its start, then we send all the configuration data into a single fixed length [TODO : HD_BITSIZE] Bit packet, after that, customizable header data can be added but it needs to be interpreted by the reciever in a custom way that has yet to be implemented, fork it if you need.

#### Configuration data:

Baudrate (speed of comunication
Bit resolution (How many bits we send each packet)
Bits per tone (How many bits are packed into a tone)
Tone spacing (spacing btween tones)
End of packet tone (EOP)

### EOP

used for determining the end and start of a packet.

The end of packet tone is Highly important because its used for calculating the tonemap for the bits, its a reference point, allowing the receiver to get active feedback onto the frecuencies, making things like doppler shift or incorrect tuning less unlikely to interfiere.

### ToneMap:

Dictionary that assings bit combinations to a specific tone wich is calculated by the EOP plus the BPT (Bits per tone)

