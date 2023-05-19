import csv
from collections import defaultdict
import re
import json

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

def binary(number):
    return bin(number)[2:]

def unary(number):
    return '1' * (number - 1) + '0'

def gamma_encode(number):
    if number == 1:
        return '0'
    else:
        binary_num = binary(number)
        length = unary(len(binary_num))
        offset = binary_num[1:]
        return length + offset

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

def gamma_decode(gamma_encoded_number):
    unary_length = gamma_encoded_number.index('0') + 1
    binary_offset = gamma_encoded_number[unary_length:]
    binary_number = '1' + binary_offset
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

if __name__ == "__main__":
    # Создание, сжатие, сохранение и загрузка индекса
    inverted_index = create_inverted_index('posts_SPbU.csv')
    delta_compressed_index = delta_compress_inverted_index(inverted_index)
    gamma_compressed_index = gamma_compress_inverted_index(inverted_index)
    # gamma_compressed_index = gamma_compress_inverted_index(delta_compressed_index)

    # Сохранение сжатого индекса в файл
    save_index_to_file(inverted_index, 'inverted_index.json')
    # save_compressed_index_to_file(delta_compressed_index, 'delta_compressed_index.json')
    # Сохранение сжатого индекса в файл
    save_compressed_index_to_file(delta_compressed_index, 'delta_compressed_index.json')

    # Загрузка сжатого индекса из файла
    with open('delta_compressed_index.json', 'r') as f:
        loaded_delta_index = json.load(f)

    save_compressed_index_to_file(gamma_compressed_index, 'gamma_compressed_index.json')

    # Загрузка сжатого индекса из файла и декодирование его обратно в числовую форму
    loaded_index = load_index('gamma_compressed_index.json')
    delta_loaded_index = load_and_decode_delta_index('delta_compressed_index.json')
    # gamma_loaded_index = load_and_decode_gamma_index('gamma_compressed_index.json')

    # delta_encoded_index = {word: [delta_encode(post_id) for post_id in post_ids] for word, post_ids in inverted_index.items()}
    # save_compressed_index_to_file(delta_encoded_index, 'delta_compressed_index.json')
    # delta_loaded_index = load_and_decode_index('delta_compressed_index.json', delta_decode)


    # delta_loaded_index = load_and_decode_index('delta_compressed_index.json', delta_decode)
    gamma_loaded_index = load_and_decode_gamma_index('gamma_compressed_index.json')


    query = "Ректор СПбГУ"
    matching_post_ids = search(query, gamma_loaded_index)
    print(f"Post IDs matching the query '{query}': {matching_post_ids}")

    query = "Ректор СПбГУ"
    matching_post_ids = search(query, gamma_loaded_index)
    matching_messages = get_matching_messages('posts_SPbU.csv', matching_post_ids)
    new_line = '\n' + '-'*120 + '\n'
    print(f"Messages matching the query '{query}': {new_line.join(matching_messages)}")

    # def save_search_results_to_file(results, filename):
    #     with open(filename, 'w') as f:
    #         json.dump(results, f)

    # query = "Ректор СПбГУ"
    # matching_post_ids = search(query, loaded_index)
    # matching_messages = get_matching_messages('posts_SPbU.csv', matching_post_ids)
    # save_search_results_to_file(matching_messages, 'search_results.json')

    query = "Ректор СПбГУ"
    matching_post_ids = search(query, gamma_loaded_index)
    matching_messages = get_matching_messages('posts_SPbU.csv', matching_post_ids)
    save_search_results_to_file(matching_messages, 'search_results.txt')
