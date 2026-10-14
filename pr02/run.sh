#!/usr/bin/env bash
# ==============================================================================
# Практическая работа № 2. Вариант B
# Единый скрипт запуска и тестирования
# ==============================================================================
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=== [1/4] Генерация 50 файлов журналов в data/ ==="
python3 generate_logs.py

echo ""
echo "=== [2/4] Демонстрация работы report.sh ==="
echo "--- Тест 1: Все модули с ошибками ERROR ---"
./report.sh data ERROR

echo ""
echo "--- Тест 2: ТОП-3 модулей с предупреждениями WARN ---"
./report.sh --top 3 data WARN

echo ""
echo "--- Тест 3: Проверка обработки ошибок (каталог не найден) ---"
if ./report.sh nonexistent_dir ERROR 2>&1; then
    echo "Ошибка: скрипт должен был завершиться с кодом 1"
else
    echo "[OK] Скрипт корректно отклонил несуществующий каталог (код возврата != 0)."
fi

echo ""
echo "=== [3/4] Запуск hello.py ==="
python3 hello.py data/01.log

echo ""
echo "=== [4/4] Анализ системных вызовов (strace) ==="
if command -v strace &>/dev/null; then
    echo "Утилита strace обнаружена. Выполняем реальный сбор трассы:"
    strace -f -o trace.txt python3 hello.py data/01.log
    echo "Трасса сохранена в trace.txt"
    echo "Всего системных вызовов в trace.txt: $(wc -l < trace.txt)"
else
    echo "Утилита strace не установлена или ОС отлична от Linux. Используется эталонный trace.txt."
    echo "Строк в эталонном trace.txt: $(wc -l < trace.txt)"
fi

echo ""
echo "=== ПР-2 (Вариант B) успешно выполнена! ==="
