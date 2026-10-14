#!/usr/bin/env python3
"""
Практическая работа № 4. Вариант B. Задание 4.
memory_sharing_demo.py: Демонстрация разделения адресного пространства:
  - Потоки выполняются в едином адресном пространстве процесса и разделяют память.
  - Процессы имеют изолированные адресные пространства (свои сегменты данных и кучи).
"""
import threading
import multiprocessing
import time

# Глобальный список для демонстрации разделения памяти
shared_list = ["ORIGINAL_0", "ORIGINAL_1", "ORIGINAL_2"]

def thread_worker():
    global shared_list
    print(f"  [Поток TID {threading.get_ident()}] Модифицирует shared_list...")
    shared_list.append("ADDED_BY_THREAD")
    shared_list[0] = "MODIFIED_BY_THREAD"

def process_worker():
    global shared_list
    print("  [Процесс] Модифицирует shared_list в своей копии адресного пространства...")
    shared_list.append("ADDED_BY_PROCESS")
    shared_list[0] = "MODIFIED_BY_PROCESS"
    print(f"  [Процесс] Внутри процесса-потомка: {shared_list}")

def main():
    global shared_list
    print("=== Демонстрация разделения памяти: Потоки vs Процессы ===\n")

    # --- 1. ТЕСТ С ПОТОКОМ ---
    print("1. Исходное состояние shared_list перед запуском потока:")
    print(f"   {shared_list}")

    t = threading.Thread(target=thread_worker)
    t.start()
    t.join()

    print("   Состояние shared_list в родителе ПОСЛЕ завершения потока:")
    print(f"   {shared_list}")
    if "ADDED_BY_THREAD" in shared_list and shared_list[0] == "MODIFIED_BY_THREAD":
        print("   [✓] ПОТОКИ РАЗДЕЛЯЮТ ПАМЯТЬ: изменения, внесенные потоком, напрямую видны в родителе!\n")
    else:
        print("   [X] Ошибка теста потоков.\n")

    # Сброс списка к исходному
    shared_list = ["ORIGINAL_0", "ORIGINAL_1", "ORIGINAL_2"]

    # --- 2. ТЕСТ С ПРОЦЕССОМ ---
    print("2. Исходное состояние shared_list перед запуском процесса:")
    print(f"   {shared_list}")

    p = multiprocessing.Process(target=process_worker)
    p.start()
    p.join()

    print("   Состояние shared_list в родителе ПОСЛЕ завершения процесса:")
    print(f"   {shared_list}")
    if shared_list == ["ORIGINAL_0", "ORIGINAL_1", "ORIGINAL_2"]:
        print("   [✓] ПРОЦЕССЫ ИЗОЛИРОВАНЫ: изменения в памяти потомка НЕ повлияли на память родителя!")
        print("   --> Для передачи данных между процессами необходимы специальные средства IPC (Shared Memory, Pipes, Queues).\n")
    else:
        print("   [X] Ошибка теста процессов.\n")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
