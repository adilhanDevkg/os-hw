#!/usr/bin/env bash
# ==============================================================================
# Практическая работа № 3. Вариант B
# Единый скрипт запуска и проверки всех заданий
# ==============================================================================
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=== [1/5] Запуск ptree.py (Дерево процессов по /proc) ==="
python3 ptree.py

echo ""
echo "=== [2/5] Запуск runner.py (Параллельный запуск команд через fork+exec) ==="
python3 runner.py -n 3 python3 -c 'import os, time; print(f"Hello from child PID {os.getpid()}"); time.sleep(0.3)'

echo ""
echo "=== [3/5] Запуск zombie.py (Демонстрация состояния Z) ==="
python3 zombie.py

echo ""
echo "=== [4/5] Запуск orphan.py (Демонстрация процесса-сироты) ==="
python3 orphan.py

echo ""
echo "=== [5/5] Запуск cow_demo.py (Демонстрация Copy-On-Write) ==="
python3 cow_demo.py

echo ""
echo "=== Практическая работа № 3 (Вариант B) успешно завершена! ==="
