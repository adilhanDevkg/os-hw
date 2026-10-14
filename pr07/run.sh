#!/usr/bin/env bash
# ==============================================================================
# Практическая работа № 7. Вариант B
# Единый скрипт запуска и проверки IPC
# ==============================================================================
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=== [1/3] Тестирование ИМЕНОВАННЫХ КАНАЛОВ (FIFO Клиент-Сервер) ==="
python3 fifo_server.py &
SERVER_FIFO_PID=$!
sleep 0.3

echo "Запуск клиентов по очереди:"
python3 fifo_client.py client_1 "15 * 4 + 10"
python3 fifo_client.py client_2 "(100 - 25) / 5"
python3 fifo_client.py client_3 "2 ** 8 + 4"

# Завершение FIFO сервера
echo "SHUTDOWN" > /tmp/calc_request.fifo || kill -TERM "$SERVER_FIFO_PID" 2>/dev/null || true
wait "$SERVER_FIFO_PID" 2>/dev/null || true
echo "[✓] FIFO-сервер успешно завершил работу."

echo ""
echo "=== [2/3] Тестирование UNIX-ДОМЕННЫХ СОКЕТОВ (UDS Клиент-Сервер с параллельными клиентами) ==="
python3 uds_server.py &
SERVER_UDS_PID=$!
sleep 0.3

echo "Параллельный запуск нескольких клиентов:"
python3 uds_client.py "50 * 5" &
PID_C1=$!
python3 uds_client.py "2 ** 16 - 1" &
PID_C2=$!
python3 uds_client.py "1000 / (4 + 6)" &
PID_C3=$!

wait "$PID_C1" "$PID_C2" "$PID_C3"

kill -TERM "$SERVER_UDS_PID" 2>/dev/null || true
wait "$SERVER_UDS_PID" 2>/dev/null || true
echo "[✓] UDS-сервер успешно завершил работу."

echo ""
echo "=== [3/3] Тестирование Shared Memory vs Pipe (10^7 чисел = 40 МБ) ==="
python3 shm_vs_pipe.py

echo ""
echo "=== Проверка чистоты системы после завершения ==="
echo "Проверка остаточных сокетов и каналов в /tmp:"
ls -la /tmp/calc_* 2>/dev/null || echo "Остаточных файлов FIFO и UDS сокетов не обнаружено (чисто)."

echo ""
echo "=== Практическая работа № 7 (Вариант B) успешно завершена! ==="
