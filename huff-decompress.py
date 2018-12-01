import argparse
import os
import pickle

from itertools import chain


class Node:
    def __init__(self, symbol, frequency):
        self.symbol = symbol
        self.frequency = frequency
        self.left = None
        self.right = None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Huffman Coding Decompression")
    parser.add_argument("bin", help="bin file to be decompressed")
    args = parser.parse_args()

    coded_bytes = open(args.bin, 'rb').read()
    coded_text = "".join(chain('{0:0b}'.format(byte).zfill(8) for byte in coded_bytes))

    root, _ = os.path.splitext(args.bin)
    model = pickle.load(open(root + "-symbol-model.pkl", 'rb'))

    text = ""
    node = model
    for binary in coded_text:
        node = node.left if binary == "0" else node.right

        if node.symbol == "□":
            break
        elif node.symbol:
            text += node.symbol
            node = model

    open(root + "-decompressed.txt", 'w').write(text)
