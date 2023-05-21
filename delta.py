import csv
from collections import defaultdict
import re
import json
import time
from pympler import asizeof
from BitVector import BitVector
import sys

# from gamma import *
from gamma import create_inverted_index

def delta_code_elias(int_value):
    result = ""
    binary = str(bin(int_value))[2:]
    binary_len = len(binary)
    len_binary_len_binary = str(bin(binary_len))[2:]
    for i in range(len(len_binary_len_binary) - 1):
        result += "0"
    result += "1"
    result += len_binary_len_binary[1:]
    result += binary[1:]
    return result 

def delta_encode_bitvector(numbers):
    prev = 0
    delta_encoded = BitVector(size=0)
    for number in sorted(numbers):
        delta = number - prev
        binary = BitVector(intVal=delta)
        unary = BitVector(intVal=len(binary) - 1)
        unary.pad_from_left(1)  # Append leading 1
        delta_encoded += unary
        delta_encoded += binary[1:]  # Append binary representation without leading 1
        prev = number
    return delta_encoded

def delta_decode_bitvector(delta_encoded):
    numbers = []
    total = 0
    i = 0
    while i < len(delta_encoded):
        unary_len = delta_encoded[i:].intValue() + 1  # Count unary length
        i += unary_len
        binary = BitVector(intVal=1, size=1)
        binary += delta_encoded[i:i+unary_len]  # Append binary representation
        delta = binary.intValue()
        total += delta
        numbers.append(total)
        i += unary_len
    return numbers

def delta_encode_bitvector_compressed(inverted_index):
    delta_compressed_index = {}
    for word, post_ids in inverted_index.items():
        delta_compressed_index[word] = delta_encode_bitvector(list(post_ids))
    return delta_compressed_index

def delta_decode_bitvector_compressed(delta_compressed_index):
    delta_decompressed_index = {}
    for word, delta_encoded in delta_compressed_index.items():
        delta_decompressed_index[word] = delta_decode_bitvector(delta_encoded)
    return delta_decompressed_index

def delta_decode_bitvector(delta_encoded):
    numbers = []
    total = 0
    i = 0
    while i < len(delta_encoded):
        unary_len = delta_encoded[i:].intValue() + 1  # Count unary length
        if i+unary_len > len(delta_encoded):
            break
            raise Exception(f"Index out of range: i={i}, unary_len={unary_len}, length of delta_encoded={len(delta_encoded)}")
        binary = BitVector(intVal=1, size=1)
        binary += delta_encoded[i : i + unary_len]  # Append binary representation without leading 1
        delta = binary.intValue()
        total += delta
        numbers.append(total)
        i += unary_len
    return numbers

print()
print("Delta:")
inverted_index = create_inverted_index('posts_SPbU.csv') # ('test_files/empty_file.csv') # ('test_files/empty_file.csv') ('posts_MGU.csv')
delta_bitvector_compressed_index = delta_encode_bitvector_compressed(inverted_index)
delta_bitvector_size = asizeof.asizeof(delta_bitvector_compressed_index) 
delta_decompressed_index = delta_decode_bitvector_compressed(delta_bitvector_compressed_index)
print(inverted_index['покоряем'])
print(delta_decompressed_index['покоряем'])
print(f"Delta bitvector compressed index size: {delta_bitvector_size}")