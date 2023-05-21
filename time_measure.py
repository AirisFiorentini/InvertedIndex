import time
from main import create_inverted_index 
from main import delta_compress_inverted_index 
from main import gamma_compress_inverted_index
from main import save_index_to_file

# Записываем текущее время
start_time = time.time()

# Выполняем индексацию данных
inverted_index = create_inverted_index('posts_SPbU.csv')
delta_compressed_index = delta_compress_inverted_index(inverted_index)
gamma_compressed_index = gamma_compress_inverted_index(delta_compressed_index)

# Сохраняем сжатый индекс в файл
#save_index_to_file(gamma_compressed_index, 'compressed_index.json')

# Записываем текущее время и вычитаем из него время начала, чтобы получить общее время выполнения
end_time = time.time()
indexing_time = end_time - start_time

print(f"Indexing time: {indexing_time} seconds")

