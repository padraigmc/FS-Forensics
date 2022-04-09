import codecs

from BinaryFile import BinaryFile


class PartitionFactory:
    @staticmethod
    def get_partition(file_path, partition_type, start_sector, size):
        if partition_type == '07':
            return NTFS(file_path, start_sector, partition_type, size)
        elif partition_type == '06':
            return FAT(file_path, start_sector, partition_type, size)
        else:
            return Partition(file_path, partition_type, start_sector, size)


class Partition:
    def __init__(self, file_path, partition_type, start_sector, size):
        self.file_path = file_path
        self.partition_type = partition_type.upper()
        self.start_sector = int(start_sector, base=16)
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
        elif self.partition_type == '43':
            return 'Old Linux Native '
        elif self.partition_type == '83':
            return 'Linux Native '
        elif self.partition_type == '85':
            return 'Linux Extended '
        else:
            return 'Undefined'

    def get_file_obj(self):
        return BinaryFile(self.file_path)

    def print_info(self):
        size = int(self.size, base=16)

        print(f'Partition Type = {self.get_partition_type()}')
        print(f'Start Sector = {self.start_sector} ')
        print(f'Size (sectors) = {size}')

    def is_valid_partition(self):
        if self.partition_type == '00':
            return False
        else:
            return True


class NTFS(Partition):
    def __init__(self, file_path, start_sector, partition_type, size):
        super().__init__(file_path, partition_type, start_sector, size)
        file = self.get_file_obj()

        self.file_path = file_path
        self.start_sector = int(start_sector, base=16)
        self.start_byte = self.start_sector * 512

        # seek to start of BPB
        file.seek(self.start_byte + int('B', 16))

        # store BPB info
        self.bytes_per_sector = file.read(2, output_format='d')
        self.sectors_per_cluster = file.read(1, output_format='d')
        self.mft_logical_cluster_num = file.read(8, self.start_byte + int('30', 16), output_format='d')
        self.mft_sector_address = self.start_sector + (self.mft_logical_cluster_num * self.sectors_per_cluster)
        self.mft_byte_address = self.mft_sector_address * self.bytes_per_sector

        self.attributes = []

        # Get attribute 1 info
        attr_1_byte = file.read(2, self.mft_byte_address + int('14', 16), 'd')
        attr_1 = NTFSAttribute(file, self.mft_byte_address + attr_1_byte)
        self.attributes.append(attr_1)

        # Get attribute 2 info
        attr_2_byte = attr_1_byte + attr_1.length
        attr_2 = NTFSAttribute(file, self.mft_byte_address + attr_2_byte)
        self.attributes.append(attr_2)

        file.close()

    def print_info(self):
        print('NTFS Volume Information')
        print('-----------------------')
        size = int(self.size, base=16)

        print(f'Partition Type = {self.get_partition_type()}')
        print(f'Start Sector = {self.start_sector} ')
        print(f'Size (sectors) = {size}')

        self.print_bpb_info()
        self.print_attribute_info()

    def print_bpb_info(self):
        print(f'Bytes per Sector = {self.bytes_per_sector}')
        print(f'Sectors per Cluster = {self.sectors_per_cluster}')
        print(f'MFT Sector Address = {self.mft_sector_address}')
        print()

    def print_attribute_info(self):
        for index, attribute in enumerate(self.attributes):
            print(f'Attribute {index}')
            print('------------------------')
            print(f'Type: {attribute.get_type(True)} ({attribute.get_type()})')
            print(f'Length = {attribute.length}')
            print()


class NTFSAttribute:
    def __init__(self, file: BinaryFile, start_byte_offset):
        self.start_byte_offset = start_byte_offset

        self.type = file.read(4, self.start_byte_offset, 'd')
        self.length = file.read(4, output_format='d')

    def get_type(self, human_readable=False):
        if not human_readable:
            return self.type

        if self.type == 16:
            return "$STANDARD_INFORMATION"
        elif self.type == 32:
            return "$ATTRIBUTE_LIST"
        if self.type == 48:
            return "$FILE_NAME"
        elif self.type == 64:
            return "$OBJECT_ID"
        elif self.type == 80:
            return "$SECURITY_DESCRIPTOR"
        elif self.type == 128:
            return "$DATA"
        elif self.type == 144:
            return "$INDEX_ROOT"
        elif self.type == 160:
            return "$INDEX_ALLOCATION"
        elif self.type == 256:
            return "$LOGGED_UTILITY_STREAM "
        else:
            return 'Attribute type not defined!'

    def get_length(self):
        return self.length


class FAT(Partition):
    def __init__(self, file_path, start_sector, partition_type, size):
        super().__init__(file_path, partition_type, start_sector, size)
        file = self.get_file_obj()

        self.file_path = file_path
        self.start_sector = int(start_sector, base=16)
        self.start_byte = self.start_sector * 512

        # seek to start of BPB
        file.seek(self.start_byte + int('B', 16))

        # store BPB info
        self.bytes_per_sector = file.read(2, output_format='d') # 0hb
        self.sectors_per_cluster = file.read(1, output_format='d') # 0hd
        self.size_reserved_area = file.read(2, output_format='d') # 0he
        self.num_fat_copies = file.read(1, output_format='d') # 0h10
        self.max_dir_entries = file.read(2, output_format='d') # 0h11
        self.size_of_each_fat = file.read(2, self.start_byte + int('16', 16), output_format='d') # 0h16

        self.total_fat_size = self.num_fat_copies * self.size_of_each_fat
        self.root_dir_size = int((self.max_dir_entries * 32) / self.bytes_per_sector)
        self.data_area_addr = 63 + self.size_reserved_area + self.total_fat_size
        self.cluster_2_addr = self.data_area_addr + self.root_dir_size

        file.close()

        self.deleted_files = self.get_deleted_files_offsets()

    def get_deleted_files_offsets(self):
        deleted_files = []
        file = self.get_file_obj()

        for offset in range(0, self.root_dir_size * self.bytes_per_sector, 32):
            dir_entry_offset = (self.data_area_addr * self.bytes_per_sector) + offset
            filename = file.read(11, dir_entry_offset, output_format='h', big_endian=False).upper()

            if filename[:2] == 'E5': # if deleted
                filename_ansi = BinaryFile.decode_ansi(filename)
                starting_cluster = file.read(2, dir_entry_offset + 26, output_format='d') # 0h1A
                filesize = file.read(4, output_format='d')

                offset_file_content = (self.cluster_2_addr + ((starting_cluster - 2) * self.sectors_per_cluster)) * self.bytes_per_sector

                initial_content = file.read(16, offset_file_content, big_endian=False)
                initial_content_ansi = '"' + BinaryFile.decode_ansi(initial_content) + '"'

                # add deleted file obj to list
                deleted_files.append(
                    DeletedFatFile(filename_ansi, starting_cluster, filesize, initial_content_ansi)
                )

        return deleted_files

    def print_info(self):
        print('FAT-16 Volume Information')
        print('-----------------------')
        size = int(self.size, base=16)

        print(f'Partition Type = {self.get_partition_type()}')
        print(f'Start Sector = {self.start_sector} ')
        print(f'Size (sectors) = {size}')

        print(f'Num Sectors per Cluster = {self.sectors_per_cluster}')
        print(f'Size of FAT Area (sectors) = {self.total_fat_size}')
        print(f'Size of Root Directory = {self.root_dir_size}')
        print(f'Sector Address of Cluster #2 = {self.cluster_2_addr}')
        print()

        print('Deleted Files')
        print('-----------------')
        for file in self.deleted_files:
            file.print_info()


class DeletedFatFile:
    def __init__(self, filename, starting_cluster, filesize, partial_file_content):
        self.filename = filename
        self.starting_cluster = starting_cluster
        self.filesize = filesize
        self.partial_file_content = partial_file_content

    def print_info(self):
        print(f'Filename = {self.filename}')
        print(f'Starting Cluster = {self.starting_cluster}')
        print(f'Filesize (bytes) = {self.filesize}')
        print(f'Content (first 16 characters) = \n{self.partial_file_content}')

