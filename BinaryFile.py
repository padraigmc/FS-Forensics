import codecs


class BinaryFile:
	def __init__(self, path):
		self.file = open(path, 'rb')

	def seek(self, offset):
		self.file.seek(offset)

	def read(self, size, offset=None, output_format='h', big_endian=True):
		block = []

		# if offset provided, seek
		if offset:
			self.file.seek(offset)

		for i in range(size):
			byte = self.file.read(1)
			byte = byte.hex()
			block.append(byte)

		# reverse block for little endian translation and convert to string
		if big_endian:
			block = reversed(block)

		# convert array to string
		block = ''.join(block)

		# if dec_output flag set, convert to decimal int
		if output_format == 'd':
			return int(block, 16)
		else:  # output_format == 'h'
			return block

	def close(self):
		self.file.close()

	@staticmethod
	def decode_ansi(text):
		return str(codecs.decode(text, "hex"), 'ansi')
