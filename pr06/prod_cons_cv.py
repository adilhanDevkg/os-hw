#!/usr/bin/env python3
"""
Практическая работа № 6. Вариант B. Задание 1 (б).
prod_cons_cv.py: Задача «производитель–потребитель» с кольцевым буфером на 5 элементов.
Синхронизация: мьютекс и условная переменная (threading.Condition).
Параметры: 3 производителя, 2 потребителя, 1000 элементов.
"""
import threading
import time
from typing import List, Optional

BUFFER_CAPACITY = 5
TOTAL_ITEMS = 1000
NUM_PRODUCERS = 3
NUM_CONSUMERS = 2

class CircularBufferCV:
    def __init__(self, capacity: int = BUFFER_CAPACITY):
        self.capacity = capacity
        self.buffer: List[Optional[int]] = [None] * capacity
        self.head = 0
        self.tail = 0
        self.count = 0

        # Условная переменная на базе мьютекса
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)

        self.max_observed_fill = 0
        self.violations = 0

    def put(self, item: Optional[int]):
        with self.cv:
            # Важно: цикл while для защиты от ложных/перехваченных пробуждений
            while self.count >= self.capacity:
                self.cv.wait()

            if self.count >= self.capacity:
                self.violations += 1
                raise RuntimeError(f"Инвариант нарушен: переполнение буфера! ({self.count} >= {self.capacity})")

            self.buffer[self.tail] = item
            self.tail = (self.tail + 1) % self.capacity
            self.count += 1
            if self.count > self.max_observed_fill:
                self.max_observed_fill = self.count

            # Оповещаем ждущих потребителей
            self.cv.notify_all()

    def get(self) -> Optional[int]:
        with self.cv:
            # Ожидание появления хотя бы одного элемента в буфере
            while self.count == 0:
                self.cv.wait()

            if self.count <= 0:
                self.violations += 1
                raise RuntimeError(f"Инвариант нарушен: чтение из пустого буфера! ({self.count})")

            item = self.buffer[self.head]
            self.buffer[self.head] = None
            self.head = (self.head + 1) % self.capacity
            self.count -= 1

            # Оповещаем ждущих производителей о появившемся месте
            self.cv.notify_all()
            return item

def producer_worker(prod_id: int, items_to_produce: List[int], buffer: CircularBufferCV):
    for item in items_to_produce:
        buffer.put(item)

def consumer_worker(cons_id: int, buffer: CircularBufferCV, consumed_list: List[int], lock: threading.Lock):
    while True:
        item = buffer.get()
        if item is None:  # Сигнал окончания
            break
        with lock:
            consumed_list.append(item)

def main():
    print(f"=== Производитель-Потребитель на УСЛОВНОЙ ПЕРЕМЕННОЙ (Condition Variable) ===")
    print(f"Буфер: {BUFFER_CAPACITY} элементов | Элементов: {TOTAL_ITEMS} | Производителей: {NUM_PRODUCERS} | Потребителей: {NUM_CONSUMERS}")

    buf = CircularBufferCV(BUFFER_CAPACITY)
    all_items = list(range(TOTAL_ITEMS))
    
    prod_chunks = [[] for _ in range(NUM_PRODUCERS)]
    for i, item in enumerate(all_items):
        prod_chunks[i % NUM_PRODUCERS].append(item)

    consumed = []
    consumed_lock = threading.Lock()

    producers = []
    consumers = []

    t0 = time.time()

    for c_id in range(NUM_CONSUMERS):
        t = threading.Thread(target=consumer_worker, args=(c_id, buf, consumed, consumed_lock))
        consumers.append(t)
        t.start()

    for p_id in range(NUM_PRODUCERS):
        t = threading.Thread(target=producer_worker, args=(p_id, prod_chunks[p_id], buf))
        producers.append(t)
        t.start()

    for t in producers:
        t.join()

    # Отправляем сигналы завершения потребителям
    for _ in range(NUM_CONSUMERS):
        buf.put(None)

    for t in consumers:
        t.join()

    elapsed = time.time() - t0

    print(f"\nВремя обработки: {elapsed:.4f} сек.")
    print(f"Максимальное зафиксированное заполнение буфера: {buf.max_observed_fill}/{BUFFER_CAPACITY}")
    print(f"Нарушений инвариантов: {buf.violations}")

    assert buf.violations == 0, f"Нарушения инвариантов: {buf.violations}"
    assert len(consumed) == TOTAL_ITEMS, f"Потреблено {len(consumed)} вместо {TOTAL_ITEMS}"
    assert set(consumed) == set(range(TOTAL_ITEMS)), "Нарушена корректность данных!"

    print("[✓] Проверка успешна: все 1000 элементов обработаны строго по одному разу без переполнений!")

if __name__ == "__main__":
    main()
