#!/usr/bin/env python3
"""
Практическая работа № 6. Вариант B. Задание 4.
spurious_wakeup_demo.py: Демонстрация проблемы «потерянного пробуждения» (lost / spurious wakeup)
и почему условную переменную ОБЯЗАТЕЛЬНО нужно проверять в цикле `while`, а не через `if`.
"""
import threading
import time

class BrokenQueueWithIf:
    """Ошибочная реализация: проверка условия через 'if' вместо 'while'."""
    def __init__(self):
        self.items = []
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)
        self.errors = 0

    def put(self, item):
        with self.cv:
            self.items.append(item)
            # notify_all будит всех ожидающих потребителей
            self.cv.notify_all()

    def get_broken(self, consumer_id: int):
        with self.cv:
            # ОШИБКА: используется if вместо while!
            if len(self.items) == 0:
                self.cv.wait()

            # Если проснулись два потока, первый заберет единственный элемент,
            # а второй придет сюда с пустым self.items!
            if len(self.items) == 0:
                self.errors += 1
                raise IndexError(f"[CRASH в Потребителе {consumer_id}] Попытка извлечения из пустого списка! Сработало пробуждение по if!")
            return self.items.pop(0)

class SafeQueueWithWhile:
    """Корректная реализация: проверка условия в цикле 'while'."""
    def __init__(self):
        self.items = []
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)
        self.errors = 0

    def put(self, item):
        with self.cv:
            self.items.append(item)
            self.cv.notify_all()

    def get_safe(self, consumer_id: int):
        with self.cv:
            # КОРРЕКТНО: цикл while гарантирует повторную проверку после захвата мьютекса
            while len(self.items) == 0:
                self.cv.wait()
            return self.items.pop(0)

def main():
    print("=== [1] Тест ОШИБОЧНОЙ очереди (проверка через IF) ===")
    broken_q = BrokenQueueWithIf()

    def bad_consumer(cid):
        try:
            val = broken_q.get_broken(cid)
            print(f"  Потребитель {cid} успешно получил: {val}")
        except IndexError as e:
            print(f"  [!] {e}")

    # Запускаем двух потребителей, когда очередь пуста
    t1 = threading.Thread(target=bad_consumer, args=(1,))
    t2 = threading.Thread(target=bad_consumer, args=(2,))
    t1.start()
    t2.start()

    time.sleep(0.05)
    print("Производитель кладет ОДИН элемент и вызывает notify_all()...")
    broken_q.put("ЭЛЕМЕНТ_1")

    t1.join()
    t2.join()

    print(f"Итог теста с IF: зафиксировано ошибок = {broken_q.errors}\n")

    print("=== [2] Тест КОРРЕКТНОЙ очереди (проверка через WHILE) ===")
    safe_q = SafeQueueWithWhile()
    results = []

    def good_consumer(cid):
        val = safe_q.get_safe(cid)
        results.append((cid, val))
        print(f"  Потребитель {cid} успешно получил: {val}")

    t1 = threading.Thread(target=good_consumer, args=(1,))
    t2 = threading.Thread(target=good_consumer, args=(2,))
    t1.start()
    t2.start()

    time.sleep(0.05)
    print("Производитель кладет первый элемент...")
    safe_q.put("ДАННЫЕ_A")
    time.sleep(0.05)
    print("Производитель кладет второй элемент...")
    safe_q.put("ДАННЫЕ_B")

    t1.join()
    t2.join()

    assert len(results) == 2
    print(f"Итог теста с WHILE: оба потребителя корректно и безопасно получили данные: {results}")

if __name__ == "__main__":
    main()
