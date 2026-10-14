#!/usr/bin/env python3
"""
Генерация файла numbers.txt с целыми числами для ПР-4.
"""
import os
import sys
import random

def generate(filename: str, count: int = 5_000_000):
    print(f"Генерация {count:,} чисел в файл {filename}...")
    chunk_size = 100_000
    with open(filename, "w", encoding="utf-8") as f:
        remaining = count
        while remaining > 0:
            current_batch = min(remaining, chunk_size)
            lines = [str(random.randint(1, 1000)) + "\n" for _ in range(current_batch)]
            f.writelines(lines)
            remaining -= current_batch
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    print(f"[OK] Файл {filename} успешно создан (размер: {size_mb:.2f} МБ)")

if __name__ == "__main__":
    count = 5_000_000
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    target = os.path.join(os.path.dirname(__file__), "numbers.txt")
    generate(target, count)
