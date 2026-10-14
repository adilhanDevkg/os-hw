#!/usr/bin/env python3
"""
race_condition_fixed.py: Устранение состояния гонки с помощью мьютекса (threading.Lock).
Счетчик защищен критической секцией `with lock:`.
"""
import threading
import sys

counter = 0
lock = threading.Lock()

def worker():
    global counter
    for _ in range(100_000):
        with lock:
            val = counter
            val += 1
            counter = val

def main():
    global counter
    counter = 0
    sys.setswitchinterval(0.0001)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected = 400_000
    print(f"Итог С БЛОКИРОВКОЙ (threading.Lock): {counter} (Ожидалось: {expected})")
    assert counter == expected, f"Ошибка: счетчик не равен {expected}!"
    print("[✓] Состояние гонки полностью устранено: результат стабильно 400 000!")

if __name__ == "__main__":
    main()
