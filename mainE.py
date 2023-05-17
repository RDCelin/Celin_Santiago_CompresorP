from compresor import HuffmanNode
import sys
import numpy as np
import compresorEstosManes as c
import descompresorEstosManes as d
import verificadorEstosManes as v
#sys.argv[0]

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print('no hay argumento o hay demasiados')
    exit()
  #crea la variable del archivo
  argumento = str(sys.argv[1])
  #comienza el temporizador con el tiempo unix
  tiempocomienzo = np.datetime64('now')
  #manda a comprimir
  #c.compress_file('LaBiblia.txt')
  c.compress_file(argumento)
  #halla tiempo de compresión tomanado el unix de cuando acaba y lo resta
  paso1 = np.datetime64('now')
  duracion1 = paso1 - tiempocomienzo
  #timedelta convierte en segundos
  print('han pasado', duracion1 / np.timedelta64(1, 's'), 'segundos')

  #manda a descomprimir
  d.decompress_file('comprimido.elmejorprofesor')
  #tiempo de descompresión
  paso2 = np.datetime64('now')
  duracion2 = paso2 - tiempocomienzo
  print('han pasado', duracion2 / np.timedelta64(1, 's'), 'segundos')
  #verificador

  v.verify('LaBiblia.txt', 'descomprimido-elmejorprofesor.txt')
