#!/usr/bin/env bash
# ==============================================================================
# Практическая работа № 2. Вариант B
# Скрипт report.sh: парсинг и агрегация логов по модулям
# ==============================================================================
set -euo pipefail

usage() {
    echo "Использование: $0 [--top N] <каталог_логов> <ERROR|WARN>"
    echo "       или:     $0 <каталог_логов> <ERROR|WARN> [--top N]"
    echo ""
    echo "Параметры:"
    echo "  <каталог_логов>  Путь к директории с файлами логов (*.log)"
    echo "  <ERROR|WARN>     Уровень логирования для фильтрации"
    echo "  --top N          Ограничить вывод первыми N модулями по частоте"
    echo "  -h, --help       Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 data ERROR"
    echo "  $0 --top 3 data WARN"
    exit 1
}

# Если аргументов нет, показываем справку и завершаем с кодом 1
if [[ $# -eq 0 ]]; then
    usage
fi

TOP_N=""
LOG_DIR=""
LOG_LEVEL=""

# Парсинг аргументов командной строки
while [[ $# -gt 0 ]]; do
    case "$1" in
        --top)
            if [[ -z "${2:-}" ]] || ! [[ "$2" =~ ^[0-9]+$ ]]; then
                echo "Ошибка: параметр --top требует положительное число." >&2
                exit 1
            fi
            TOP_N="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            if [[ -z "$LOG_DIR" ]]; then
                LOG_DIR="$1"
            elif [[ -z "$LOG_LEVEL" ]]; then
                LOG_LEVEL="$1"
            else
                echo "Ошибка: неожиданный аргумент '$1'" >&2
                usage
            fi
            shift
            ;;
    esac
done

# Проверка обязательных аргументов
if [[ -z "$LOG_DIR" ]] || [[ -z "$LOG_LEVEL" ]]; then
    echo "Ошибка: необходимо указать каталог и уровень логов." >&2
    usage
fi

# Проверка существования каталога
if [[ ! -d "$LOG_DIR" ]]; then
    echo "Ошибка: каталог '$LOG_DIR' не существует или не является директорией." >&2
    exit 1
fi

# Нормализация уровня (приводим к верхнему регистру)
LOG_LEVEL="$(echo "$LOG_LEVEL" | tr '[:lower:]' '[:upper:]')"
if [[ "$LOG_LEVEL" != "ERROR" && "$LOG_LEVEL" != "WARN" ]]; then
    echo "Ошибка: уровень логов должен быть ERROR или WARN (указано: '$LOG_LEVEL')." >&2
    exit 1
fi

# Проверка наличия файлов в каталоге
shopt -s nullglob
LOG_FILES=("$LOG_DIR"/*.log "$LOG_DIR"/*.txt)
shopt -u nullglob

if [[ ${#LOG_FILES[@]} -eq 0 ]]; then
    echo "Предупреждение: в каталоге '$LOG_DIR' не найдено файлов *.log или *.txt." >&2
    exit 0
fi

# Сбор и агрегация данных:
# 1. grep ищет строки с заданным уровнем
# 2. sed/awk извлекает значение после 'module='
# 3. sort | uniq -c считает частоту каждого модуля
# 4. sort -rn сортирует по убыванию
AGGREGATED=$(awk -v lvl="$LOG_LEVEL" '
    $0 ~ lvl {
        for (i = 1; i <= NF; i++) {
            if ($i ~ /^module=/) {
                split($i, arr, "=")
                count[arr[2]]++
            }
        }
    }
    END {
        for (mod in count) {
            printf "%d %s\n", count[mod], mod
        }
    }
' "${LOG_FILES[@]}" | sort -rn)

if [[ -z "$AGGREGATED" ]]; then
    echo "Сообщений уровня $LOG_LEVEL в каталоге '$LOG_DIR' не обнаружено."
    exit 0
fi

# Если задан --top N, обрезаем вывод
if [[ -n "$TOP_N" ]]; then
    AGGREGATED=$(echo "$AGGREGATED" | head -n "$TOP_N")
fi

# Форматированный вывод красивой таблицы
echo "==========================================="
echo " Отчет по событиям: $LOG_LEVEL"
echo " Каталог: $LOG_DIR"
if [[ -n "$TOP_N" ]]; then
    echo " Режим: ТОП-$TOP_N"
fi
echo "==========================================="
printf "%-18s | %-15s\n" "Модуль" "Число сообщений"
echo "-------------------+-----------------------"

while read -r count mod; do
    printf "%-18s | %-15s\n" "$mod" "$count"
done <<< "$AGGREGATED"

echo "==========================================="
