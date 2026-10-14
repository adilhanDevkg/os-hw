#!/usr/bin/env python3
"""
race_condition_demo.py: Демонстрация состояния гонки (Race Condition).
4 потока инкрементируют счетчик по 100 000 раз без блокировок.
"""
import threading
import sys

counter = 0

def worker():
    global counter
    for _ in range(100_000):
        # Чтение, инкремент, запись (гонка при переключении потоков)
        val = counter
        val += 1
        counter = val

def main():
    global counter
    counter = 0
    sys.setswitchinterval(0.0001)  # Частые переключения для надежного воспроизведения гонки

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected = 400_000
    print(f"Итог БЕЗ блокировки: {counter} (Ожидалось: {expected})")
    if counter != expected:
        print(f"[!] Состояние гонки зафиксировано: потеряно {expected - counter} операций!")
    else:
        print("[!] Не удалось поймать гонку в текущем прогоне.")

if __name__ == "__main__":
    main()
