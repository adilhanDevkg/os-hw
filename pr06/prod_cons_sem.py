#!/usr/bin/env python3
"""
Практическая работа № 6. Вариант B. Задание 1 (а).
prod_cons_sem.py: Задача «производитель–потребитель» с кольцевым буфером на 5 элементов.
Синхронизация: два семафора (empty, full) и мьютекс (mutex).
Параметры: 3 производителя, 2 потребителя, 1000 элементов.
"""
import threading
import time
from typing import List, Optional

BUFFER_CAPACITY = 5
TOTAL_ITEMS = 1000
NUM_PRODUCERS = 3
NUM_CONSUMERS = 2

class CircularBufferSem:
    def __init__(self, capacity: int = BUFFER_CAPACITY):
        self.capacity = capacity
        self.buffer: List[Optional[int]] = [None] * capacity
        self.head = 0  # Индекс для извлечения (потребитель)
        self.tail = 0  # Индекс для вставки (производитель)
        self.count = 0

        # Семафоры
        self.empty = threading.Semaphore(capacity)  # Свободные слоты
        self.full = threading.Semaphore(0)          # Заполненные слоты
        self.mutex = threading.Lock()               # Защита критической секции

        # Статистика и проверка инвариантов
        self.max_observed_fill = 0
        self.violations = 0

    def put(self, item: Optional[int]):
        self.empty.acquire()
        with self.mutex:
            if self.count >= self.capacity:
                self.violations += 1
                raise RuntimeError(f"Инвариант нарушен: переполнение буфера! ({self.count} >= {self.capacity})")
            
            self.buffer[self.tail] = item
            self.tail = (self.tail + 1) % self.capacity
            self.count += 1
            if self.count > self.max_observed_fill:
                self.max_observed_fill = self.count
        self.full.release()

    def get(self) -> Optional[int]:
        self.full.acquire()
        with self.mutex:
            if self.count <= 0:
                self.violations += 1
                raise RuntimeError(f"Инвариант нарушен: чтение из пустого буфера! ({self.count})")
            
            item = self.buffer[self.head]
            self.buffer[self.head] = None
            self.head = (self.head + 1) % self.capacity
            self.count -= 1
        self.empty.release()
        return item

def producer_worker(prod_id: int, items_to_produce: List[int], buffer: CircularBufferSem):
    for item in items_to_produce:
        buffer.put(item)

def consumer_worker(cons_id: int, buffer: CircularBufferSem, consumed_list: List[int], lock: threading.Lock):
    while True:
        item = buffer.get()
        if item is None:  # Sentinel сигнал завершения
            break
        with lock:
            consumed_list.append(item)

def main():
    print(f"=== Производитель-Потребитель на СЕМАФОРАХ ===")
    print(f"Буфер: {BUFFER_CAPACITY} элементов | Элементов: {TOTAL_ITEMS} | Производителей: {NUM_PRODUCERS} | Потребителей: {NUM_CONSUMERS}")

    buf = CircularBufferSem(BUFFER_CAPACITY)
    all_items = list(range(TOTAL_ITEMS))
    
    # Распределяем элементы между производителями
    prod_chunks = [[] for _ in range(NUM_PRODUCERS)]
    for i, item in enumerate(all_items):
        prod_chunks[i % NUM_PRODUCERS].append(item)

    consumed = []
    consumed_lock = threading.Lock()

    producers = []
    consumers = []

    t0 = time.time()

    # Запуск потребителей
    for c_id in range(NUM_CONSUMERS):
        t = threading.Thread(target=consumer_worker, args=(c_id, buf, consumed, consumed_lock))
        consumers.append(t)
        t.start()

    # Запуск производителей
    for p_id in range(NUM_PRODUCERS):
        t = threading.Thread(target=producer_worker, args=(p_id, prod_chunks[p_id], buf))
        producers.append(t)
        t.start()

    # Ждем завершения производителей
    for t in producers:
        t.join()

    # Посылаем sentinel (None) каждому потребителю для завершения
    for _ in range(NUM_CONSUMERS):
        buf.put(None)

    # Ждем завершения потребителей
    for t in consumers:
        t.join()

    elapsed = time.time() - t0

    print(f"\nВремя обработки: {elapsed:.4f} сек.")
    print(f"Максимальное зафиксированное заполнение буфера: {buf.max_observed_fill}/{BUFFER_CAPACITY}")
    print(f"Нарушений инвариантов: {buf.violations}")

    # Проверка корректности (утверждения)
    assert buf.violations == 0, f"Были зафиксированы нарушения инвариантов: {buf.violations}"
    assert len(consumed) == TOTAL_ITEMS, f"Число потребленных элементов ({len(consumed)}) != {TOTAL_ITEMS}"
    assert set(consumed) == set(range(TOTAL_ITEMS)), "Нарушена уникальность или потеряны элементы!"

    print("[✓] Проверка успешна: каждый из 1000 элементов потреблен ровно один раз, переполнения не было!")

if __name__ == "__main__":
    main()
