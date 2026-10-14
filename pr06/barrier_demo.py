#!/usr/bin/env python3
"""
Практическая работа № 6. Вариант B. Задание 3.
barrier_demo.py: Реализация переиспользуемого барьера на условной переменной
для синхронизации 4 потоков, выполняющих вычисления в три фазы.
"""
import threading
import time
import random

class ReusableBarrier:
    def __init__(self, parties: int):
        self.parties = parties
        self.count = parties
        self.generation = 0
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)

    def wait(self):
        with self.cv:
            my_generation = self.generation
            self.count -= 1
            if self.count == 0:
                # Все потоки достигли барьера: переходим к следующему поколению
                self.generation += 1
                self.count = self.parties
                self.cv.notify_all()
            else:
                # Ждем, пока текущее поколение барьера не сменится
                while my_generation == self.generation:
                    self.cv.wait()

def worker(worker_id: int, barrier: ReusableBarrier, phase_log: list, lock: threading.Lock):
    phases = [
        "Фаза 1: Сбор и валидация данных",
        "Фаза 2: Параллельные матричные вычисления",
        "Фаза 3: Агрегация результатов и фиксация"
    ]

    for p_idx, phase_name in enumerate(phases, start=1):
        # Имитация неравномерной работы потоков
        work_time = random.uniform(0.05, 0.15)
        time.sleep(work_time)

        with lock:
            msg = f"[Поток {worker_id}] ЗАВЕРШИЛ {phase_name} (за {work_time:.3f} с)"
            print(msg)
            phase_log.append((p_idx, worker_id, "done"))

        # Точка синхронизации: ни один поток не перейдет к фазе p_idx+1, пока все не завершат p_idx
        barrier.wait()

        with lock:
            print(f"  --> [Поток {worker_id}] ПРОШЕЛ барьер {p_idx}")

def main():
    print("=== Демонстрация барьера на условной переменной (4 потока, 3 фазы) ===")
    num_threads = 4
    barrier = ReusableBarrier(num_threads)
    phase_log = []
    print_lock = threading.Lock()

    threads = []
    for i in range(1, num_threads + 1):
        t = threading.Thread(target=worker, args=(i, barrier, phase_log, print_lock))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n=== Проверка корректности барьера ===")
    # Проверяем, что в логе завершения событий строго сгруппированы по фазам:
    # 4 события фазы 1, затем 4 события фазы 2, затем 4 события фазы 3
    phases_sequence = [entry[0] for entry in phase_log]
    print(f"Последовательность фаз завершения в логе:\n{phases_sequence}")

    for phase in (1, 2, 3):
        chunk = phases_sequence[(phase - 1) * 4 : phase * 4]
        assert chunk == [phase] * 4, f"Ошибка: барьер нарушен в фазе {phase}! chunk={chunk}"

    print("[✓] Барьер отработал идеально: ни один поток не начал следующую фазу раньше времени!")

if __name__ == "__main__":
    main()
