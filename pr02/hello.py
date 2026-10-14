#!/usr/bin/env python3
"""
Простая программа hello.py: открывает файл, читает его содержимое и выводит его размер в байтах.
Используется для профилирования системных вызовов через strace.
"""
import sys
import os

def main():
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        # По умолчанию читаем файл из data/01.log или создаем тестовый
        target_path = os.path.join(os.path.dirname(__file__), "data", "01.log")
        if not os.path.exists(target_path):
            target_path = os.path.abspath(__file__)

    try:
        with open(target_path, "rb") as f:
            content = f.read()
            size = len(content)
        print(f"Файл: {os.path.basename(target_path)}, Размер: {size} байт")
    except Exception as e:
        print(f"Ошибка при чтении файла {target_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
