import csv
from collections import defaultdict
import re
import json
import time
from pympler import asizeof
from BitVector import BitVector


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

def pad_to_byte_length(bitvec):
    length = len(bitvec)
    pad_size = -length % 8  # Size of padding to reach a byte boundary.
    return bitvec + BitVector(size=pad_size), length
"""
def gamma_encode_bitvector(number):
    if number == 1:
        return pad_to_byte_length(BitVector(size=1, intVal=0))
    else:
        binary_num = bin(number)[2:]
        length = unary(len(binary_num))
        offset = binary_num[1:]
        return pad_to_byte_length(BitVector(bitstring=length + offset))

def gamma_encode_bitvector_compressed(inverted_index):
    # Теперь каждый элемент в gamma_compressed_index[word] - это кортеж, 
    # где первый элемент - это ASCII-строка bitvector, 
    # а второй элемент - это исходная длина bitvector. 
    gamma_compressed_index = {}
    for word, post_ids in inverted_index.items():
        gamma_compressed_index[word] = [(gamma_encode_bitvector(post_id)[0].get_bitvector_in_ascii(), gamma_encode_bitvector(post_id)[1]) for post_id in post_ids]
    return gamma_compressed_index

"""

def gamma_encode_bitvector(numbers):
    gamma_encoded = BitVector(size=0)
    for number in sorted(numbers):
        binary_num = bin(number)[2:]
        length = unary(len(binary_num))
        offset = binary_num[1:]
        gamma_number = BitVector(bitstring=length + offset)
        padded_gamma_number, original_length = pad_to_byte_length(gamma_number)
        gamma_encoded += padded_gamma_number
    return gamma_encoded, original_length


# def gamma_encode_bitvector_compressed(inverted_index): # the second version
#     gamma_compressed_index = {}
#     for word, post_ids in inverted_index.items():
#         delta_encoded = delta_encode(list(post_ids))
#         #gamma_compressed_index[word] = [(gamma_encode_bitvector(delta)[0].get_bitvector_in_ascii(), gamma_encode_bitvector(delta)[1]) for delta in delta_encoded]
#         gamma_compressed_index[word] = [(bitvec_ascii, length) for delta in delta_encoded for bitvec_ascii, length in [gamma_encode_bitvector([delta])]]
#     return gamma_compressed_index

def gamma_encode_bitvector_compressed(delta_compressed_index):
    gamma_compressed_index = {}
    for word, delta_encoded in delta_compressed_index.items():
        gamma_compressed_index[word] = [(bitvec_ascii, length) for delta in delta_encoded for bitvec_ascii, length in [gamma_encode_bitvector([delta])]]
    return gamma_compressed_index


def binary(number):
    return bin(number)[2:]

def unary(number):
    return '0' * (number - 1) # '1' * (number - 1) + '0'

def gamma_encode(number):  #TODO: numbers 
    binary_num = binary(number)
    length = unary(len(binary_num))
    offset = binary_num
    return length + offset

    # if number == 1:
    #     return '0'
    # else:
    #     binary_num = binary(number)
    #     length = unary(len(binary_num))
    #     offset = binary_num[1:]
    #     return length + offset

def delta_compress_inverted_index(inverted_index):
    delta_compressed_index = {}
    for word, post_ids in inverted_index.items():
        delta_encoded = delta_encode(list(post_ids))
        delta_compressed_index[word] = delta_encoded
    return delta_compressed_index

def gamma_compress_inverted_index(delta_compressed_index):  #TODO: rewrite delta_compressed_index
    gamma_compressed_index = {}
    for word, delta_encoded in delta_compressed_index.items():
        gamma_encoded = [gamma_encode(number) for number in delta_encoded]
        gamma_compressed_index[word] = gamma_encoded
    return gamma_compressed_index

# Функции для сохранения и загрузки индекса
# def save_index_to_file(index, filename):
#     with open(filename, 'w') as f:
#         json.dump(index, f)

# def save_index_to_file_new(index, filename):
#     index_to_save = {word: list(post_ids) for word, post_ids in index.items()}
#     with open(filename, 'w') as f:
#         json.dump(index_to_save, f)

def save_index_to_file(index, filename):
    index_to_save = {word: list(post_ids) for word, post_ids in index.items()}
    with open(filename, 'w') as f:
        json.dump(index_to_save, f)

def save_compressed_index_to_file(index, filename):
    with open(filename, 'w') as f:
        json.dump(index, f)

def gamma_decode(gamma_encoded_number):   # changed
    unary_length = gamma_encoded_number.index('1')
    binary_offset = gamma_encoded_number[unary_length:]
    binary_number = binary_offset
    return int(binary_number, 2)

def delta_decode(delta_encoded_numbers):
    numbers = []
    total = 0
    for delta in delta_encoded_numbers:
        total += delta
        numbers.append(total)
    return numbers

# def delta_decode(delta_encoded_numbers):
#     return [delta_decode_single_number(number) for number in delta_encoded_numbers]

# def gamma_decode(gamma_encoded_numbers):
#     return [gamma_decode_single_number(number) for number in gamma_encoded_numbers]

# def delta_decode_single_number(delta_encoded_number):
#     n = len(delta_encoded_number) // 2
#     offset = delta_encoded_number[n:]
#     value = int(''.join(str(x) for x in offset), 2)
#     return (2 ** n) - 1 + value

# def gamma_decode_single_number(gamma_encoded_number):
#     n = len(gamma_encoded_number) // 2
#     value = gamma_encoded_number[n:]
#     return (2 ** n) - 1 + int(''.join(str(x) for x in value), 2)

def load_index(filename):
    with open(filename, 'r') as f:
        loaded_index = json.load(f)

    index = {}
    for word, post_ids in loaded_index.items():
        index[word] = set(post_ids)

    return index

def load_and_decode_delta_index(filename):
    with open(filename, 'r') as f:
        encoded_index = json.load(f)

    index = {}
    for word, encoded_post_ids_list in encoded_index.items():
        # decoded_post_ids = [delta_decode(encoded_post_id) for encoded_post_id in encoded_post_ids_list]
        decoded_post_ids = delta_decode(encoded_post_ids_list)
        index[word] = set(decoded_post_ids)

    return index

def load_and_decode_gamma_index(filename):
    with open(filename, 'r') as f:
        encoded_index = json.load(f)

    index = {}
    for word, encoded_post_ids_list in encoded_index.items():
        decoded_post_ids = [gamma_decode(encoded_post_id) for encoded_post_id in encoded_post_ids_list]
        index[word] = set(decoded_post_ids)

    return index

def load_and_decode_index(filename, decode_func):
    with open(filename, 'r') as f:
        encoded_index = json.load(f)

    index = {}
    for word, encoded_post_ids_list in encoded_index.items():
        decoded_post_ids = [decode_func(encoded_post_id) for encoded_post_id in encoded_post_ids_list]
        index[word] = set(decoded_post_ids)

    return index

# Функция поиска
def search(query, index):
    words = tokenize(query)
    if not words:
        return set()
    
    result = set(index.get(words[0], []))
    for word in words[1:]:
        result &= set(index.get(word, []))
        
    return result

def get_matching_messages(csv_filename, matching_post_ids):
    matching_messages = []
    with open(csv_filename, 'r', encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['post_id']) in matching_post_ids:
                matching_messages.append(row['text'])
    return matching_messages

def save_search_results_to_file(results, filename):
    with open(filename, 'w', encoding="utf8") as f:
        for message in results:
            f.write(message + '\n' + '-'*120 + '\n')

def get_data_size_of_compressed_index_gamma_bitvector(index):
    total_size = 0
    for word, post_ids in index.items():
        for bitvec_ascii, _ in post_ids:
            total_size += len(bitvec_ascii)
    return total_size

def get_data_size_of_compressed_index_delta_bitvector(index):
    total_size = 0
    for word, post_ids in index.items():
        total_size += len(post_ids)
    return total_size


if __name__ == "__main__":
    # Создание, сжатие, сохранение и загрузка индекса
    inverted_index = create_inverted_index('posts_MGU.csv') # ('test_files/empty_file.csv') 
    delta_compressed_index = delta_compress_inverted_index(inverted_index)
    # gamma_compressed_index = gamma_compress_inverted_index(inverted_index)
    delta_gamma_compressed_index = gamma_compress_inverted_index(delta_compressed_index)

    # using bitvector 
    delta_bitvector_compressed_index = delta_encode_bitvector_compressed(delta_compressed_index)  #  (inverted_index)
    gamma_bitvector_compressed_index = gamma_encode_bitvector_compressed(delta_compressed_index)
    
    for word, post_ids in inverted_index.items():
        inverted_index[word] = str(post_ids)

    for word, post_ids in delta_compressed_index.items():
        delta_compressed_index[word] = str(post_ids)
    
    for word, post_ids in delta_gamma_compressed_index.items():
        lst = []
        for item in post_ids:
            # print(type(item))
            lst.append(str(int(item, 2)))
        delta_gamma_compressed_index[word] = lst
        
    # print (gamma_compressed_index)

    original_size = asizeof.asizeof(inverted_index)
    delta_compressed_size = asizeof.asizeof(delta_compressed_index)
    # gamma_compressed_size = asizeof.asizeof(gamma_compressed_index)
    delta_gamma_size = asizeof.asizeof(delta_gamma_compressed_index)
    # delta_gamma_size2 = get_data_size_of_compressed_index_delta_bitvector(delta_gamma_compressed_index)


    delta_bitvector_size = asizeof.asizeof(delta_bitvector_compressed_index)
    delta_bitvector_size2 = get_data_size_of_compressed_index_delta_bitvector(delta_bitvector_compressed_index)
    gamma_bitvector_size = get_data_size_of_compressed_index_gamma_bitvector(gamma_bitvector_compressed_index)

    print(f"Original index size: {original_size}")
    print(f"Delta compressed index size: {delta_compressed_size}")
    # print(f"Gamma compressed index size: {gamma_compressed_size}")
    print(f"Delta Gamma compressed index size: {delta_gamma_size}")
    print(f"Delta bitvector compressed index size: {delta_bitvector_size}")
    print(f"Delta bitvector compressed index size2: {delta_bitvector_size2}")
    print(f"Gamma bitvector compressed index size: {gamma_bitvector_size}")

    # Сохранение сжатого индекса в файл
    save_index_to_file(inverted_index, 'inverted_index.json')
    # save_compressed_index_to_file(delta_compressed_index, 'delta_compressed_index.json')
    # Сохранение сжатого индекса в файл
    save_compressed_index_to_file(delta_compressed_index, 'delta_compressed_index.json')
    # save_compressed_index_to_file(gamma_compressed_index, 'gamma_compressed_index.json')
    save_compressed_index_to_file(delta_gamma_compressed_index, 'delta_gamma_compressed_index.json')


    # Загрузка сжатого индекса из файла
    with open('delta_compressed_index.json', 'r') as f:
        loaded_delta_index = json.load(f)

    # Загрузка сжатого индекса из файла и декодирование его обратно в числовую форму
    loaded_index = load_index('gamma_compressed_index.json')
    delta_loaded_index = load_and_decode_delta_index('delta_compressed_index.json')
    gamma_loaded_index = load_and_decode_gamma_index('gamma_compressed_index.json')
    delta_gamma_loaded_index = load_and_decode_gamma_index('delta_gamma_compressed_index.json')    

    # Записываем текущее время
    start_time = time.time()
    query = "Ректор СПбГУ"
    matching_post_ids = search(query, gamma_loaded_index)
    print(f"Post IDs matching the query '{query}': {matching_post_ids}")
    # Записываем текущее время и вычитаем из него время начала, чтобы получить общее время выполнения
    end_time = time.time()
    query_time = end_time - start_time
    print(f"Query time: {query_time} seconds")

    query = "Ректор СПбГУ"
    matching_post_ids = search(query, gamma_loaded_index)
    matching_messages = get_matching_messages('posts_SPbU.csv', matching_post_ids)
    new_line = '\n' + '-'*120 + '\n'
    print(f"Messages matching the query '{query}': {new_line.join(matching_messages)}")

    query = "Ректор СПбГУ"
    matching_post_ids = search(query, gamma_loaded_index)
    matching_messages = get_matching_messages('posts_SPbU.csv', matching_post_ids)
    save_search_results_to_file(matching_messages, 'search_results.txt')
