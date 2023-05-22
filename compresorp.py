import os
import sys
import numpy as np
from mpi4py import MPI


def verificar_path(path_w):
    return os.path.exists(path_w)


class HuffmanNode:
    def __init__(self, freq, value=None, left=None, right=None):
        self.freq = freq
        self.value = value
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

    def __eq__(self, other):
        return self.freq == other.freq


def build_freq_dict(text):
    freq_dict = {}
    for char in text:
        if char in freq_dict:
            freq_dict[char] += 1
        else:
            freq_dict[char] = 1
    return freq_dict


def build_huffman_tree(freq_dict):
    nodos = [HuffmanNode(freq=freq, value=char) for char, freq in freq_dict.items()]
    while len(nodos) > 1:
        nodos.sort()
        left = nodos.pop(0)
        right = nodos.pop(0)
        parent = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        nodos.append(parent)
    return nodos[0]


def build_codewords(nodo, code="", codewords={}):
    if nodo is None:
        return
    if nodo.value is not None:
        codewords[nodo.value] = code
    build_codewords(nodo.left, code + "0", codewords)
    build_codewords(nodo.right, code + "1", codewords)


def compress_text(text):
    freq_dict = build_freq_dict(text)
    tree = build_huffman_tree(freq_dict)
    pclave = {}
    build_codewords(tree, codewords=pclave)
    compressed = ""
    for char in text:
        compressed += pclave[char]
    binary = bytes(int(compressed[i : i + 8], 2) for i in range(0, len(compressed), 8))
    return binary, tree


def write_compressed_file(file_path, compressed_data, tree, interline):
    with open(file_path, "wb") as f:
        np.save(f, (tree, interline))
        f.write(compressed_data)


def compress_file(file_path, interline):
    with open(file_path, "r", encoding="ISO-8859-1") as f:
        text = f.read()
    text += " holaab"
    compressed_data, tree = compress_text(text)
    compressed_file_path = "comprimido.elmejorprofesor"
    write_compressed_file(compressed_file_path, compressed_data, tree, interline)
    f.close()


def verify_interline(filename):
    with open(filename, "rb") as f:
        contenido = f.read()

    if b"\r\n" in contenido:
        return "\r\n"
    else:
        return "\n"


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

Inicio = np.datetime64("now")
filename = sys.argv[1]
interline = verify_interline(filename)
compressed_data_list=None
compressed_data=None
merged_data=None

if rank == 0:
    compress_file(filename, interline)
    Final = np.datetime64("now")
    time = Final - Inicio
    print(time / np.timedelta64(1, "s"))
else:#ISO-8859-1
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()
    text += " holaab"
    compressed_data, _ = compress_text(text)
    comm.send(compressed_data, dest=0)

if rank == 0:
    compressed_data_list=comm.bcast(compressed_data_list,root=0)
    compressed_data=comm.bcast(compressed_data,root=0)
    size=comm.bcast(size,root=0)
    compressed_data_list = [compressed_data]
    for i in range(1, size):
        compressed_data = comm.recv(source=i)
        if compressed_data is not None:
            compressed_data_list.append(compressed_data)
    MPI.Finalize()
    merged_data=comm.bcast(merged_data,root=0)
    merged_data = b"".join(compressed_data_list) 
    #merged_data = b"".join(bytes(data) for data in compressed_data_list if data is not None)
    write_compressed_file("comprimido.elmejorprofesor", merged_data, None, interline)
    
