#!/usr/bin/env python3
"""
Практическая работа № 7. Вариант B. Задания 3 и 4.
shm_vs_pipe.py: Сравнение производительности передачи массива из 10^7 чисел (40 МБ)
между процессами двумя механизмами:
  1) Разделяемая память (multiprocessing.shared_memory)
  2) Анонимный канал (multiprocessing.Pipe)
Обеспечивает строгое освобождение ресурсов (shm.unlink).
"""
import os
import sys
import time
import array
import multiprocessing
from multiprocessing import shared_memory, Pipe, Event

NUM_ELEMENTS = 10_000_000  # 10^7 32-битных целых чисел = 40 МБ
BYTE_SIZE = NUM_ELEMENTS * 4

def worker_pipe_receiver(conn, done_evt):
    t_start = time.time()
    raw_data = bytearray(BYTE_SIZE)
    view = memoryview(raw_data)
    bytes_read = 0
    while bytes_read < BYTE_SIZE:
        chunk = conn.recv_bytes()
        n = len(chunk)
        view[bytes_read : bytes_read + n] = chunk
        bytes_read += n
    view.release()
    t_elapsed = time.time() - t_start
    conn.send(t_elapsed)

def test_pipe_transfer():
    print(f"\n--- [Тест 1] Передача через multiprocessing.Pipe ({BYTE_SIZE / (1024*1024):.1f} МБ) ---")
    parent_conn, child_conn = Pipe()
    done_evt = Event()

    arr = array.array("i", [i % 1000 for i in range(NUM_ELEMENTS)])
    raw_bytes = arr.tobytes()

    p = multiprocessing.Process(target=worker_pipe_receiver, args=(child_conn, done_evt))
    p.start()

    chunk_size = 65536
    t0 = time.time()
    for offset in range(0, BYTE_SIZE, chunk_size):
        parent_conn.send_bytes(raw_bytes[offset : offset + chunk_size])

    child_time = parent_conn.recv()
    p.join()
    parent_time = time.time() - t0

    throughput_mb = (BYTE_SIZE / (1024 * 1024)) / parent_time
    print(f"Время передачи через Pipe: {parent_time:.4f} сек. (Пропускная способность: {throughput_mb:.2f} МБ/с)")
    return parent_time

def worker_shm_receiver(shm_name, ready_evt, finish_evt, result_conn):
    ready_evt.wait()
    t_start = time.time()
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    # Используем memoryview для доступа к данным
    mv = memoryview(existing_shm.buf)
    sample = mv[0]
    
    # ВАЖНО: обязательно освобождаем memoryview до вызова close(),
    # иначе Python вызывает BufferError: cannot close exported pointers exist
    mv.release()
    del mv
    
    t_elapsed = time.time() - t_start
    existing_shm.close()
    finish_evt.set()
    result_conn.send((t_elapsed, sample))

def test_shm_transfer():
    print(f"\n--- [Тест 2] Передача через Shared Memory ({BYTE_SIZE / (1024*1024):.1f} МБ) ---")
    shm = None
    try:
        shm = shared_memory.SharedMemory(create=True, size=BYTE_SIZE)
        ready_evt = Event()
        finish_evt = Event()
        parent_conn, child_conn = Pipe()

        arr = array.array("i", [i % 1000 for i in range(NUM_ELEMENTS)])
        shm.buf[:BYTE_SIZE] = arr.tobytes()

        p = multiprocessing.Process(
            target=worker_shm_receiver,
            args=(shm.name, ready_evt, finish_evt, child_conn)
        )
        p.start()

        t0 = time.time()
        # Сигнализируем о готовности данных
        ready_evt.set()
        finish_evt.wait()
        total_time = time.time() - t0

        child_time, sample = parent_conn.recv()
        p.join()

        throughput_mb = (BYTE_SIZE / (1024 * 1024)) / total_time
        print(f"Время передачи через Shared Memory: {total_time:.6f} сек. (Пропускная способность: {throughput_mb:.2f} МБ/с)")
        return total_time
    finally:
        if shm is not None:
            shm.close()
            shm.unlink()
            print("[Shared Memory] Сегмент успешно закрыт и удален из памяти (unlink).")

def main():
    print(f"=== Сравнение механизмов IPC: Shared Memory vs Pipe ===")
    print(f"Объем данных: {NUM_ELEMENTS:,} чисел ({BYTE_SIZE / (1024*1024):.1f} МБ)")

    time_pipe = test_pipe_transfer()
    time_shm = test_shm_transfer()

    speedup = time_pipe / time_shm if time_shm > 0 else float("inf")

    print("\n" + "=" * 80)
    print(" Сводная таблица сравнения механизмов IPC")
    print("=" * 80)
    print(f"{'Механизм IPC':<22} | {'Синхронизация?':<16} | {'Объем данных':<14} | {'Время передачи':<15} | {'Ускорение':<10}")
    print("-" * 80)
    print(f"{'FIFO (Named Pipe)':<22} | {'Не требуется':<16} | {'Потоковый':<14} | {'Зависит от IO':<15} | {'-':<10}")
    print(f"{'Unix Domain Socket':<22} | {'Не требуется':<16} | {'Потоковый':<14} | {'Зависит от IO':<15} | {'-':<10}")
    print(f"{'Pipe (канал)':<22} | {'Встроена в ядро':<16} | {f'{BYTE_SIZE/(1024*1024):.1f} МБ':<14} | {f'{time_pipe:.4f} сек':<15} | {'1.0x (база)':<10}")
    print(f"{'Shared Memory (shm)':<22} | {'ОБЯЗАТЕЛЬНА':<16} | {f'{BYTE_SIZE/(1024*1024):.1f} МБ':<14} | {f'{time_shm:.6f} сек':<15} | {f'{speedup:.1f}x':<10}")
    print("=" * 80)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
