## B-Tree Index File Manager

In this project, you will write an interactive Python program to create and manage index files containing a B-Tree. The user can create, insert, and search these index files via command-line commands. Your implementation should **never have more than 3 nodes in memory at a time** and must handle any errors in user input.

---

### Command Overview

All commands must be **lowercase**.

#### `create`
Create a new index file.

- **Usage:**  
    `project3 create <index_file>`
- **Behavior:**  
    Fails with an error if the file already exists (file remains unmodified).
- **Example:**  
    `project3 create test.idx`

---

#### `insert`
Insert a key/value pair into an index file.

- **Usage:**  
    `project3 insert <index_file> <key> <value>`
- **Behavior:**  
    - Fails if the file does not exist or is not a valid index file.
    - `<key>` and `<value>` are converted to unsigned integers and inserted into the B-Tree.
- **Example:**  
    `project3 insert test.idx 15 100`

---

#### `search`
Search for a key in an index file.

- **Usage:**  
    `project3 search <index_file> <key>`
- **Behavior:**  
    - Fails if the file does not exist or is not a valid index file.
    - `<key>` is converted to an unsigned integer.
    - If found, prints the key/value pair; otherwise, prints an error message.
- **Example:**  
    `project3 search test.idx 15`

---

#### `load`
Bulk insert key/value pairs from a CSV file.

- **Usage:**  
    `project3 load <index_file> <csv_file>`
- **Behavior:**  
    - Fails if either file does not exist or if the index file is invalid.
    - Each line in the CSV is a comma-separated key/value pair, inserted as with the `insert` command.
- **Example:**  
    `project3 load test.idx input.csv`

---

#### `print`
Print all key/value pairs in the index file.

- **Usage:**  
    `project3 print <index_file>`
- **Behavior:**  
    - Fails if the file does not exist or is not a valid index file.
    - Prints every key/value pair to standard output.
- **Example:**  
    `project3 print test.idx`

---

#### `extract`
Export all key/value pairs to a CSV file.

- **Usage:**  
    `project3 extract <index_file> <output_csv>`
- **Behavior:**  
    - Fails if the index file does not exist or is not valid, or if the output file already exists (output file remains unmodified).
    - Saves every key/value pair as comma-separated pairs to the output file.
- **Example:**  
    `project3 extract test.idx output.csv`

---

## Index File Format

The index file is divided into blocks of 512 bytes. Each B-Tree node fits within a single 512-byte block, and the file header occupies the entire first block. New nodes are always appended to the end of the file. Since there is no delete operation, you do not need to handle node deletion.

The actual size of the header and each node will be smaller than 512 bytes; the remaining space in each block is left unused.

All numbers stored in the file must be 8-byte integers in big-endian byte order. In Python, you can use the `to_bytes` method to convert an integer to this format:

```python
n.to_bytes(8, 'big')
```

This converts the integer `n` to a sequence of 8 bytes in big-endian order, as required for the index file. Each block will have a block id determined by the order in the file, starting at zero.

### Header Format

The header is stored in the first 512-byte block of the index file. It can be cached in memory, but must always be kept in sync with the file. The header fields, in order, are:

- **8 bytes:** Magic number `"4348PRJ3"` (as ASCII values).
- **8 bytes:** Block ID of the root node (zero if the tree is empty).
- **8 bytes:** Block ID for the next node to be added (i.e., the next available block).
- **Remaining bytes:** Unused.

---

### B-Tree Node Format

Each B-Tree node is stored in a single 512-byte block and contains the following fields, in order:

- **8 bytes:** Block ID of this node.
- **8 bytes:** Block ID of this node's parent (zero if this node is the root).
- **8 bytes:** Number of key/value pairs currently in this node.
- **152 bytes:** 19 keys (each key is an 8-byte unsigned integer).
- **152 bytes:** 19 values (each value is an 8-byte unsigned integer).
- **160 bytes:** 20 child pointers (each is an 8-byte block ID; zero if the child is a leaf).
- **Remaining bytes:** Unused.

#### Notes

- The B-Tree has a minimal degree of 10, so each node can store up to 19 key/value pairs and 20 child pointers.
- The sequences of keys, values, and child pointers are aligned by index:
    - The *i*-th key corresponds to the *i*-th value.
    - The *i*-th child pointer points to the subtree containing all entries with keys less than the *i*-th key (for *i = 0*), or between the *i*-th and *(i+1)*-th keys.
- All numbers are stored as 8-byte big-endian integers.
- If a child pointer is zero, it indicates that the corresponding child is a leaf node.
- Unused space in each block is ignored.