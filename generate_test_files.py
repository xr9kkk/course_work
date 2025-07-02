import os
import random
import string
import json
from datetime import datetime
import csv

def generate_test_files():
    """Генерация всех тестовых файлов для проверки хеш-функций"""
    os.makedirs('test_data', exist_ok=True)
    
    # 1. Числовые данные
    generate_number_files()
    
    # 2. Текстовые данные
    generate_text_files()
    
    # 3. Комбинированные данные
    generate_combined_files()
    
    # 4. Специальные случаи
    generate_edge_cases()
    
    print("Все тестовые файлы созданы в папке test_data")

def generate_number_files():
    """Генерация файлов с числовыми данными"""
    sizes = [100, 1000, 10000, 100000]  # Разные размеры данных
    
    for size in sizes:
        # Случайные целые числа
        with open(f'test_data/numbers_{size}.txt', 'w') as f:
            f.write('\n'.join(str(random.randint(-1000000, 1000000)) for _ in range(size)))
        
        # Последовательные числа (для проверки на паттерны)
        with open(f'test_data/sequential_{size}.txt', 'w') as f:
            f.write('\n'.join(str(i) for i in range(size)))
        
        # Числа с дубликатами
        with open(f'test_data/duplicates_{size}.txt', 'w') as f:
            nums = [random.randint(1, 100) for _ in range(size)]
            f.write('\n'.join(map(str, nums)))

def generate_text_files():
    """Генерация файлов с текстовыми данными"""
    word_list = load_english_words()  # Загрузка реальных английских слов
    
    sizes = [100, 1000, 5000]  # Разные размеры данных
    
    for size in sizes:
        # Случайные строки
        with open(f'test_data/random_strings_{size}.txt', 'w') as f:
            for _ in range(size):
                length = random.randint(3, 50)
                chars = random.choices(string.ascii_letters + string.digits, k=length)
                f.write(''.join(chars) + '\n')
        
        # Реальные слова
        with open(f'test_data/words_{size}.txt', 'w') as f:
            f.write('\n'.join(random.choices(word_list, k=size)))
        
        # UUIDs
        with open(f'test_data/uuids_{size}.txt', 'w') as f:
            for _ in range(size):
                f.write(str(uuid.uuid4()) + '\n')

def generate_combined_files():
    """Генерация файлов с комбинированными данными"""
    sizes = [100, 1000, 5000]
    
    for size in sizes:
        # JSON данные
        with open(f'test_data/json_data_{size}.json', 'w') as f:
            data = [{
                "id": random.randint(1, 100000),
                "name": ''.join(random.choices(string.ascii_letters, k=10)),
                "value": random.random(),
                "timestamp": str(datetime.now())
            } for _ in range(size)]
            json.dump(data, f)
        
        # CSV данные
        with open(f'test_data/csv_data_{size}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'value', 'active'])
            for i in range(size):
                writer.writerow([
                    i + 1,
                    ''.join(random.choices(string.ascii_uppercase, k=5)),
                    round(random.uniform(10.0, 100.0), 2),
                    random.choice([True, False])
                ])

def generate_edge_cases():
    """Генерация файлов со специальными случаями"""
    # Пустые файлы
    open('test_data/empty.txt', 'w').close()
    
    # Очень длинные строки
    with open('test_data/long_strings.txt', 'w') as f:
        f.write('a' * 10000 + '\n')
        f.write('b' * 50000 + '\n')
        f.write(' ' * 100000 + '\n')  # Только пробелы
    
    
    # Очень большие числа
    with open('test_data/big_numbers.txt', 'w') as f:
        nums = [
            2**64,
            -2**63,
            3.14159265358979323846264338327950288419716939937510,
            1.7976931348623157e+308  # Max float
        ]
        f.write('\n'.join(map(str, nums)))

def load_english_words():
    """Загрузка списка английских слов (если доступен)"""
    try:
        import nltk
        nltk.download('words')
        from nltk.corpus import words
        return words.words()
    except:
        # Возвращаем встроенный список, если nltk не доступен
        return ['apple', 'banana', 'cherry', 'date', 'elderberry', 
                'fig', 'grape', 'honeydew', 'kiwi', 'lemon']

if __name__ == "__main__":
    import uuid  # Импорт здесь, чтобы не требовалось для основных функций
    generate_test_files()