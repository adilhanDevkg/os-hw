#!/usr/bin/env python3
"""
Практическая работа № 4. Вариант B. Задание 2.
io_benchmark.py: Бенчмарк сетевой задачи (загрузка 20 URL) тремя способами:
  1) Последовательно
  2) ThreadPoolExecutor (4 потока)
  3) ProcessPoolExecutor (4 процесса)
Использует многопоточный локальный HTTP-сервер с фиксированной задержкой 50 мс на запрос.
"""
import time
import socket
import statistics
import urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

class LatencyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Имитация задержки сети и удаленного сервера (50 мс)
        time.sleep(0.05)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK response")

    def log_message(self, format, *args):
        # Отключаем вывод в консоль для каждого запроса
        pass

def fetch_url(url: str) -> int:
    with urllib.request.urlopen(url, timeout=5) as resp:
        return len(resp.read())

def run_sequential(urls):
    return [fetch_url(u) for u in urls]

def run_thread_pool(urls, workers=4):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(fetch_url, urls))

def run_process_pool(urls, workers=4):
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(fetch_url, urls))

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def main():
    port = find_free_port()
    # ThreadingHTTPServer обслуживает запросы параллельно в отдельных потоках
    server = ThreadingHTTPServer(("127.0.0.1", port), LatencyHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"Многопоточный HTTP-сервер запущен на http://127.0.0.1:{port} (задержка 50 мс на запрос)")

    num_urls = 20
    urls = [f"http://127.0.0.1:{port}/item_{i}" for i in range(num_urls)]
    print(f"Подготовлен список из {num_urls} запросов.\n")

    methods = [
        ("Последовательно (1 воркер)", lambda: run_sequential(urls)),
        ("ThreadPoolExecutor (4 потока)", lambda: run_thread_pool(urls, 4)),
        ("ProcessPoolExecutor (4 процесса)", lambda: run_process_pool(urls, 4)),
    ]

    trials = 3
    results = {}

    print(f"=== Бенчмарк сетевого ввода-вывода (по {trials} прогона на метод) ===")
    for name, fn in methods:
        times = []
        for trial in range(1, trials + 1):
            t_start = time.time()
            res = fn()
            t_elapsed = time.time() - t_start
            times.append(t_elapsed)
            assert len(res) == num_urls
            print(f"  [{name}] Прогон {trial}: {t_elapsed:.4f} сек.")

        med = statistics.median(times)
        results[name] = {"times": times, "median": med}
        print(f"  --> Медиана: {med:.4f} сек.\n")

    server.shutdown()

    baseline = results["Последовательно (1 воркер)"]["median"]

    print("=" * 80)
    print(f"{'Метод':<32} | {'Прогон 1':<9} | {'Прогон 2':<9} | {'Прогон 3':<9} | {'Медиана':<9} | {'Ускорение':<10}")
    print("-" * 80)
    for name, r in results.items():
        t1, t2, t3 = r["times"]
        med = r["median"]
        speedup = baseline / med
        print(f"{name:<32} | {t1:<9.4f} | {t2:<9.4f} | {t3:<9.4f} | {med:<9.4f} | {speedup:<10.2f}x")
    print("=" * 80)

if __name__ == "__main__":
    main()
