import argparse
import collections
import operator
import os
import pickle
import re
import time

from array import array
from itertools import chain


# Huffman tree node
class Node:
    def __init__(self, symbol, frequency):
        self.symbol = symbol
        self.frequency = frequency
        self.left = None
        self.right = None


class HuffmanTree:
    def __init__(self, plain_text):
        # lookup dictionary
        self.lookup = {}
        self.text = plain_text
        # symbols list, ascending order
        self.symbols = collections.Counter(self.text)
        self.symbols = sorted(self.symbols.items(), key=operator.itemgetter(1))
        # Huffman tree node list, ascending order
        self.heap = list(chain(Node(symbol, frequency) for symbol, frequency in self.symbols))

        # loop will stop iff Huffman tree construction completed
        while len(self.heap) > 1:
            left = self.heap.pop(0)
            right = self.heap.pop(0)

            merged = Node(None, left.frequency + right.frequency)
            merged.left, merged.right = left, right

            # merged node insertion
            index = next((i for i, n in enumerate(self.heap) if n.frequency >= merged.frequency), -1)
            self.heap.insert(index if index != -1 else len(self.heap), merged)

    # Huffman tree to lookup dictionary
    def encoding(self, node, code):
        if node.symbol:
            # symbol found
            self.lookup[node.symbol] = code
            return
        self.encoding(node.left, code + "0")
        self.encoding(node.right, code + "1")

    # Huffman tree to model dictionary
    def modeling(self, node):
        if node.symbol:
            # symbol found
            return node.symbol
        return {0: self.modeling(node.left), 1: self.modeling(node.right)}

    def encoded(self):
        self.encoding(self.heap[0], "")
        # text to encoded text
        coded_text = "".join(chain(self.lookup[symbol] for symbol in self.text))
        # 0 padding
        coded_text = coded_text.ljust(len(coded_text) + 8 - len(coded_text) % 8, "0")
        # encoded text to byte array
        byte_array = array('B', list(chain(int(coded_text[i:i + 8], 2) for i in range(0, len(coded_text), 8))))

        # return bin and model files
        return byte_array, self.modeling(self.heap[0])


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser(description="Huffman Coding Compression")
    parser.add_argument("infile", help="file to be compressed")
    parser.add_argument("-s", help="specify character-based (default) or word-based encoding", choices=["char", "word"])
    args = parser.parse_args()

    # file name
    root, _ = os.path.splitext(args.infile)

    # model of encoding, default character-based
    encoding_model = "char" if not args.s else args.s

    # append BELL (pseudo-EOF) to the text
    with open(args.infile, encoding="utf-8") as file:
        text = file.read() + "\x07"

    # char to word encoding model
    if encoding_model == "word":
        text = re.compile(r"[a-z]+|[^a-z]", re.I).findall(text)

    start = time.time()
    # Huffman tree construction
    tree = HuffmanTree(text)
    print("Cost of symbol model build:", time.time() - start, "s")

    coded_array, model = tree.encoded()

    # bin file store
    with open(root + ".bin", mode="wb") as file:
        coded_array.tofile(file)

    # model file store
    with open(root + "-symbol-model.pkl", mode="wb") as file:
        pickle.dump(model, file)
