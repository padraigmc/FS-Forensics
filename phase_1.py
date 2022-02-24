class FileSystem:
	def __init__(self, file_path):
		self.file_path = file_path
		self.partitions = self.read_partitions()

	def read_partitions(self):
		partitions = []
		mbr_start = int('1BE', base=16)
		entry_offset = 16

		file = BinaryFile(self.file_path)
		file.seek(mbr_start)

		for i in range(0, 4):
			file.seek(mbr_start + (i * entry_offset))

			# read information from MBR entry
			bootable_partition = file.read(1)
			start_chs = file.read(3)
			partition_type = file.read(1)
			end_chs = file.read(3)
			start_lba = file.read(4)
			partition_size = file.read(4)

			partition = Partition(
				partition_type,
				start_lba,
				partition_size
			)

			partitions.append(partition)

		return partitions

	def print_partition_information(self):
		for index, partition in enumerate(self.partitions):
			print('-------------------')
			print(f'Partition {index}')
			print('-------------------')
			partition.print_attributes()
			print('')


class Partition:
	def __init__(self, partition_type, start_sector, size):
		self.partition_type = partition_type
		self.start_sector = start_sector
		self.size = size

	def print_attributes(self):
		s_sector = int(self.start_sector, base=16)
		size = int(self.size, base=16)

		print(f'Partition Type = {self.partition_type}')
		print(f'Start Sector = {s_sector} ')
		print(f'Size = {size}')


class BinaryFile:
	def __init__(self, path):
		self.file = open(path, 'rb')

	def seek(self, offset):
		self.file.seek(offset)

	def read(self, size, offset=None):
		block = []

		# if offset provided, seek
		if offset:
			print(f'offset = {offset}')
			self.file.seek(offset)
			print(self.file.read(1))

		for i in range(size):
			byte = self.file.read(1)
			byte = byte.hex()
			block.append(byte)

		block = reversed(block)

		return ''.join(block)

	def close(self):
		self.file.close()
