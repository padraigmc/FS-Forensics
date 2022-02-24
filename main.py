from phase_1 import BinaryFile, FileSystem


if __name__ == '__main__':
	fs = FileSystem(r'C:\repos\FS-Forensics\Sample_1.dd')
	fs.print_partition_information()
