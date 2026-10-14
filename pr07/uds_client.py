#!/usr/bin/env python3
"""
Практическая работа № 7. Вариант B. Задание 2.
uds_client.py: Клиент Unix-доменных сокетов (AF_UNIX).
Отправляет выражение на UDS-сервер и получает ответ.
Использование: python3 uds_client.py "<выражение>"
"""
import os
import sys
import socket

SOCKET_PATH = "/tmp/calc_uds.sock"

def main():
    expr = sys.argv[1] if len(sys.argv) > 1 else "12 * 12 + 36"
    client_pid = os.getpid()

    if not os.path.exists(SOCKET_PATH):
        print(f"Ошибка: сервер не запущен (сокет {SOCKET_PATH} не найден).", file=sys.stderr)
        sys.exit(1)

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.connect(SOCKET_PATH)
        print(f"[UDS Клиент PID {client_pid}] Отправка выражения: '{expr}'")
        s.sendall(f"{expr}\n".encode("utf-8"))
        resp = s.recv(1024).decode("utf-8").strip()
        print(f"[UDS Клиент PID {client_pid}] Результат вычисления: {resp}")
    finally:
        s.close()

if __name__ == "__main__":
    main()
