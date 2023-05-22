import sys
from mpi4py import MPI
comm = MPI.COMM_WORLD   # Defines the default communicator
num_procs = comm.Get_size()  # Stores the number of processes in num_procs.
rank = comm.Get_rank()  # Stores the rank (pid) of the current process
number=rank
res=[]
#at the end
if rank == 0:
    res.append(number**2)
    #enviar tdodo??
    for i in range(num_procs):
        comm.send(i,dest=i) 
    print("root recibio :")
    
    for i in range(num_procs):
        comm.recv(source=i)
        res.append(i**2)
    print(res)
else:
    number=comm.recv(source=0)
    number**=2
    
    comm.send(number,dest=0)
