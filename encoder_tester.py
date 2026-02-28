import encoder_decoder

text_input = input("Type Bytes sequence: ")

bits = [int(b) for b in text_input]
data = bytearray(bits)

bit_size = len(data)

print(f"\n--- Using {bit_size} As bit size ---")
result = encoder_decoder.encode_data(data, bit_size)

print("Parity Encoded Bytearray  :")
print(list(result))