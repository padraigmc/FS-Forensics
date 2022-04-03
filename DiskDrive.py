from Partition import PartitionFactory
from BinaryFile import BinaryFile


class DiskDrive:
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
			
			partition = PartitionFactory.get_partition(
				self.file_path,
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
			partition.print_info()
			print('')
		
		print(f'Total Number of Valid Partitions: {self.valid_partitions}\n')
