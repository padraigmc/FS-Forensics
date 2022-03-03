from phase_1 import BinaryFile


class NTFS:
    def __init__(self, file: BinaryFile, start_sector):
        self.start_sector = start_sector
        self.start_byte = self.start_sector * 512

        self.bytes_per_sector = None
        self.sectors_per_cluster = None
        self.mft_logical_cluster_num = None
        self.mft_sector_offset = None

        self.attributes = []

        self.get_bpb_info(file)

    def get_bpb_info(self, file: BinaryFile):
        self.bytes_per_sector = file.read(2, self.start_byte + int('B', 16), output_format='d')
        self.sectors_per_cluster = file.read(1, output_format='d')
        self.mft_logical_cluster_num = file.read(8, self.start_byte + int('30', 16), output_format='d')
        self.mft_sector_offset = self.mft_logical_cluster_num * self.sectors_per_cluster

        print(f'Bytes per sector = {self.bytes_per_sector}')
        print(f'Sectors per cluster = {self.sectors_per_cluster}')
        print(f'MFT Logical Cluster Number = {self.mft_logical_cluster_num}')
        print(f'MFT Cluster Offset = {self.mft_sector_offset}')

        mft_start_byte = self.start_byte + (self.mft_sector_offset * self.bytes_per_sector)
