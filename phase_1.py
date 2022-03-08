class FileSystem:
	def __init__(self, file_path):
		self.file_path = file_path
		self.valid_partitions = 0
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
			
			if partition.is_valid_partition():
				self.valid_partitions += 1
			
			partitions.append(partition)
		
		file.close()
		
		return partitions

	def print_partition_information(self):
		for index, partition in enumerate(self.partitions):
			print('-------------------')
			print(f'Partition {index}')
			print('-------------------')
			partition.print_attributes()
			print('')
		
		print(f'Total Number of Valid Partitions: {self.valid_partitions}\n')


class Partition:
	def __init__(self, partition_type, start_sector, size):
		self.partition_type = partition_type.upper()
		self.start_sector = start_sector
		self.size = size
	
	def get_partition_type(self):
		if self.partition_type == '00':
			return 'Unknown'
		elif self.partition_type == '01':
			return '12-bit FAT'
		elif self.partition_type == '04':
			return '16-bit FAT'
		elif self.partition_type == '05':
			return 'Extended MS-DOS Partition'
		elif self.partition_type == '06':
			return 'FAT-16'
		elif self.partition_type == '07':
			return 'NTFS'
		elif self.partition_type == '0B':
			return 'FAT-32 (CHS)'
		elif self.partition_type == '0C':
			return 'FAT-32 (LBA)'
		elif self.partition_type == '0E':
			return 'FAT-16 (LBA)'
		else:
			return 'Undefined'
	
	def print_attributes(self):
		s_sector = int(self.start_sector, base=16)
		size = int(self.size, base=16)
		
		print(f'Partition Type = {self.get_partition_type()}')
		print(f'Start Sector = {s_sector} ')
		print(f'Size = {size}')
	
	def is_valid_partition(self):
		if self.partition_type == '00':
			return False
		else:
			return True


class BinaryFile:
	def __init__(self, path):
		self.file = open(path, 'rb')
	
	def seek(self, offset):
		self.file.seek(offset)
	
	def read(self, size, offset=None):
		block = []
		
		# if offset provided, seek
		if offset:
			self.file.seek(offset)
		
		for i in range(size):
			byte = self.file.read(1)
			byte = byte.hex()
			block.append(byte)
		
		block = reversed(block)
		
		return ''.join(block)
	
	def close(self):
		self.file.close()
