from phase_1 import FileSystem
from NTFS import NTFS


if __name__ == '__main__':
	fs = FileSystem(r'D:\repos\Sample_1.dd')
	fs.print_partition_information()

	ntfs = NTFS(r'D:\repos\Sample_1.dd', 1606500)
	ntfs.print_info()
