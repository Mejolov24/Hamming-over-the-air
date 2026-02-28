def encode_data(data : bytearray,BitSize : int):
    encoded_data : bytearray
    encoded_data_size : int = 0
    parity_bits_amount : int = 0
    parity_bits_position = []
    
    # calculate data size and parity position:
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
    for p in parity_bits_position: # scroll trough every parity bit
        parity_value = 0
        for i in range(1, encoded_data_size + 1): #scroll trough every data bit until we finish
            if i & p: # check if that specific parity bit matches with our parity bit
                parity_value = parity_value ^ encoded_data[i - 1] # set the parity value to the XOR encoded data value
        encoded_data[p - 1] = parity_value 
    return encoded_data

def decode_data(encoded_data : bytearray,BitSize : int):
    encoded_data_size : int = len(encoded_data)
    parity_bits_amount : int = encoded_data_size - BitSize
    error_position : int = 0
    parity_bits_position = [0] * BitSize
    partially_decoded_data : bytearray = encoded_data
    decoded_data : bytearray = [0] * BitSize
    
    for i in range(parity_bits_amount):
        p = pow(2,i)
        parity_sum = 0
        
        for j in range(1,encoded_data_size + 1 ):
            if j & p:
                parity_sum = parity_sum ^ encoded_data[j - 1]
        if parity_sum != 0:
            error_position += p
    
    if error_position > 0:
        partially_decoded_data[error_position - 1] = 1 - partially_decoded_data[error_position - 1]
        
    for i in range(parity_bits_amount):
        parity_bits_position[i] = pow(2,i)
    
    i2 : int = 0
    for i in range(1, encoded_data_size + 1):
         if i not in parity_bits_position:
             decoded_data[i2] = partially_decoded_data[i - 1]
             i2 += 1

    return decoded_data