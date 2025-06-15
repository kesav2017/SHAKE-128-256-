# Round constants
RC = [
    0x0000000000000001, 0x0000000000008082,
    0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001,
    0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088,
    0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B,
    0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080,
    0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080,
    0x0000000080000001, 0x8000000080008008
]

# Rotation offsets
r = [
    [ 0, 36,  3, 41, 18],
    [ 1, 44, 10, 45,  2],
    [62,  6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39,  8, 14]
]

# Rotate left function
def ROTL(x,r):
	return(((x<<r) | (x>>(64-r)))) & 0xFFFFFFFFFFFFFFFF

# F-Function
def permute(state):
	for round in range(24):
		#Theta phase
		C = [state[i] ^ state[i+5] ^ state[i+10] ^ state[i+15] ^ state[i+20] for i in range(5)]
		D = [C[(i+4)%5] ^ ROTL(C[(i+1)%5],1) for i in range(5)]

		for i in range(5):
			for j in range(5):
				state[i+5*j] ^= D[i]

		#rho and pi phase
		#rho ->  rotates word using rotational constans
		#pi  ->  moves bit to a new position i.e., [(x,y) -> (y%5, (2x + 3y)%5)]
		B = [0]*25
		for i in range(5):
			for j in range(5):
				B[j + 5*((2*i + 3*j)%5)] = ROTL(state[i + 5*j],r[i][j])

		#chi phase
		for i in range(5):
			for j in range(5):
				state[i + 5*j] = B[i + 5*j] ^ (~B[(i+1)%5 + 5*j] & B[(i+2)%5 + 5*j])

		#iota phase
		state[0] ^= RC[round]

def padding(message,rate_byte):
	pad_length = rate_byte - (len(message)%rate_byte)
	if pad_length == 1:
		return message + b'\x9f'
	else:
		return message + b'\x1f' + b'\x00'*(pad_length - 2) + b'\x80'

def SHAKE(message,security_strength,out_len):
	capacity = security_strength*2
	rate = 1600-capacity
	rate_byte = rate // 8
	output_length = out_len // 8

	padded_message = padding(message,rate_byte)
	
	state = [0]*25

	#absorb
	for offset in range(0,len(padded_message),rate_byte):
		block = padded_message[offset:offset + rate_byte]
		for i in range(len(block)//8):
			word = int.from_bytes(block[i*8:(i+1)*8],'little')
			state[i] ^= word
		permute(state)

	#squeeze
	output = b''
	for i in range(output_length // 8):
		output += state[i].to_bytes(8, 'little')

	return output[:output_length].hex()

security_strength = input("Enter the Security Strength(128 or 256): ")
out_len = input("Enter the output Length: ")
security_strength = int(security_strength)
out_len = int(out_len)
message = input("Enter message: ")
msg = message.encode('utf-8')
print("HASH: ", SHAKE(msg,security_strength,out_len))
