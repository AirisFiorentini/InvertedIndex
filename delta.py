import csv
from collections import defaultdict
import re
from pympler import asizeof
from BitVector import BitVector
import time

# Функции для создания индекса
def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

def create_inverted_index(csv_filename): # инвертированный индекс
    inverted_index = defaultdict(set)
    with open(csv_filename, 'r', encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            post_id = int(row['post_id'])
            text = row['text']
            for word in tokenize(text):
                inverted_index[word].add(post_id)
    return inverted_index

def delta_encode_bitvector(numbers):
    numbers = sorted(numbers)
    prev = 0
    delta_encoded = BitVector(size=0)
    for number in sorted(numbers):
        delta = number - prev
        binary = BitVector(intVal=delta)
        unary = BitVector(intVal=len(binary))
        for i in range(len(unary) - 1):
            delta_encoded += BitVector(intVal=0)
        delta_encoded += BitVector(intVal=1)
        delta_encoded += unary[1:]
        delta_encoded += binary[1:]  # Append binary representation without leading 1
        prev = number
    return delta_encoded


def delta_decode_bitvector(delta_encoded):
    numbers = []
    i = 0
    last_decoded = 0
    while i < len(delta_encoded):
        zeros = 0
        while True:
            if delta_encoded[i:i+1] == BitVector(intVal=1):
                break
            zeros += 1
            i += 1
        i += 1
        next_m_bits = BitVector(size=0)
        for j in range(zeros):
            next_m_bits += delta_encoded[i:i+1]
            i += 1
        l_value = 2 ** zeros + next_m_bits.intValue()
        next_l_bits = BitVector(size=0)
        for j in range(l_value - 1):
            next_l_bits += delta_encoded[i:i+1]
            i += 1
        value = 2 ** (l_value - 1) + next_l_bits.intValue()
        value += last_decoded
        last_decoded = value
        numbers.append(value)
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

if __name__ == "__main__":
    print()
    print("Delta:")
    inverted_index = create_inverted_index('posts_MGU.csv') # ('test_files/empty_file.csv') # ('test_files/empty_file.csv') ('posts_MGU.csv')
    start_time = time.time()
    delta_bitvector_compressed_index = delta_encode_bitvector_compressed(inverted_index)
    end_time = time.time()
    indexing_time = end_time - start_time

    print(f"Indexing time of delta: {indexing_time} seconds")

    delta_bitvector_size = asizeof.asizeof(delta_bitvector_compressed_index) 
    print(f"Delta bitvector compressed index size: {delta_bitvector_size}")

    delta_decompressed_index = delta_decode_bitvector_compressed(delta_bitvector_compressed_index)
    # print(inverted_index['покоряем'])
    # print(delta_decompressed_index['покоряем'])
