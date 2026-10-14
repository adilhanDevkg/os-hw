#!/usr/bin/env python3
"""
Практическая работа № 7. Вариант B. Задание 1.
fifo_client.py: Клиент на именованных каналах (FIFO).
Отправляет математическое выражение серверу и ожидает ответ через персональный FIFO.
Использование: python3 fifo_client.py <client_id> "<выражение>"
"""
import os
import sys
import atexit

REQUEST_FIFO = "/tmp/calc_request.fifo"

def main():
    if len(sys.argv) < 3:
        client_id = f"proc_{os.getpid()}"
        expr = sys.argv[1] if len(sys.argv) > 1 else "25 * 4 + (100 / 2)"
    else:
        client_id = sys.argv[1]
        expr = sys.argv[2]

    response_fifo = f"/tmp/calc_resp_{client_id}.fifo"

    def cleanup():
        if os.path.exists(response_fifo):
            try:
                os.unlink(response_fifo)
            except OSError:
                pass

    atexit.register(cleanup)
    cleanup()

    if not os.path.exists(REQUEST_FIFO):
        print(f"Ошибка: сервер не запущен (канал {REQUEST_FIFO} не найден).", file=sys.stderr)
        sys.exit(1)

    os.mkfifo(response_fifo)

    print(f"[Клиент {client_id}] Отправка запроса: '{expr}'")
    # Отправляем запрос на сервер
    with open(REQUEST_FIFO, "w", encoding="utf-8") as wf:
        wf.write(f"{client_id}:{expr}\n")

    # Читаем ответ из нашего персонального канала
    with open(response_fifo, "r", encoding="utf-8") as rf:
        response = rf.readline().strip()

    print(f"[Клиент {client_id}] Получен ответ от сервера: {response}")
    cleanup()

if __name__ == "__main__":
    main()
