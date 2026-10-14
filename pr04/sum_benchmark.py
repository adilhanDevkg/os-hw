#!/usr/bin/env python3
"""
Практическая работа № 4. Вариант B. Задание 1.
sum_benchmark.py: Подсчет суммы чисел из numbers.txt тремя способами:
  1) Один поток
  2) 4 потока (threading)
  3) 4 процесса (multiprocessing)
Измерение времени каждого метода, 3 повтора, расчет медианы и ускорения.
"""
import os
import sys
import time
import statistics
import threading
import multiprocessing

def chunk_worker_thread(sublist, results, index):
    results[index] = sum(sublist)

def sum_threads(data, num_threads=4):
    n = len(data)
    step = (n + num_threads - 1) // num_threads
    threads = []
    results = [0] * num_threads

    for i in range(num_threads):
        chunk = data[i * step : (i + 1) * step]
        t = threading.Thread(target=chunk_worker_thread, args=(chunk, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return sum(results)

def chunk_worker_proc(sublist):
    return sum(sublist)

def sum_processes(data, num_procs=4):
    n = len(data)
    step = (n + num_procs - 1) // num_procs
    chunks = [data[i * step : (i + 1) * step] for i in range(num_procs)]
    
    with multiprocessing.Pool(processes=num_procs) as pool:
        results = pool.map(chunk_worker_proc, chunks)
    return sum(results)

def main():
    target = os.path.join(os.path.dirname(__file__), "numbers.txt")
    if not os.path.exists(target):
        print(f"Файл {target} не найден. Запуск генерации...")
        from generate_numbers import generate
        generate(target, 5_000_000)

    print(f"Загрузка чисел из {target} в память...")
    t0 = time.time()
    with open(target, "r", encoding="utf-8") as f:
        data = [int(line.strip()) for line in f if line.strip()]
    print(f"Загружено {len(data):,} чисел за {time.time() - t0:.2f} сек.\n")

    methods = [
        ("1 поток (последовательно)", lambda: sum(data)),
        ("4 потока (threading)", lambda: sum_threads(data, 4)),
        ("4 процесса (multiprocessing)", lambda: sum_processes(data, 4)),
    ]

    trials = 3
    results = {}

    print(f"=== Бенчмарк подсчета суммы (по {trials} прогона на метод) ===")
    for name, fn in methods:
        times = []
        sums = []
        for trial in range(1, trials + 1):
            t_start = time.time()
            total = fn()
            t_elapsed = time.time() - t_start
            times.append(t_elapsed)
            sums.append(total)
            print(f"  [{name}] Прогон {trial}: {t_elapsed:.4f} сек. (Сумма: {total})")

        # Проверка корректности (суммы должны совпадать)
        assert len(set(sums)) == 1, f"Ошибка: суммы не совпадают: {sums}"

        med = statistics.median(times)
        results[name] = {"times": times, "median": med, "sum": sums[0]}
        print(f"  --> Медиана: {med:.4f} сек.\n")

    baseline = results["1 поток (последовательно)"]["median"]

    print("=" * 80)
    print(f"{'Метод':<30} | {'Прогон 1':<9} | {'Прогон 2':<9} | {'Прогон 3':<9} | {'Медиана':<9} | {'Ускорение':<10}")
    print("-" * 80)
    for name, r in results.items():
        t1, t2, t3 = r["times"]
        med = r["median"]
        speedup = baseline / med
        print(f"{name:<30} | {t1:<9.4f} | {t2:<9.4f} | {t3:<9.4f} | {med:<9.4f} | {speedup:<10.2f}x")
    print("=" * 80)

if __name__ == "__main__":
    # Для корректного старта multiprocessing на macOS/Linux
    multiprocessing.freeze_support()
    main()
