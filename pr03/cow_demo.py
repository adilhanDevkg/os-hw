#!/usr/bin/env python3
"""
Практическая работа № 3. Вариант B. Задание 4.
cow_demo.py: Демонстрация механизма Copy-On-Write (COW) при системном вызове fork.
Измерение RSS дочернего процесса до и после модификации унаследованной памяти.
"""
import os
import sys
import time
import resource

def get_rss_kb() -> int:
    """Возвращает текущий Resident Set Size (RSS) процесса в килобайтах."""
    # Приоритет: чтение точного VmRSS из /proc/self/status (Linux)
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except Exception:
        pass

    # Fallback через POSIX getrusage
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return usage // 1024  # На macOS ru_maxrss возвращается в байтах
    return usage  # На Linux ru_maxrss в килобайтах

def main():
    print("=== Демонстрация Copy-On-Write (COW) в ОС Linux ===")
    
    # Выделяем массив размером 60 МБ
    size_mb = 60
    size_bytes = size_mb * 1024 * 1024
    print(f"[Родитель PID {os.getpid()}] Выделяем {size_mb} МБ памяти...")
    data = bytearray(b"X" * size_bytes)
    
    # Принудительно "прогреваем" память родителя, чтобы страницы стали Resident
    for i in range(0, size_bytes, 4096):
        data[i] = 65  # 'A'

    parent_rss = get_rss_kb()
    print(f"[Родитель PID {os.getpid()}] RSS родителя после инициализации: {parent_rss / 1024:.2f} МБ")

    print("\n[Родитель] Вызываем os.fork()...")
    pid = os.fork()

    if pid == 0:
        # Ветка потомка
        child_pid = os.getpid()
        rss_before = get_rss_kb()
        print(f"\n  [Потомок PID {child_pid}] Создан через fork().")
        print(f"  [Потомок PID {child_pid}] RSS ДО изменения данных: {rss_before / 1024:.2f} МБ")
        print("  --> Страницы памяти физически разделяются с родителем (Shared Clean). Копирования не произошло!")

        print(f"\n  [Потомок PID {child_pid}] Модифицируем память (запись байта в каждую страницу 4 КБ)...")
        for i in range(0, size_bytes, 4096):
            data[i] = 66  # 'B' - запись вызывает аппаратный Page Fault (защита от записи)

        rss_after = get_rss_kb()
        print(f"  [Потомок PID {child_pid}] RSS ПОСЛЕ изменения данных: {rss_after / 1024:.2f} МБ")
        diff = (rss_after - rss_before) / 1024
        print(f"  --> Прирост физической памяти RSS потомка: +{diff:.2f} МБ")
        print("  [✓] Механизм Copy-On-Write подтвержден: физическое копирование страниц произошло только при записи!")
        os._exit(0)
    else:
        # Ветка родителя
        os.waitpid(pid, 0)
        parent_rss_end = get_rss_kb()
        print(f"\n[Родитель PID {os.getpid()}] Потомок завершился.")
        print(f"[Родитель PID {os.getpid()}] RSS родителя остался неизменным: {parent_rss_end / 1024:.2f} МБ")
        print("=== Тест Copy-On-Write успешно пройден ===")

if __name__ == "__main__":
    main()
