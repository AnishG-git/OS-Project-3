import sys
import os
import struct

BLOCK_SIZE = 512
HEADER_MAGIC = b'4348PRJ3'
HEADER_SIZE = BLOCK_SIZE
NODE_SIZE = BLOCK_SIZE
BTREE_DEGREE = 10
MAX_KEYS = 19
MAX_CHILDREN = 20

HEADER_FORMAT = '>8sQQ'  # magic, root_block_id, next_block_id
NODE_FORMAT = '>QQQ' + 'Q'*MAX_KEYS + 'Q'*MAX_KEYS + 'Q'*MAX_CHILDREN

class BTreeIndexFile:
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.header = None

    def open(self, mode='rb+'):
        self.file = open(self.filename, mode)

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def read_header(self):
        self.file.seek(0)
        data = self.file.read(HEADER_SIZE)
        magic, root_block, next_block = struct.unpack(HEADER_FORMAT, data[:24])
        self.header = {'magic': magic, 'root_block': root_block, 'next_block': next_block}
        return self.header

    def write_header(self, root_block, next_block):
        self.file.seek(0)
        data = struct.pack(HEADER_FORMAT, HEADER_MAGIC, root_block, next_block)
        data += b'\x00' * (HEADER_SIZE - len(data))
        self.file.write(data)
        self.file.flush()

    @staticmethod
    def file_exists(filename):
        return os.path.exists(filename)

    @staticmethod
    def is_valid_index_file(filename):
        try:
            with open(filename, 'rb') as f:
                magic = f.read(8)
                return magic == HEADER_MAGIC
        except Exception:
            return False

# Command handlers

def cmd_create(index_file):
    if BTreeIndexFile.file_exists(index_file):
        print('error: file already exists')
        return
    with open(index_file, 'wb') as f:
        # Write header: magic, root_block=0, next_block=1
        data = struct.pack(HEADER_FORMAT, HEADER_MAGIC, 0, 1)
        data += b'\x00' * (HEADER_SIZE - len(data))
        f.write(data)
    print(f'created {index_file}')

def main():
    if len(sys.argv) < 3:
        print('error: not enough arguments')
        return
    cmd = sys.argv[1]
    if cmd == 'create' and len(sys.argv) == 3:
        cmd_create(sys.argv[2])
    else:
        print('error: unknown or malformed command')

if __name__ == '__main__':
    main()
