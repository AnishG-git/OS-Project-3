import csv
def cmd_load(index_file, csv_file):
    if not BTreeIndexFile.file_exists(index_file):
        print('error: file does not exist')
        return
    if not BTreeIndexFile.is_valid_index_file(index_file):
        print('error: not a valid index file')
        return
    if not os.path.exists(csv_file):
        print('error: csv file does not exist')
        return
    with open(csv_file, 'r', newline='') as csvf:
        reader = csv.reader(csvf)
        for row in reader:
            if len(row) != 2:
                print('error: invalid csv row')
                continue
            cmd_insert(index_file, row[0], row[1])

def cmd_print(index_file):
    if not BTreeIndexFile.file_exists(index_file):
        print('error: file does not exist')
        return
    if not BTreeIndexFile.is_valid_index_file(index_file):
        print('error: not a valid index file')
        return
    with open(index_file, 'rb') as f:
        f.seek(0)
        header_data = f.read(HEADER_SIZE)
        magic, root_block, next_block = struct.unpack(HEADER_FORMAT, header_data[:24])
        if root_block == 0:
            return
        def inorder(node):
            for i in range(node.num_keys):
                # Print left child
                if node.children[i] != 0:
                    child = read_node(f, node.children[i])
                    inorder(child)
                print(f'{node.keys[i]} {node.values[i]}')
            # Print rightmost child
            if node.children[node.num_keys] != 0:
                child = read_node(f, node.children[node.num_keys])
                inorder(child)
        root = read_node(f, root_block)
        inorder(root)

def cmd_extract(index_file, output_csv):
    if not BTreeIndexFile.file_exists(index_file):
        print('error: file does not exist')
        return
    if not BTreeIndexFile.is_valid_index_file(index_file):
        print('error: not a valid index file')
        return
    if os.path.exists(output_csv):
        print('error: output file already exists')
        return
    with open(index_file, 'rb') as f, open(output_csv, 'w', newline='') as outf:
        writer = csv.writer(outf)
        f.seek(0)
        header_data = f.read(HEADER_SIZE)
        magic, root_block, next_block = struct.unpack(HEADER_FORMAT, header_data[:24])
        if root_block == 0:
            return
        def inorder(node):
            for i in range(node.num_keys):
                if node.children[i] != 0:
                    child = read_node(f, node.children[i])
                    inorder(child)
                writer.writerow([node.keys[i], node.values[i]])
            if node.children[node.num_keys] != 0:
                child = read_node(f, node.children[node.num_keys])
                inorder(child)
        root = read_node(f, root_block)
        inorder(root)

def cmd_search(index_file, key_str):
    if not BTreeIndexFile.file_exists(index_file):
        print('error: file does not exist')
        return
    if not BTreeIndexFile.is_valid_index_file(index_file):
        print('error: not a valid index file')
        return
    try:
        key = int(key_str)
        if key < 0:
            raise ValueError
    except Exception:
        print('error: key must be an unsigned integer')
        return
    with open(index_file, 'rb') as f:
        f.seek(0)
        header_data = f.read(HEADER_SIZE)
        magic, root_block, next_block = struct.unpack(HEADER_FORMAT, header_data[:24])
        if root_block == 0:
            print('error: key not found')
            return
        # Traverse B-Tree from root
        node = read_node(f, root_block)
        while True:
            # Binary search in node's keys
            left, right = 0, node.num_keys - 1
            found = False
            pos = 0
            while left <= right:
                mid = (left + right) // 2
                if key < node.keys[mid]:
                    right = mid - 1
                elif key > node.keys[mid]:
                    left = mid + 1
                else:
                    # Found
                    print(f'{node.keys[mid]} {node.values[mid]}')
                    return
            pos = left
            # If leaf node (all children are zero)
            if all(c == 0 for c in node.children):
                break
            # Descend to child
            child_block = node.children[pos] if pos < len(node.children) else 0
            if child_block == 0:
                break
            node = read_node(f, child_block)
        print('error: key not found')

# Helper for B-Tree node
class BTreeNode:
    def __init__(self, block_id, parent_id, num_keys, keys, values, children):
        self.block_id = block_id
        self.parent_id = parent_id
        self.num_keys = num_keys
        self.keys = keys  # list of ints, length MAX_KEYS
        self.values = values  # list of ints, length MAX_KEYS
        self.children = children  # list of ints, length MAX_CHILDREN

    @staticmethod
    def empty(block_id, parent_id):
        return BTreeNode(block_id, parent_id, 0, [0]*MAX_KEYS, [0]*MAX_KEYS, [0]*MAX_CHILDREN)

    def to_bytes(self):
        data = struct.pack('>QQQ', self.block_id, self.parent_id, self.num_keys)
        data += b''.join(k.to_bytes(8, 'big') for k in self.keys)
        data += b''.join(v.to_bytes(8, 'big') for v in self.values)
        data += b''.join(c.to_bytes(8, 'big') for c in self.children)
        data += b'\x00' * (NODE_SIZE - len(data))
        return data

    @staticmethod
    def from_bytes(data):
        block_id, parent_id, num_keys = struct.unpack('>QQQ', data[:24])
        keys = [int.from_bytes(data[24+8*i:32+8*i], 'big') for i in range(MAX_KEYS)]
        values = [int.from_bytes(data[176+8*i:184+8*i], 'big') for i in range(MAX_KEYS)]
        children = [int.from_bytes(data[328+8*i:336+8*i], 'big') for i in range(MAX_CHILDREN)]
        return BTreeNode(block_id, parent_id, num_keys, keys, values, children)

def read_node(f, block_id):
    f.seek(block_id * BLOCK_SIZE)
    data = f.read(BLOCK_SIZE)
    return BTreeNode.from_bytes(data)

def write_node(f, node):
    f.seek(node.block_id * BLOCK_SIZE)
    f.write(node.to_bytes())
    f.flush()

def cmd_insert(index_file, key_str, value_str):
    if not BTreeIndexFile.file_exists(index_file):
        print('error: file does not exist')
        return
    if not BTreeIndexFile.is_valid_index_file(index_file):
        print('error: not a valid index file')
        return
    try:
        key = int(key_str)
        value = int(value_str)
        if key < 0 or value < 0:
            raise ValueError
    except Exception:
        print('error: key and value must be unsigned integers')
        return
    with open(index_file, 'rb+') as f:
        # Read header
        f.seek(0)
        header_data = f.read(HEADER_SIZE)
        magic, root_block, next_block = struct.unpack(HEADER_FORMAT, header_data[:24])
        if root_block == 0:
            # Tree is empty, create root node
            node = BTreeNode.empty(next_block, 0)
            node.num_keys = 1
            node.keys[0] = key
            node.values[0] = value
            write_node(f, node)
            # Update header
            f.seek(0)
            new_header = struct.pack(HEADER_FORMAT, HEADER_MAGIC, next_block, next_block+1)
            new_header += b'\x00' * (HEADER_SIZE - len(new_header))
            f.write(new_header)
            f.flush()
            print(f'inserted {key} {value}')
            return
        # Non-empty tree: read root node
        root = read_node(f, root_block)
        # Only support insert into non-full root for now
        if root.num_keys >= MAX_KEYS:
            print('error: root node full (splitting not implemented)')
            return
        # Find position to insert
        i = 0
        while i < root.num_keys and key > root.keys[i]:
            i += 1
        if i < root.num_keys and key == root.keys[i]:
            print('error: duplicate key')
            return
        # Shift keys/values to make room
        for j in range(root.num_keys, i, -1):
            root.keys[j] = root.keys[j-1]
            root.values[j] = root.values[j-1]
        root.keys[i] = key
        root.values[i] = value
        root.num_keys += 1
        write_node(f, root)
        print(f'inserted {key} {value}')
        
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
    elif cmd == 'insert' and len(sys.argv) == 5:
        cmd_insert(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'search' and len(sys.argv) == 4:
        cmd_search(sys.argv[2], sys.argv[3])
    elif cmd == 'load' and len(sys.argv) == 4:
        cmd_load(sys.argv[2], sys.argv[3])
    elif cmd == 'print' and len(sys.argv) == 3:
        cmd_print(sys.argv[2])
    elif cmd == 'extract' and len(sys.argv) == 4:
        cmd_extract(sys.argv[2], sys.argv[3])
    else:
        print('error: unknown or malformed command')

if __name__ == '__main__':
    main()
