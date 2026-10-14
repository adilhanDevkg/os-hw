#!/usr/bin/env bash
# ==============================================================================
# Практическая работа № 5. Вариант B
# Единый скрипт запуска и тестирования симулятора планирования CPU
# ==============================================================================
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=== [1/4] Автоматическая проверка с эталоном из методички (set1.txt) ==="
python3 test_sched.py

echo ""
echo "=== [2/4] Запуск RR (q = 3) на контрольном наборе set1.txt ==="
python3 sched.py --algo rr --quantum 3 set1.txt

echo ""
echo "=== [3/4] Сравнение всех алгоритмов на set1.txt и set3.txt ==="
echo "--- set1.txt ---"
python3 sched.py --all set1.txt
echo ""
echo "--- set3.txt (эффект конвоя) ---"
python3 sched.py --all set3.txt

echo ""
echo "=== [4/4] Исследование кванта RR (1..10) на наборе set2.txt ==="
python3 sched.py --sweep-rr set2.txt

echo ""
echo "=== Практическая работа № 5 (Вариант B) успешно завершена! ==="
