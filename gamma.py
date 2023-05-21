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

# Функции для сжатия индекса
def delta_encode(numbers):
    prev = 0
    delta_encoded = []
    for number in sorted(numbers):
        delta_encoded.append(number - prev)
        prev = number
    return delta_encoded

def delta_compress_inverted_index(inverted_index):
    delta_compressed_index = {}
    for word, post_ids in inverted_index.items():
        delta_encoded = delta_encode(list(post_ids))
        delta_compressed_index[word] = delta_encoded
    return delta_compressed_index

def delta_decode(delta_encoded_numbers):
    numbers = []
    total = 0
    for delta in delta_encoded_numbers:
        total += delta
        numbers.append(total)
    return numbers

def decode_delta_index(delta_encoded_index):
    index = {}
    for word, encoded_post_ids_list in delta_encoded_index.items():
        decoded_post_ids = delta_decode(encoded_post_ids_list)
        index[word] = set(decoded_post_ids)
    return index

def unary(number):
    return '0' * (number - 1)

def gamma_encode(number):
    binary_repr = bin(number)[2:]  # Get binary representation of the number
    length_part = unary(len(binary_repr)) + '1'  # Unary representation of length
    offset_part = binary_repr[1:]  # Offset is binary representation without the leading 1
    return length_part + offset_part

def gamma_decode(gamma_encoded):
    unary_end = gamma_encoded.find('1')  # Find where unary part ends
    length = unary_end + 1  # Length of the binary number
    offset = gamma_encoded[unary_end + 1: unary_end + 1 + length]  # Get offset
    binary_repr = '1' + offset  # Reconstruct the binary representation
    return int(binary_repr, 2)  # Convert binary to integer

def gamma_encode_bitvector(numbers):
    gamma_encoded = ''.join(gamma_encode(number) for number in numbers)
    return BitVector(bitstring=gamma_encoded)

def gamma_encode_bitvector_compressed(inverted_index):
    gamma_compressed_index = {}
    for word, post_ids in inverted_index.items():
        delta_encoded = delta_encode(list(post_ids))
        gamma_encoded = ''.join(gamma_encode(number) for number in delta_encoded)
        bitvector = BitVector(bitstring=gamma_encoded)
        # Add padding if necessary
        if len(bitvector) % 8 != 0:
            bitvector.pad_from_right(8 - len(bitvector) % 8)
        gamma_compressed_index[word] = bitvector
    return gamma_compressed_index

def gamma_decode_bitvector(gamma_encoded_bitvector):
    gamma_encoded = str(gamma_encoded_bitvector)
    numbers = []
    start = 0
    while start < len(gamma_encoded):
        # на каждой итерации проверять, что единица действительно нашлась. 
        unary_end = gamma_encoded.find('1', start)  # Find where unary part ends
        if unary_end == -1:
            break
        length = unary_end - start + 1  # Length of the binary number
        number = gamma_decode(gamma_encoded[start: unary_end + length])  # Decode number
        numbers.append(number)
        start = unary_end + length
    return numbers

def gamma_decode_bitvector_compressed(gamma_compressed_index):
    gamma_decompressed_index = {}
    for word, bitvector in gamma_compressed_index.items():
        numbers = gamma_decode_bitvector(bitvector)
        gamma_decompressed_index[word] = numbers
    return decode_delta_index(gamma_decompressed_index)

# Функция поиска
def search(query, index):
    words = tokenize(query)
    if not words:
        return set()
    
    result = set(index.get(words[0], []))
    for word in words[1:]:
        result &= set(index.get(word, []))
        
    return result


inverted_index = create_inverted_index('posts_MGU.csv') # ('test_files/empty_file.csv') # ('test_files/empty_file.csv') ('posts_MGU.csv')

query = "Ректор МГУ"
start_time = time.time()
matching_post_ids = search(query, inverted_index)
# print(f"Post IDs matching the query '{query}': {matching_post_ids}")
# Записываем текущее время и вычитаем из него время начала, чтобы получить общее время выполнения
end_time = time.time()
query_time = end_time - start_time
print(f"Query time: {query_time} seconds")


print("Inverted index size:", asizeof.asizeof(inverted_index))
# delta_compressed_index = delta_compress_inverted_index(inverted_index)
# print('delta', delta_compressed_index['покоряем'])
# print(delta_compressed_index)
delta_compressed_index = inverted_index
start_time = time.time()
gamma_bitvector_compressed_index = gamma_encode_bitvector_compressed(delta_compressed_index)
end_time = time.time()
indexing_time = end_time - start_time

print(f"Indexing time of gamma: {indexing_time} seconds")



gamma_bitvector_size = asizeof.asizeof(gamma_bitvector_compressed_index) 
print(f"Gamma bitvector compressed index size: {gamma_bitvector_size}")

gamma_decompressed_index = gamma_decode_bitvector_compressed(gamma_bitvector_compressed_index)
#print(smth)

# print(inverted_index['покоряем'])
# print(gamma_decompressed_index['покоряем'])
# #print(gamma_decode_bitvector(gamma_bitvector_compressed_index['покоряем']))


# print(gamma_encode_bitvector([10, 12, 2]))
# print(gamma_decode_bitvector(gamma_encode_bitvector([10, 12, 2])))

# test = {'word':set([10, 12, 2])}
# # print(gamma_decode_bitvector(gamma_encode_bitvector_compressed(test)))
# print(gamma_decode_bitvector_compressed(gamma_encode_bitvector_compressed(test)))
# print(gamma_encode_bitvector_compressed(test)["word"])
