import pytest
import os.path
from main import *

# Проверка на правильные размеры файла "inverted_index.json"
def test_1():
    file1 = "inverted_index.json"
    size1 = os.path.getsize(file1)
    assert size1 == 1003832

# Проверка на правильные размеры файла "compressed_index.json"
def test_2():
    file2 = "gamma_compressed_index.json"
    size2 = os.path.getsize(file2)
    assert size2 == 1924317

# проверка функции tokenize
def test_3():
    text = "🏆Покоряем вершину [club202446718|«ТехноОлимпа»]..."
    result = tokenize(text)
    assert result[0] == 'покоряем' and result[-1] == "техноолимпа"

# проверка функции tokenize на неправльный вход
def test_4():
    text = 255
    with pytest.raises(AttributeError):
        tokenize(text)

# проверка функции create_inverted_index
def test_5():
    result = create_inverted_index("test_files/test_posts_file.csv")
    assert len(result) == 266 and result["мы"] == {1666, 4293, 10543}

# проверка функции create_inverted_index на неправильный вход - несуществующий файл
def test_6():
    with pytest.raises(FileNotFoundError):
        create_inverted_index("test_files/no_existing_file.csv") 

# проверка функции create_inverted_index на неправильный вход - рандомное число вместо строки
def test_7():
    with pytest.raises(OSError):
        create_inverted_index(23534)

# проверка функции delta_encode
def test_8():
    numbers = [4257, 4282, 4268, 4293] 
    res = [4257, 11, 14, 11]
    assert delta_encode(numbers) == res

# проверка функции delta_encode на неверный вход
def test_9():
    numbers = "ha-ha"
    with pytest.raises(TypeError):
        delta_encode(numbers)

# проверка функции binary
def test_10():
    numbers = 4257
    res = '1000010100001'
    assert binary(numbers) == res

# проверка функции binary на неверный вход
def test_11():
    number = "ha-ha"
    with pytest.raises(TypeError):
        binary(number)

# проверка функции unary
def test_12():
    number = 13
    res = '1111111111110'
    assert unary(number) == res

# проверка функции unary на неверный вход
def test_13():
    number = "ha-ha"
    with pytest.raises(TypeError):
        unary(number)

# проверка функции create_inverted_index на пустой файл
def test_14():
    result = create_inverted_index("test_files/empty_file.csv")
    assert len(result) == 0

# проверка функции create_inverted_index на некорректный файл (без поля text)
def test_15():
    with pytest.raises(KeyError):
        create_inverted_index("test_files/uncorrect_file.csv")

# проверка функции create_inverted_index на очень большой файл (~136 тыс записей)
def test_16():
    result = create_inverted_index("test_files/very_big_file.csv")
    assert len(result) == 805866

# проверка функции gamma_encode
def test_17():
    number = 4257
    res = '1111111111110000010100001'
    assert gamma_encode(number) == res

# проверка функции gamma_encode на 1
def test_18():
    number = 1
    res = '0'
    assert gamma_encode(number) == res

# проверка функции gamma_encode на некорректный вход
def test_19():
   number = "ha-ha"
   with pytest.raises(TypeError):
        gamma_encode(number)

# проверка функции delta_compress_inverted_index
def test_20():
    inverted_index = create_inverted_index("test_files/test_posts_file.csv")
    result = delta_compress_inverted_index(inverted_index)
    assert len(result) == 266 and result["мы"] == [1666, 2627, 6250]

# проверка функции delta_compress_inverted_index - некорректный вход
def test_21():
    with pytest.raises(AttributeError):
        delta_compress_inverted_index(2)

# проверка функции gamma_compress_inverted_index
def test_22():
    inverted_index = create_inverted_index("test_files/test_posts_file.csv")
    delta_compressed_index = delta_compress_inverted_index(inverted_index)
    result = gamma_compress_inverted_index(delta_compressed_index)
    assert len(result) == 266 and result["мы"] == ['111111111101010000010', '11111111111001001000011', '1111111111110100001101010']


# проверка функции gamma_compress_inverted_index - некорректный вход
def test_23():
    with pytest.raises(AttributeError):
        gamma_compress_inverted_index(2)

# проверка функции save_index_to_file
def test_24():
    inverted_index = create_inverted_index('test_files/test_posts_file.csv')
    cur_path = os.path.dirname(__file__)
    abs_path = os.path.join(cur_path, 'test_files\\created_files\\saved_inverted_index.json')
    save_index_to_file(inverted_index, abs_path)
    assert os.path.exists('test_files/created_files/saved_inverted_index.json') == True

# проверка функции save_compressed_index_to_file - delta index
def test_25():
    inverted_index = create_inverted_index('test_files/test_posts_file.csv')
    delta_compressed_index = delta_compress_inverted_index(inverted_index)
    cur_path = os.path.dirname(__file__)
    abs_path = os.path.join(cur_path, 'test_files\\created_files\\saved_delta_compressed_index.json')
    save_compressed_index_to_file(delta_compressed_index, abs_path)
    assert os.path.exists("test_files/created_files/saved_delta_compressed_index.json") == True

# проверка функции save_compressed_index_to_file
def test_26():
    inverted_index = create_inverted_index('test_files/test_posts_file.csv')
    delta_compressed_index = delta_compress_inverted_index(inverted_index)
    gamma_compressed_index = gamma_compress_inverted_index(delta_compressed_index)
    cur_path = os.path.dirname(__file__)
    abs_path = os.path.join(cur_path, 'test_files\\created_files\\saved_gamma_compressed_index.json')
    save_compressed_index_to_file(gamma_compressed_index, abs_path)
    assert os.path.exists("test_files/created_files/saved_gamma_compressed_index.json") == True

# проверка функции load_index
def test_27():
    loaded_index = load_index('test_files/created_files/saved_gamma_compressed_index.json')
    assert len(loaded_index) == 266 and loaded_index["мы"] == {'111111111101010000010', '1111111111110100001101010', '11111111111001001000011'}

# проверка функции delta_decode
def test_28():
    delta_encoded_numbers = [4257, 11, 14, 11]
    res = [4257, 4268, 4282, 4293]
    assert delta_decode(delta_encoded_numbers) == res

# проверка функции gamma_decode
def test_29():
    gamma_encoded_number = "1111111111110000010100001"
    res = 4257
    assert gamma_decode(gamma_encoded_number) == res

# проверка функции load_and_decode_delta_index
def test_30():
    result = load_and_decode_delta_index('test_files/created_files/saved_delta_compressed_index.json')
    assert len(result) == 266 and result["мы"] == {1666, 4293, 10543}

# проверка функции load_and_decode_gamma_index
def test_31():
    result = load_and_decode_gamma_index('test_files/created_files/saved_gamma_compressed_index.json')
    assert len(result) == 266 and result["мы"] == {1666, 2627, 6250}

# проверка функции search
def test_32():
    query = 'Ректор СПбГУ'
    index = load_and_decode_gamma_index('gamma_compressed_index.json')
    res = {52242, 214}
    assert search(query, index) == res

# проверка функции search на пустую строку
def test_33():
    query = ''
    index = load_and_decode_gamma_index('gamma_compressed_index.json')
    assert search(query, index) == set()

# проверка функции search - некорреткный ввод
def test_34():
    query = [5, True, -156, {}, []]
    index = load_and_decode_gamma_index('gamma_compressed_index.json')
    for q in query:
        with pytest.raises(AttributeError):
            search(query, index)
    with pytest.raises(AttributeError):
            search('Ректор СПбГУ', [])

# проверка функции save_search_results_to_file
def test_35():
    query = "Ректор СПбГУ"
    gamma_loaded_index = load_and_decode_gamma_index('gamma_compressed_index.json')
    matching_post_ids = search(query, gamma_loaded_index)
    matching_messages = get_matching_messages('posts_SPbU.csv', matching_post_ids)
    save_search_results_to_file(matching_messages, 'search_results.txt')
    assert os.path.exists("search_results.txt") == True

# проверка функции get_matching_messages
def test_36():
    query = "Ректор СПбГУ"
    gamma_loaded_index = load_and_decode_gamma_index('gamma_compressed_index.json')
    matching_post_ids = search(query, gamma_loaded_index)
    matching_messages = get_matching_messages('posts_SPbU.csv', matching_post_ids)
    assert len(matching_messages) == 2