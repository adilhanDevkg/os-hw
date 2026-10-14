#!/usr/bin/env python3
"""
Практическая работа № 3. Вариант B. Задание 3 (б).
orphan.py: Демонстрация процесса-сироты (orphan).
Родитель завершается раньше потомка, потомок усыновляется init (PID 1) или systemd --user / subreaper.
"""
import os
import sys
import time
import subprocess

def get_process_name(pid: int) -> str:
    """Возвращает имя процесса по PID."""
    try:
        out = subprocess.check_output(["ps", "-p", str(pid), "-o", "comm="]).decode().strip()
        return out
    except Exception:
        return "unknown"

def main():
    print("=== Демонстрация создания процесса-сироты (Orphan) ===")
    parent_pid = os.getpid()
    print(f"[Родитель] Мой PID: {parent_pid}")

    pid = os.fork()

    if pid == 0:
        # Ветка потомка
        my_pid = os.getpid()
        orig_ppid = os.getppid()
        print(f"  [Потомок PID {my_pid}] Запущен. Исходный родитель PPID: {orig_ppid} ({get_process_name(orig_ppid)})")
        
        # Ждем, пока родитель завершится
        print(f"  [Потомок PID {my_pid}] Ожидание завершения родителя...")
        for _ in range(20):
            curr_ppid = os.getppid()
            if curr_ppid != orig_ppid:
                break
            time.sleep(0.1)

        new_ppid = os.getppid()
        adopter_name = get_process_name(new_ppid)
        print(f"\n  [Потомок PID {my_pid}] Родитель завершился!")
        print(f"  [Потомок PID {my_pid}] Текущий PPID: {new_ppid} [Усыновитель: '{adopter_name}']")

        if new_ppid == 1:
            print("  [✓] Потомок был усыновлен корневым процессом init (PID 1).")
        else:
            print(f"  [✓] Потомок усыновлен subreaper-процессом (systemd --user / менеджер сессии PID {new_ppid}).")
        
        print(f"  [Потомок PID {my_pid}] Завершение работы потомка.")
        os._exit(0)
    else:
        # Ветка родителя: быстро завершаемся
        time.sleep(0.1)
        print(f"[Родитель PID {parent_pid}] Завершаю свою работу, оставляя потомка {pid} сиротой.")
        os._exit(0)

if __name__ == "__main__":
    main()
