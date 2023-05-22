import pytest
from delta import *

# проверка функции tokenize
def test_1():
    text = "🏆Покоряем    вершину !! [club202446718|«ТехноОлимпа»]...     "
    result = tokenize(text)
    assert result == ['покоряем', 'вершину', 'club202446718', 'техноолимпа']

# проверка функции tokenize на неправильный вход
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

# проверка функции delta_encode_bitvector
def test_6():
    numbers = [7, 17]
    res = "0111100100010"
    assert str(delta_encode_bitvector(numbers)) == res

# проверка функции delta_encode_bitvector на неверный вход
def test_7():
    numbers = "ha-ha"
    with pytest.raises(TypeError):
        delta_encode_bitvector(numbers)

# проверка функции create_inverted_index на пустой файл
def test_8():
    result = create_inverted_index("test_files/empty_file.csv")
    assert len(result) == 0

# проверка функции create_inverted_index на некорректный файл (без поля text)
def test_9():
    with pytest.raises(KeyError):
        create_inverted_index("test_files/uncorrect_file.csv")

# проверка функции delta_decode_bitvector
def test_10():
    numbers = [7, 17]
    enc_numbers = delta_encode_bitvector(numbers)
    res = [7, 17]
    assert delta_decode_bitvector(enc_numbers) == res

# проверка функции delta_decode_bitvector на неверный вход
def test_11():
    numbers = "ha-ha"
    with pytest.raises(AttributeError):
        delta_decode_bitvector(numbers)

# проверка функции delta_decode_bitvector_compressed
def test_12():
    inverted_index = create_inverted_index("test_files/very_small_file.csv")
    delta_compressed_index = delta_encode_bitvector_compressed(inverted_index)
    res = delta_decode_bitvector_compressed(delta_compressed_index)
    print(res)
    true = {'покоряем': [4293], 'вершину': [4293], 'club202446718': [4293], 'техноолимпа': [4293], 
            'мы': [2447, 4293, 10543], 'карточкивожатого': [10543], 'во': [10543], 'вторник': [10543], 
            'узнали': [10543], 'собрание': [2447], 'english': [2447], 'word': [2447]}
    assert res == true

# проверка функции create_inverted_index очень большой файл (500 Мб)
def test_13():
    result = create_inverted_index("test_files/very_big_file.csv")
    assert len(result) == 805866