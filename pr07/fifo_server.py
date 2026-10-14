#!/usr/bin/env python3
"""
Практическая работа № 7. Вариант B. Задание 1.
fifo_server.py: Сервер на именованных каналах (FIFO).
Принимает запросы вида "<client_id>:<выражение>" из /tmp/calc_request.fifo,
вычисляет математическое выражение и отправляет ответ в персональный FIFO клиента /tmp/calc_resp_<client_id>.fifo.
"""
import os
import sys
import ast
import signal
import atexit

REQUEST_FIFO = "/tmp/calc_request.fifo"

def safe_eval(expr_str: str) -> str:
    """Безопасное вычисление базовых арифметических выражений через AST."""
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
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Недопустимый тип константы")
        elif isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            op = type(node.op)
            if op in allowed_operators:
                return allowed_operators[op](left, right)
            raise ValueError(f"Оператор {op} не поддерживается")
        elif isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            op = type(node.op)
            if op in allowed_operators:
                return allowed_operators[op](operand)
            raise ValueError("Недопустимый унарный оператор")
        raise ValueError(f"Недопустимое выражение: {type(node)}")

    try:
        tree = ast.parse(expr_str.strip(), mode="eval")
        res = eval_node(tree.body)
        return str(res)
    except ZeroDivisionError:
        return "Ошибка: Деление на ноль"
    except Exception as e:
        return f"Ошибка: {e}"

def cleanup():
    if os.path.exists(REQUEST_FIFO):
        try:
            os.unlink(REQUEST_FIFO)
        except OSError:
            pass

atexit.register(cleanup)

def main():
    cleanup()
    os.mkfifo(REQUEST_FIFO)
    print(f"[FIFO Сервер] Создан канал запросов: {REQUEST_FIFO}")
    print("[FIFO Сервер] Ожидание запросов от клиентов (Ctrl+C для выхода)...")

    def handle_signal(sig, frame):
        print("\n[FIFO Сервер] Завершение работы...")
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    while True:
        # Открытие FIFO в режиме чтение-запись предотвращает получение немедленного EOF при отключении клиента
        try:
            with open(REQUEST_FIFO, "r", encoding="utf-8") as rf:
                for line in rf:
                    line = line.strip()
                    if not line:
                        continue
                    if line == "SHUTDOWN":
                        print("[FIFO Сервер] Получен сигнал завершения SHUTDOWN.")
                        return

                    parts = line.split(":", 1)
                    if len(parts) != 2:
                        continue
                    client_id, expr = parts[0].strip(), parts[1].strip()
                    print(f"[FIFO Сервер] Запрос от клиента [{client_id}]: '{expr}'")

                    result = safe_eval(expr)
                    client_fifo = f"/tmp/calc_resp_{client_id}.fifo"

                    if os.path.exists(client_fifo):
                        try:
                            with open(client_fifo, "w", encoding="utf-8") as wf:
                                wf.write(f"{result}\n")
                            print(f"[FIFO Сервер] Ответ отправлен в {client_fifo}: {result}")
                        except Exception as e:
                            print(f"[FIFO Сервер] Ошибка отправки ответа: {e}")
        except Exception as e:
            print(f"[FIFO Сервер] Ошибка цикла: {e}")

if __name__ == "__main__":
    main()
