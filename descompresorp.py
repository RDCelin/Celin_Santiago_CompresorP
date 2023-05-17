import numpy as np
import sys
from mpi4py import MPI

# Function to compress data using MPS techniques
def compress_data(data, bond_dimension):
    # Convert data to a list of characters
    characters = list(data)

    # Create the MPS tensor network
    num_chars = len(characters)
    tensors = []

    # Initialize the boundary tensors
    tensors.append(np.random.rand(1, bond_dimension, bond_dimension))
    tensors.append(np.random.rand(bond_dimension, 1, bond_dimension))

    # Create the core tensors
    for i in range(1, num_chars - 1):
        tensors.append(np.random.rand(bond_dimension, bond_dimension, bond_dimension))

    # Initialize the compression
    compressed_data = []

    # Compress each character
    for i in range(num_chars):
        char = characters[i]
        tensor = tensors[i]

        # Contract the MPS tensor with the character tensor
        contracted_tensor = np.tensordot(tensor, char, axes=(2, 0))

        # Reduce the bond dimension using singular value decomposition (SVD)
        U, S, V = np.linalg.svd(contracted_tensor, full_matrices=False)
        U_truncated = U[:, :bond_dimension]
        S_truncated = S[:bond_dimension]
        V_truncated = V[:bond_dimension, :]

        # Update the MPS tensor and the next boundary tensor
        tensors[i] = U_truncated
        next_boundary_tensor = np.diag(S_truncated) @ V_truncated

        # Add the compressed character to the compressed data
        compressed_data.append(next_boundary_tensor)

    return compressed_data

# Read the input file
def read_input_file(input_file):
    with open(input_file, 'r') as file:
        data = file.read()
    return data

# Main function
def main():
    # Initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Check if the input file and bond dimension are provided
    if len(sys.argv) < 3:
        if rank == 0:
            print("Usage: mpiexec -n <num_processes> python compress.py input_file bond_dimension")
        return

    input_file = sys.argv[1]
    bond_dimension = int(sys.argv[2])

    # Read the input file on the root process
    if rank == 0:
        data = read_input_file(input_file)
    else:
        data = None

    # Distribute the data among processes
    data = comm.bcast(data, root=0)

    # Perform compression on each process
    compressed_data = compress_data(data, bond_dimension)

    # Gather compressed data to the root process
    compressed_data = comm.gather(compressed_data, root=0)

    # Root process writes the compressed data to the output file
    if rank == 0:
        output_file = input_file + ".compressed"
        with open(output_file, 'wb') as file:
            for process_data in compressed_data:
                for compressed_char in process_data:
                    np.save(file, compressed_char)

        print("Compression completed. Compressed data is saved in", output_file)