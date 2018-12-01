import argparse
import os
import pickle
import time

from itertools import chain

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Huffman Coding Decompression")
    parser.add_argument("bin", help="bin file to be decompressed")
    args = parser.parse_args()

    coded_bytes = open(args.bin, mode='rb').read()
    coded_text = "".join(chain('{0:0b}'.format(byte).zfill(8) for byte in coded_bytes))

    root, _ = os.path.splitext(args.bin)
    model = pickle.load(open(root + "-symbol-model.pkl", mode='rb'))

    text = ""
    current = model
    for binary in coded_text:
        current = current[0] if binary == "0" else current[1]

        if current == "\x07":
            break
        elif isinstance(current, str):
            text += current
            current = model

    open(root + "-decompressed.txt", mode="w", encoding="utf8").write(text)
