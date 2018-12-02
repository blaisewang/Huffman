import argparse
import os
import pickle
import time

from itertools import chain

if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser(description="Huffman Coding Decompression")
    parser.add_argument("bin", help="bin file to be decompressed")
    args = parser.parse_args()

    # bin file read
    with open(args.bin, mode="rb") as file:
        coded_bytes = file.read()

    start = time.time()

    # byte to string
    coded_text = "".join(chain("{0:0b}".format(byte).zfill(8) for byte in coded_bytes))

    # model file read
    root, _ = os.path.splitext(args.bin)
    with open(root + "-symbol-model.pkl", mode="rb") as file:
        model = pickle.load(file)

    text = ""
    node = model
    # coded text to original text
    for binary in coded_text:
        node = node[0] if binary == "0" else node[1]

        if node == "\x07":
            # pseudo-EOF BELL found
            break
        elif isinstance(node, str):
            # leaf reached
            text += node
            node = model

    print("Cost of decoding:", time.time() - start, "s")

    # decompressed text store
    with open(root + "-decompressed.txt", mode="w", encoding="utf-8") as file:
        file.write(text)
