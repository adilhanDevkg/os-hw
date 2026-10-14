#!/usr/bin/env bash
# ==============================================================================
# Практическая работа № 4. Вариант B
# Единый скрипт запуска и проверки бенчмарков
# ==============================================================================
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=== [1/4] Генерация входного массива numbers.txt (2 млн чисел для быстрого и надежного теста) ==="
python3 generate_numbers.py 2000000

echo ""
echo "=== [2/4] Запуск CPU-bound бенчмарка (Суммирование: 1 поток vs 4 потока vs 4 процесса) ==="
python3 sum_benchmark.py

echo ""
echo "=== [3/4] Запуск I/O-bound бенчмарка (20 URL-запросов: посл. vs ThreadPool vs ProcessPool) ==="
python3 io_benchmark.py

echo ""
echo "=== [4/4] Запуск теста разделения памяти (memory_sharing_demo.py) ==="
python3 memory_sharing_demo.py

echo ""
echo "=== Практическая работа № 4 (Вариант B) успешно завершена! ==="
