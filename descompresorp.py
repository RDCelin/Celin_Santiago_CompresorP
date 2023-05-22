import os
import sys
import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

class HuffmanNode:
    def _init_(self, freq, value=None, left=None, right=None):
        self.freq = freq
        self.value = value
        self.left = left
        self.right = right

    def _lt_(self, other):
        return self.freq < other.freq

    def _eq_(self, other):
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
            nodo = tree
    return decoded


def decompress_file(file_path):
    info_comp, tree, interline = read_compressed_file(file_path)
    texto = decode_text(info_comp, tree)
    posicion_ultimo_espacio = texto.rfind(" hola")
    new_text = texto[:posicion_ultimo_espacio]
    decompressed_file_path = "descomprimido-elmejorprofesor.txt"
    
    if rank == 0:
        with open(decompressed_file_path, "w", encoding="ISO-8859-1", newline=interline) as f:
            f.write(new_text)
    
    MPI.Finalize()


if _name_ == "_main_":
    Inicio = np.datetime64("now")
    filename = sys.argv[1]
    if verificar_path(filename):
        decompress_file(filename)
    Final = np.datetime64("now")
    time = Final - Inicio
    print(time / np.timedelta64(1, "s"))
