#!/usr/bin/env python3
"""
Практическая работа № 7. Вариант B. Задание 2.
uds_server.py: Сервер на Unix-доменных сокетах (socket.AF_UNIX).
Обрабатывает запросы нескольких одновременных клиентов конкурентно:
по отдельному дочернему процессу (через fork) на каждого клиента.
"""
import os
import sys
import socket
import signal
import atexit
import ast

SOCKET_PATH = "/tmp/calc_uds.sock"

def safe_eval(expr_str: str) -> str:
    """Безопасный калькулятор арифметических выражений."""
    allowed_operators = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.Pow: lambda a, b: a ** b,
        ast.Mod: lambda a, b: a % b,
        ast.USub: lambda a: -a,
        ast.UAdd: lambda a: +a,
    }

    def eval_node(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return allowed_operators[type(node.op)](eval_node(node.left), eval_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            return allowed_operators[type(node.op)](eval_node(node.operand))
        raise ValueError("Неподдерживаемая операция")

    try:
        tree = ast.parse(expr_str.strip(), mode="eval")
        return str(eval_node(tree.body))
    except Exception as e:
        return f"Ошибка: {e}"

def cleanup():
    if os.path.exists(SOCKET_PATH):
        try:
            os.unlink(SOCKET_PATH)
        except OSError:
            pass

atexit.register(cleanup)

def handle_client(conn: socket.socket):
    try:
        data = conn.recv(1024).decode("utf-8").strip()
        if data:
            print(f"  [Воркер PID {os.getpid()}] Запрос: '{data}'")
            res = safe_eval(data)
            conn.sendall(f"{res}\n".encode("utf-8"))
            print(f"  [Воркер PID {os.getpid()}] Ответ: '{res}'")
    except Exception as e:
        print(f"  [Воркер PID {os.getpid()}] Ошибка: {e}")
    finally:
        conn.close()

def main():
    cleanup()
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(10)
    print(f"[UDS Сервер] Прослушивание Unix-сокета: {SOCKET_PATH}")
    print("[UDS Сервер] Режим: отдельный дочерний процесс (fork) на каждого клиента.")

    # Автоматическая уборка зомби-потомков
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    def handle_signal(sig, frame):
        print("\n[UDS Сервер] Остановка сервера...")
        server.close()
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        while True:
            conn, _ = server.accept()
            pid = os.fork()
            if pid == 0:
                # Дочерний процесс-воркер для обслуживания клиента
                server.close()
                handle_client(conn)
                os._exit(0)
            else:
                # Родительский процесс закрывает свою копию дескриптора сокета клиента
                conn.close()
    except Exception:
        pass
    finally:
        server.close()
        cleanup()

if __name__ == "__main__":
    main()
