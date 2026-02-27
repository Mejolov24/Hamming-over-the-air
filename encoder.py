
# Creation of arrays:
#Creation of encoded array size:
def encode_data(data : bytearray,BitSize : int):
    encoded_data : bytearray
    encoded_data_size : int = 0
    parity_bits_amount : int = 0
    parity_bits_position = []

    while pow(2,parity_bits_amount) < BitSize + parity_bits_amount + 1 :
        parity_bits_amount += 1
        encoded_data_size = BitSize + parity_bits_amount

    encoded_data = [0] * encoded_data_size
    parity_bits_position = [0] * parity_bits_amount

    # calculate parity bits location:
    for i in range(parity_bits_amount):
        parity_bits_position[i] = pow(2,i)
    
    # add data in spaces that arent occupied by future parity bits, parity calculation requires to start a index 1.
    i2 : int = 0
    for i in range(1,encoded_data_size + 1):
        if i not in parity_bits_position:
            encoded_data[i - 1] = data[i2]
            i2 += 1
    
    # calculate and add parity bits
    for p in parity_bits_position:
        parity_value = 0
        for i in range(1, encoded_data_size + 1):
            if i & p:
                parity_value = parity_value ^ encoded_data[i - 1]
        encoded_data[p - 1] = parity_value
    return encoded_data