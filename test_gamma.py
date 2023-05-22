import pytest
from gamma import *

# проверка функции tokenize
def test_1():
    text = "🏆Покоряем    вершину !! [club202446718|«ТехноОлимпа»]...     "
    result = tokenize(text)
    assert result == ['покоряем', 'вершину', 'club202446718', 'техноолимпа']

# проверка функции tokenize на неправльный вход
def test_2():
    text = 255
    with pytest.raises(AttributeError):
        tokenize(text)

# проверка функции create_inverted_index
def test_3():
    result = create_inverted_index("test_files/very_small_file.csv")
    true =  {'покоряем': {4293}, 'вершину': {4293}, 'club202446718': {4293},
                     'техноолимпа': {4293}, 'мы': {2447, 4293, 10543}, 'карточкивожатого': {10543},
                     'во': {10543}, 'вторник': {10543}, 'узнали': {10543}, 'собрание': {2447},
                     'english': {2447}, 'word': {2447}}
    assert result == true

# проверка функции create_inverted_index на неправильный вход - несуществующий файл
def test_4():
    with pytest.raises(FileNotFoundError):
        create_inverted_index("test_files/no_existing_file.csv")

# # проверка функции create_inverted_index на неправильный вход - рандомное число вместо строки
def test_5():
    with pytest.raises(OSError):
        create_inverted_index(23534)

# проверка функции delta_encode
def test_6():
    numbers = [7, 17]
    res = [7, 10]
    assert delta_encode(numbers) == res

# проверка функции delta_encode на неверный вход
def test_7():
    numbers = "ha-ha"
    with pytest.raises(TypeError):
        delta_encode(numbers)

# проверка функции create_inverted_index на пустой файл
def test_8():
    result = create_inverted_index("test_files/empty_file.csv")
    assert len(result) == 0

# проверка функции create_inverted_index на некорректный файл (без поля text)
def test_9():
    with pytest.raises(KeyError):
        create_inverted_index("test_files/uncorrect_file.csv")

# проверка функции delta_decode
def test_10():
    numbers = [7, 10]
    res = [7, 17]
    assert delta_decode(numbers) == res

# проверка функции delta_decode на неверный вход
def test_11():
    numbers = "ha-ha"
    with pytest.raises(TypeError):
        delta_decode(numbers)

# проверка функции unary
def test_12():
    number = 5
    res = '0000'
    assert unary(number) == res

# проверка функции unary на неверный вход
def test_13():
    number = "ha-ha"
    with pytest.raises(TypeError):
        unary(number)

# проверка функции gamma_encode
def test_14():
    numbers = 10
    res = "0001010"
    assert gamma_encode(numbers) == res

# проверка функции gamma_encode на неверный вход
def test_15():
    numbers = "ha-ha"
    with pytest.raises(TypeError):
        gamma_encode(numbers)

# проверка функции gamma_decode
def test_16():
    numbers = "0001010"
    res = 10
    assert gamma_decode(numbers) == res


# проверка функции gamma_decode на неверный вход
def test_17():
    numbers = 25
    with pytest.raises(AttributeError):
        gamma_decode(numbers)

# проверка функции gamma_encode_bitvector
def test_18():
    numbers = [7, 10]
    res = "001110001010"
    assert str(gamma_encode_bitvector(numbers)) == res


# проверка функции gamma_encode_bitvector на неверный вход
def test_19():
    numbers = "ha-ha"
    with pytest.raises(TypeError):
        gamma_encode_bitvector(numbers)

# проверка функции gamma_decode_bitvector
def test_20():
    numbers = "001110001010"
    res = [7, 10]
    assert gamma_decode_bitvector(numbers) == res

# проверка функции search
def test_21():
    query = 'Вершину на'
    inverted_index = create_inverted_index("test_files/test_search_file.csv")
    matching_post_ids = search(query, inverted_index)
    res = {1, 2}
    assert matching_post_ids == res

# проверка функции search на пустую строку
def test_22():
    query = ''
    inverted_index = create_inverted_index("test_files/test_search_file.csv")
    matching_post_ids = search(query, inverted_index)
    assert matching_post_ids == set()

# проверка функции search - некорреткный ввод
def test_23():
    query = [5, True, -156, {}, []]
    inverted_index = create_inverted_index("test_files/test_search_file.csv")
    for q in query:
        with pytest.raises(AttributeError):
            search(query, inverted_index)
    with pytest.raises(AttributeError):
            search('Ректор СПбГУ', [])