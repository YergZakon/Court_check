import json
import os
from collections import Counter

def validate_json_files(directory):
    results = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            results[filename] = validate_json_file(file_path)
    return results

def validate_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        if not isinstance(data, list):
            return {"valid": False, "error": "Файл должен содержать список объектов"}
        
        if len(data) == 0:
            return {"valid": False, "error": "Файл пуст"}
        
        expected_keys = [
            "суть_спора", "требования_истца", "аргументы_истца",
            "позиция_ответчика", "правовая_позиция_суда", "итоговое_решение"
        ]
        
        key_counts = Counter()
        for case in data:
            if not isinstance(case, dict):
                return {"valid": False, "error": "Каждый элемент списка должен быть объектом"}
            
            for key in case.keys():
                key_counts[key.lower()] += 1
        
        missing_keys = [key for key in expected_keys if key_counts[key.lower()] == 0]
        extra_keys = [key for key in key_counts if key.lower() not in [k.lower() for k in expected_keys]]
        
        if missing_keys or extra_keys:
            return {
                "valid": False,
                "missing_keys": missing_keys,
                "extra_keys": extra_keys,
                "key_counts": dict(key_counts)
            }
        
        return {"valid": True, "case_count": len(data), "key_counts": dict(key_counts)}
    
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"Невалидный JSON: {str(e)}"}
    except Exception as e:
        return {"valid": False, "error": f"Ошибка при чтении файла: {str(e)}"}

if __name__ == "__main__":
    directory = "."  # Текущая директория, измените при необходимости
    results = validate_json_files(directory)
    
    print("Результаты валидации JSON-файлов:")
    for filename, result in results.items():
        print(f"\n{filename}:")
        if result['valid']:
            print(f"  Валидный: Да")
            print(f"  Количество дел: {result['case_count']}")
            print("  Количество ключей:")
            for key, count in result['key_counts'].items():
                print(f"    {key}: {count}")
        else:
            print(f"  Валидный: Нет")
            print(f"  Ошибка: {result.get('error', 'Неизвестная ошибка')}")
            if 'missing_keys' in result:
                print(f"  Отсутствующие ключи: {', '.join(result['missing_keys'])}")
            if 'extra_keys' in result:
                print(f"  Лишние ключи: {', '.join(result['extra_keys'])}")
            if 'key_counts' in result:
                print("  Количество ключей:")
                for key, count in result['key_counts'].items():
                    print(f"    {key}: {count}")
