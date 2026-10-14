#!/usr/bin/env python3
"""
Практическая работа № 3. Вариант B. Задание 3 (а).
zombie.py: Демонстрация процесса-зомби (состояние Z / defunct).
Потомок завершается немедленно, а родитель не вызывает wait(), оставляя запись в PCB/таблице процессов.
"""
import os
import sys
import time
import subprocess

def main():
    print("=== Демонстрация создания процесса-зомби ===")
    parent_pid = os.getpid()
    print(f"[Родитель] PID: {parent_pid}")

    child_pid = os.fork()

    if child_pid == 0:
        # Ветка потомка
        my_pid = os.getpid()
        print(f"  [Потомок] PID: {my_pid}, PPID: {os.getppid()} - немедленно завершаю работу.")
        os._exit(0)
    else:
        # Ветка родителя: НЕ вызываем wait() сразу, даем потомку завершиться
        print(f"[Родитель] Потомок PID={child_pid} запущен. Ждем 1 секунду...")
        time.sleep(1)

        print("\n[Родитель] Проверяем статус потомка через ps:")
        try:
            ps_out = subprocess.check_output(["ps", "-o", "pid,ppid,stat,command", "-p", str(child_pid)]).decode()
            print(ps_out)
            if "Z" in ps_out or "defunct" in ps_out:
                print(f"[✓] Процесс {child_pid} находится в состоянии ЗОМБИ (STAT содержит Z / defunct)!")
        except Exception as e:
            print(f"Ошибка проверки ps: {e}")

        print("\n[Родитель] Теперь вызываем os.wait(), освобождая запись в таблице процессов...")
        reaped_pid, status = os.wait()
        print(f"[Родитель] Потомок {reaped_pid} убран из таблицы процессов (exit status: {status}).")

        print("[Родитель] Повторная проверка ps (зомби должен исчезнуть):")
        try:
            res = subprocess.run(["ps", "-p", str(child_pid)], capture_output=True, text=True)
            if str(child_pid) not in res.stdout:
                print(f"[✓] Запись процесса {child_pid} полностью удалена из ОС.")
            else:
                print(res.stdout)
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
