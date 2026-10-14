#!/usr/bin/env python3
"""
Практическая работа № 3. Вариант B. Задание 2.
runner.py: Создание N дочерних процессов через fork, каждый через exec запускает переданную команду.
Родитель ждет всех процессов и выводит коды возврата и время работы каждого.
"""
import os
import sys
import time
import argparse

def main():
    parser = argparse.ArgumentParser(description="Параллельный запуск N копий команды через fork + exec")
    parser.add_argument("-n", "--count", type=int, default=4, help="Количество дочерних процессов (по умолчанию: 4)")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Команда и аргументы для запуска (например: sleep 1)")

    args = parser.parse_args()

    if not args.command:
        # Если аргументов нет, по умолчанию запускаем команду echo/sleep
        args.command = ["python3", "-c", "import time, os; print(f'Worker PID {os.getpid()} working...'); time.sleep(0.5)"]

    print(f"=== Запуск {args.count} процессов команды: {' '.join(args.command)} ===")
    
    children = {}

    overall_start = time.time()
    for i in range(1, args.count + 1):
        t_start = time.time()
        pid = os.fork()
        if pid == 0:
            # Ветка дочернего процесса: замещаем образ процесса через execvp
            try:
                os.execvp(args.command[0], args.command)
            except Exception as e:
                print(f"[Child PID {os.getpid()}] Ошибка execvp: {e}", file=sys.stderr)
                os._exit(127)
        else:
            # Ветка родителя: сохраняем PID и время старта
            children[pid] = {
                "index": i,
                "start": t_start,
                "end": None,
                "status": None,
                "duration": None
            }

    # Родитель ждет завершения всех дочерних процессов
    results = []
    while children:
        pid, status = os.waitpid(-1, 0)
        t_end = time.time()
        if pid in children:
            info = children.pop(pid)
            info["end"] = t_end
            info["duration"] = t_end - info["start"]

            if os.WIFEXITED(status):
                info["exit_code"] = os.WEXITSTATUS(status)
                info["reason"] = "OK"
            elif os.WIFSIGNALED(status):
                info["exit_code"] = -os.WTERMSIG(status)
                info["reason"] = f"Signal {os.WTERMSIG(status)}"
            else:
                info["exit_code"] = status
                info["reason"] = "Unknown"
            
            results.append((pid, info))

    total_time = time.time() - overall_start

    # Сортируем результаты по индексу запуска
    results.sort(key=lambda x: x[1]["index"])

    print("\n" + "=" * 65)
    print(" Результаты выполнения дочерних процессов")
    print("=" * 65)
    print(f"{'№':<3} | {'PID':<8} | {'Код возврата':<13} | {'Время (сек)':<12} | {'Статус':<15}")
    print("-" * 65)
    for _, (pid, info) in enumerate(results):
        print(f"{info['index']:<3} | {pid:<8} | {info['exit_code']:<13} | {info['duration']:<12.4f} | {info['reason']:<15}")
    print("=" * 65)
    print(f"Все процессы завершены. Общее астрономическое время: {total_time:.4f} сек.")

if __name__ == "__main__":
    main()
