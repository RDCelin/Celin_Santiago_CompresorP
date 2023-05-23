import os
import sys
import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

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


def verificar_path(path_w):
    return os.path.exists(path_w)


def read_compressed_file(file_path):
    with open(file_path, "rb") as f:
        data = np.load(f, allow_pickle=True)
        tree = data[0]
        interline = data[1]
        info_comp = f.read()
    return info_comp, tree, interline


def decode_text(info_comp, tree):
    decoded = ""
    binario_str = "".join(["{:08b}".format(byte) for byte in info_comp])
    nodo = tree
    for bit in binario_str:
        if bit == "0":
            nodo = nodo.left
        else:
            nodo = nodo.right
        if nodo.value is not None:
            decoded += nodo.value
            if decoded.endswith(" hola"):
                
                decoded = decoded[:-5]
                break
            nodo = tree
    return decoded


def parallel_decompress_file(file_path):
    if rank == 0:
        info_comp, tree, interline = read_compressed_file(file_path)
        texto = decode_text(info_comp, tree)
        posicion_ultimo_espacio = texto.rfind(" hola")
        new_text = texto[:posicion_ultimo_espacio]
        if len(new_text) > 0:
            chunks = split_text_into_chunks(new_text, size)
        else:
            chunks = []
    else:
        info_comp, tree, interline = None, None, None
        chunks = None

    info_comp = comm.bcast(info_comp, root=0)
    tree = comm.bcast(tree, root=0)
    interline = comm.bcast(interline, root=0)
    chunks = comm.scatter(chunks, root=0)

    decompressed_chunk = decompress_chunk(chunks, info_comp, tree, interline)
    decompressed_data = comm.gather(decompressed_chunk, root=0)

    if rank == 0:
        combined_text = combine_chunks(decompressed_data)
        decompressed_file_path = "descomprimidop-elmejorprofesor.txt"
        with open(
            decompressed_file_path, "w", encoding="ISO-8859-1", newline=interline
        ) as f:
            f.write(combined_text)

def split_text_into_chunks(text, num_chunks):
    words = text.split()
    chunk_size = len(words) // num_chunks
    remainder = len(words) % num_chunks
    chunks = [words[i:i+chunk_size] for i in range(0, len(words) - remainder, chunk_size)]
    if remainder > 0:
        chunks.append(words[-remainder:])
    return chunks[:num_chunks]


def decompress_chunk(chunk, info_comp, tree, interline):
    texto = decode_text(info_comp, tree)
    return texto

def combine_chunks(chunks):
    combined_text = ""
    for i,chunk in enumerate(chunks):
         combined_text = chunk  
    return combined_text




Inicio = np.datetime64("now")
filename = sys.argv[1]
if verificar_path(filename):
    parallel_decompress_file(filename)
Final = np.datetime64("now")
if rank == 0:
    time = Final - Inicio
    print(time / np.timedelta64(1, "s"))
