import os


def compare_file_sizes(file1, file2):
    size1 = os.path.getsize(file1)
    size2 = os.path.getsize(file2)
    
    print(f"Size of {file1}: {size1} bytes")
    print(f"Size of {file2}: {size2} bytes")
    
    if size1 > size2:
        print(f"{file1} is larger than {file2} by {size1 - size2} bytes")
        print(f"{file1} is {size1 / size2} times larger than {file2}")
        print(f"{file2} is {size2 / size1} times smaller than {file1}")
    elif size2 > size1:
        print(f"{file2} is larger than {file1} by {size2 - size1} bytes")
        print(f"{file2} is {size2 / size1} times larger than {file1}")
        print(f"{file1} is {size1 / size2} times smaller than {file2}")
    else:
        print("Both files are of the same size")

# Call Example: compare_file_sizes('inverted_index.json', 'gamma_compressed_index.json')
compare_file_sizes('inverted_index.json', 'delta_compressed_index.json'), print()
compare_file_sizes('inverted_index.json', 'gamma_compressed_index.json')