import argparse
import array
import collections
import operator
import os
import pickle
import re
import time

from itertools import chain


class Node:
    def __init__(self, symbol, frequency):
        self.symbol = symbol
        self.frequency = frequency
        self.left = None
        self.right = None


class HuffmanTree:
    def __init__(self, plain_text):
        self.lookup = {}
        self.text = plain_text
        self.symbols = collections.Counter(self.text)
        self.symbols = sorted(self.symbols.items(), key=operator.itemgetter(1))
        self.heap = list(chain(Node(symbol, frequency) for symbol, frequency in self.symbols))

        while len(self.heap) > 1:
            left = self.heap.pop(0)
            right = self.heap.pop(0)

            merged = Node(None, left.frequency + right.frequency)
            merged.left, merged.right = left, right

            index = next((i for i, n in enumerate(self.heap) if n.frequency >= merged.frequency), -1)
            self.heap.insert(index if index != -1 else len(self.heap), merged)

    def coding(self, node, code):
        if node.symbol:
            self.lookup[node.symbol] = code
            return
        self.coding(node.left, code + "0")
        self.coding(node.right, code + "1")

    def modeling(self, node):
        if node.symbol:
            return node.symbol
        return {0: self.modeling(node.left), 1: self.modeling(node.right)}

    def encoded(self):
        self.coding(self.heap[0], "")
        symbol_model = self.modeling(self.heap[0])
        coded_text = "".join(chain(self.lookup[symbol] for symbol in self.text))
        coded_text = coded_text.ljust(len(coded_text) + 8 - len(coded_text) % 8, "0")

        coded_array = array.array('B', list(chain(int(coded_text[i:i + 8], 2) for i in range(0, len(coded_text), 8))))

        return coded_array, symbol_model


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Huffman Coding Compression")
    parser.add_argument("infile", help="file to be compressed")
    parser.add_argument("-s", help="specify character-based (default) or word-based encoding", choices=["char", "word"])
    args = parser.parse_args()

    root, _ = os.path.splitext(args.infile)
    encoding_model = "char" if not args.s else args.s

    text = open(args.infile, encoding="utf8").read() + "\x07"
    if encoding_model == "word":
        text = re.compile(r"[a-z]+|[^a-z]", re.I).findall(text)

    tree = HuffmanTree(text)
    encoded_array, model = tree.encoded()

    encoded_array.tofile(open(root + ".bin", mode="wb"))
    pickle.dump(model, open(root + "-symbol-model.pkl", mode="wb"))
