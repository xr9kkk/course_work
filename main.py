import hashlib
import mmh3
import time
import os
import json
import csv
from collections import defaultdict
import matplotlib.pyplot as plt
from scipy.stats import chisquare
from typing import Dict, List, Tuple, Callable, Any
from generate_test_files import generate_test_files

class HashFunctionTester:
    def __init__(self):
        self.results = {}
        self.test_data = {}
        
    def load_test_files(self) -> None:
        """Загрузка всех тестовых данных из папки test_data"""
        if not os.path.exists('test_data'):
            print("Тестовые файлы не найдены. Генерация...")
            generate_test_files()
        
        print("Загрузка тестовых данных из файлов...")
        
        # Получаем список всех файлов в папке test_data
        test_files = [f for f in os.listdir('test_data') if os.path.isfile(os.path.join('test_data', f))]
        
        for filename in test_files:
            file_path = os.path.join('test_data', filename)
            try:
                if filename.endswith('.txt'):
                    with open(file_path, 'r') as f:
                        # Для текстовых файлов читаем построчно
                        data = [line.strip() for line in f]
                        self.test_data[filename] = data
                        
                elif filename.endswith('.csv'):
                    with open(file_path, 'r', newline='') as f:
                        reader = csv.reader(f)
                        # Пропускаем заголовок если есть
                        if filename.startswith('csv_data'):
                            next(reader)
                        data = [tuple(row) for row in reader]
                        self.test_data[filename] = data
                        
                elif filename.endswith('.json'):
                    with open(file_path, 'r') as f:
                        json_data = json.load(f)
                        if isinstance(json_data, list):
                            # Преобразуем JSON объекты в кортежи
                            data = [tuple(item.values()) for item in json_data]
                            self.test_data[filename] = data
                            
                print(f"  Загружен файл: {filename} ({len(self.test_data[filename])} элементов)")
                
            except Exception as e:
                print(f"  Ошибка при загрузке файла {filename}: {str(e)}")
                continue

    def define_hash_functions(self) -> Dict[str, Callable]:
        """Определение тестируемых хеш-функций"""
        return {
            'MD5': lambda x: int(hashlib.md5(str(x).encode()).hexdigest(), 16),
            'SHA-1': lambda x: int(hashlib.sha1(str(x).encode()).hexdigest(), 16),
            'SHA-256': lambda x: int(hashlib.sha256(str(x).encode()).hexdigest(), 16),
            'MurmurHash': lambda x: mmh3.hash(str(x)),
            'Python hash': hash,
            'Simple hash': self.simple_hash,
        }
    
    def simple_hash(self, key) -> int:
        """Простая хеш-функция для сравнения"""
        if isinstance(key, (tuple, list)):
            return sum(hash(str(x)) for x in key) % 1000000
        return hash(str(key)) % 1000000

    def test_functions(self, hash_functions: Dict[str, Callable]) -> None:
        """Основной метод тестирования хеш-функций"""
        if not self.test_data:
            raise ValueError("Нет тестовых данных для проверки")
            
        print("\nНачало тестирования хеш-функций...")
        
        for filename, data in self.test_data.items():
            print(f"\nТестирование файла: {filename}")
            self.results[filename] = {}
            
            for func_name, func in hash_functions.items():
                print(f"  Функция: {func_name}", end=' ', flush=True)
                start_time = time.time()
                
                try:
                    # Вычисляем хеши для всех элементов
                    hashes = []
                    for item in data:
                        try:
                            hashes.append(func(item))
                        except Exception as e:
                            print(f"\nОшибка при хешировании элемента {item}: {str(e)}")
                            hashes.append(0)  # Используем 0 для ошибок
                    
                    # Анализ результатов
                    hash_counts = defaultdict(int)
                    for h in hashes:
                        hash_counts[h] += 1
                    
                    collisions = sum(cnt - 1 for cnt in hash_counts.values() if cnt > 1)
                    collision_rate = collisions / len(data)
                    unique_hashes = len(hash_counts)
                    chi2, p_value = self.test_uniformity(list(hash_counts.values()))
                    
                    # Сохранение результатов
                    self.results[filename][func_name] = {
                        'time': time.time() - start_time,
                        'collisions': collisions,
                        'collision_rate': collision_rate,
                        'unique_hashes': unique_hashes,
                        'chi2': chi2,
                        'p_value': p_value,
                        'hash_counts': hash_counts
                    }
                    
                    print(f"| Время: {self.results[filename][func_name]['time']:.4f}s | Коллизии: {collisions}", end='')
                    
                except Exception as e:
                    print(f"\nОшибка при тестировании {func_name} на {filename}: {str(e)}")
                    continue

    def test_uniformity(self, counts: List[int]) -> Tuple[float, float]:
        """Тест хи-квадрат на равномерность распределения"""
        expected = sum(counts) / len(counts) if counts else 0
        if expected == 0:
            return (0, 0)
        return chisquare(counts)

    def visualize_results(self) -> None:
        """Визуализация результатов тестирования"""
        if not self.results:
            print("Нет результатов для визуализации")
            return
            
        print("\nСоздание графиков...")
        os.makedirs('results', exist_ok=True)
        
        # Создаем сводный график по всем файлам
        self._create_summary_plots()
        
        # Создаем графики для каждого файла
        for filename, func_results in self.results.items():
            self._create_file_plots(filename, func_results)
        
        print("Графики сохранены в папке 'results'")

    def _create_summary_plots(self):
        """Создает сводные графики по всем тестам"""
        # Сводный график времени выполнения
        plt.figure(figsize=(15, 8))
        for filename, func_results in self.results.items():
            times = [res['time'] for res in func_results.values()]
            plt.plot(list(func_results.keys()), times, label=filename)
        
        plt.title('Сравнение времени выполнения хеш-функций')
        plt.ylabel('Время (секунды)')
        plt.xlabel('Хеш-функция')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig('results/summary_time_comparison.png')
        plt.close()
        
        # Сводный график коллизий
        plt.figure(figsize=(15, 8))
        for filename, func_results in self.results.items():
            collisions = [res['collisions'] for res in func_results.values()]
            plt.plot(list(func_results.keys()), collisions, label=filename)
        
        plt.title('Сравнение количества коллизий')
        plt.ylabel('Коллизии')
        plt.xlabel('Хеш-функция')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig('results/summary_collisions_comparison.png')
        plt.close()

    def _create_file_plots(self, filename: str, func_results: Dict[str, Dict]):
        """Создает графики для конкретного файла"""
        clean_name = os.path.splitext(filename)[0]
        
        plt.figure(figsize=(15, 10))
        
        # График времени выполнения
        plt.subplot(2, 2, 1)
        times = [res['time'] for res in func_results.values()]
        plt.bar(func_results.keys(), times)
        plt.title(f'Время выполнения ({clean_name})')
        plt.ylabel('Секунды')
        plt.xticks(rotation=45)
        
        # График коллизий
        plt.subplot(2, 2, 2)
        collisions = [res['collisions'] for res in func_results.values()]
        plt.bar(func_results.keys(), collisions)
        plt.title(f'Количество коллизий ({clean_name})')
        plt.ylabel('Коллизии')
        plt.xticks(rotation=45)
        
        # График процента коллизий
        plt.subplot(2, 2, 3)
        collision_rates = [res['collision_rate'] * 100 for res in func_results.values()]
        plt.bar(func_results.keys(), collision_rates)
        plt.title(f'Процент коллизий ({clean_name})')
        plt.ylabel('%')
        plt.xticks(rotation=45)
        
        # График p-value теста хи-квадрат
        plt.subplot(2, 2, 4)
        p_values = [res['p_value'] for res in func_results.values()]
        plt.bar(func_results.keys(), p_values)
        plt.title(f'p-value теста равномерности ({clean_name})')
        plt.ylabel('p-value')
        plt.xticks(rotation=45)
        plt.axhline(y=0.05, color='r', linestyle='--')
        
        plt.tight_layout()
        plt.savefig(f'results/{clean_name}_results.png')
        plt.close()

    def save_results_to_csv(self) -> None:
        """Сохранение результатов в CSV файл"""
        if not self.results:
            print("Нет результатов для сохранения")
            return
            
        os.makedirs('results', exist_ok=True)
        
        with open('results/test_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Filename', 'Function', 'Time (s)', 'Collisions', 
                '% Collisions', 'Unique Hashes', 'Chi-square', 'p-value'
            ])
            
            for filename, func_results in self.results.items():
                for func_name, res in func_results.items():
                    writer.writerow([
                        filename,
                        func_name,
                        f"{res['time']:.6f}",
                        res['collisions'],
                        f"{res['collision_rate'] * 100:.2f}",
                        res['unique_hashes'],
                        f"{res['chi2']:.2f}",
                        f"{res['p_value']:.4f}"
                    ])
        
        print("Результаты сохранены в results/test_results.csv")

def main():
    """Основная функция программы"""
    tester = HashFunctionTester()
    
    try:
        # 1. Загрузка тестовых данных
        print("=== Загрузка тестовых данных ===")
        tester.load_test_files()
        
        # 2. Определение хеш-функций
        print("\n=== Определение хеш-функций ===")
        hash_functions = tester.define_hash_functions()
        
        # 3. Тестирование
        print("\n=== Тестирование хеш-функций ===")
        tester.test_functions(hash_functions)
        
        # 4. Визуализация
        print("\n=== Визуализация результатов ===")
        tester.visualize_results()
        
        # 5. Сохранение
        tester.save_results_to_csv()
        
        print("\nТестирование завершено!")
    except Exception as e:
        print(f"\nПроизошла ошибка: {str(e)}")
        print("Попробуйте удалить папку test_data и запустить программу снова")

if __name__ == "__main__":
    main()