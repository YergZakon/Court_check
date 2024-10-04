import json
import os

def fix_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json') and not filename.endswith('_analysis.json'):
            file_path = os.path.join(directory, filename)
            fix_json_file(file_path)

def fix_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    fixed_data = []
    for item in data:
        fixed_item = {}
        for key, value in item.items():
            fixed_key = fix_key(key)
            if fixed_key in [
                "суть_спора", "требования_истца", "аргументы_истца",
                "позиция_ответчика", "правовая_позиция_суда", "итоговое_решение"
            ]:
                fixed_item[fixed_key] = value
        
        if len(fixed_item) == 6:  # Убедимся, что у нас есть все необходимые ключи
            fixed_data.append(fixed_item)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(fixed_data, file, ensure_ascii=False, indent=2)
    
    print(f"Файл {file_path} исправлен. Обработано записей: {len(fixed_data)}")

def fix_key(key):
    key_mapping = {
        "суть спора": "суть_спора",
        "требования истца": "требования_истца",
        "аргументы истца": "аргументы_истца",
        "позиция ответчика": "позиция_ответчика",
        "правовая позиция суда": "правовая_позиция_суда",
        "итоговое решение": "итоговое_решение"
    }
    return key_mapping.get(key.lower(), key)

if __name__ == "__main__":
    directory = "."  # Текущая директория, измените при необходимости
    fix_json_files(directory)
    print("Исправление JSON-файлов завершено.")
