from phase_1 import BinaryFile


class NTFS:
    def __init__(self, file_path, start_sector):
        file = BinaryFile(file_path)

        self.file_path = file_path
        self.start_sector = start_sector
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
        attr_1 = NTFSAttribute(self.file_path, self.mft_byte_address + attr_1_byte)
        self.attributes.append(attr_1)

        # Get attribute 2 info
        attr_2_byte = attr_1_byte + attr_1.length
        attr_2 = NTFSAttribute(self.file_path, self.mft_byte_address + attr_2_byte)
        self.attributes.append(attr_2)

    def print_info(self):
        print('NTFS Volume Information')
        print('-----------------------')

        self.print_bpb_info()
        self.print_attribute_info()

    def print_bpb_info(self):
        print(f'Bytes per Sector = {self.bytes_per_sector}')
        print(f'Sectors per Cluster = {self.sectors_per_cluster}')
        print(f'MFT Sector Address = {self.mft_sector_address}')
        print()

    def print_attribute_info(self):
        for index, attribute in enumerate(self.attributes):
            print(f'Attribute {index}:')
            print(f'Type: {attribute.type} \t Length = {attribute.length}')
            print()


class NTFSAttribute:
    def __init__(self, file_path, start_byte_offset):
        file = BinaryFile(file_path)

        self.start_byte_offset = start_byte_offset

        self.type = file.read(4, self.start_byte_offset, 'd')
        self.length = file.read(4, output_format='d')

    def get_type(self, human_readable=False):
        if not human_readable:
            return self.type

        return 'Attribute type not defined!'

    def get_length(self):
        return self.length
