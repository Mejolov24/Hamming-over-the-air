import encoder_decoder

text_input = input("Type Bytes sequence: ")
bits = [int(b) for b in text_input]
bit_size = int(input("Type ByteSize: "))
data = bytearray(bits)


result = encoder_decoder.decode_data(data, bit_size)

print("Parity Decoded Bytearray  :")
print(list(result))