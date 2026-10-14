#!/usr/bin/env bash
# ==============================================================================
# Практическая работа № 6. Вариант B
# Единый скрипт запуска и проверки задач синхронизации
# ==============================================================================
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=== [1/5] Программа с состоянием гонки vs Исправленная версия ==="
echo "--- Гонка (race_condition_demo.py) ---"
python3 race_condition_demo.py
echo ""
echo "--- Устранение гонки (race_condition_fixed.py) ---"
python3 race_condition_fixed.py

echo ""
echo "=== [2/5] Производитель-Потребитель на СЕМАФОРАХ (prod_cons_sem.py) ==="
python3 prod_cons_sem.py

echo ""
echo "=== [3/5] Производитель-Потребитель на УСЛОВНОЙ ПЕРЕМЕННОЙ (prod_cons_cv.py) ==="
python3 prod_cons_cv.py

echo ""
echo "=== [4/5] Переиспользуемый барьер (barrier_demo.py) ==="
python3 barrier_demo.py

echo ""
echo "=== [5/5] Демонстрация проблемы IF vs WHILE (spurious_wakeup_demo.py) ==="
python3 spurious_wakeup_demo.py

echo ""
echo "=== Практическая работа № 6 (Вариант B) успешно завершена! ==="
