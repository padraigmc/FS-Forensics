from DiskDrive import DiskDrive
import sys


def main():
    # get filepath from arguments list
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        #file_path = r'C:\repos\FS-Forensics\Sample_1.dd'
        file_path = r'D:\repos\ET4027\FS-Forensics\Sample_1.dd'

        #file_path = r'D:\repos\ET4027\AssignmentDrive\et4027.dd'

    fs = DiskDrive(file_path)
    fs.print_partition_information()


if __name__ == '__main__':
    main()
