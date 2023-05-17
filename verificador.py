import sys

def verify(original_file_path, decompressed_file_path):
  with open(original_file_path, 'r', encoding='ISO-8859-1') as f:
    original_text = f.read()

  with open(decompressed_file_path, 'r', encoding='ISO-8859-1') as f:
    decompressed_text = f.read()

  if original_text == decompressed_text:
    print('ok')
  else:
    print('nok')

original_file_path = sys.argv[1]
decompressed_file_path = sys.argv[2]
verify(original_file_path, decompressed_file_path)
