#!/usr/bin/env python3
"""
Практическая работа № 5. Вариант B.
sched.py: Симулятор алгоритмов планирования центрального процессора (CPU).
Реализованы: FCFS, SJF, SRTF, Preemptive Priority (со старением и без), Round Robin (RR).
"""
import sys
import os
import argparse
from collections import deque
from typing import List, Tuple, Dict, Any, Optional

class Process:
    def __init__(self, pid: str, arrival: int, burst: int, priority: int = 1):
        self.pid = pid
        self.arrival = int(arrival)
        self.burst = int(burst)
        self.priority = int(priority)
        self.remaining = int(burst)
        self.dynamic_priority = int(priority)
        self.first_start: Optional[int] = None
        self.finish_time: Optional[int] = None
        self.wait_time_ready: int = 0

    def copy(self) -> "Process":
        return Process(self.pid, self.arrival, self.burst, self.priority)

def load_processes(filename: str) -> List[Process]:
    processes = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            pid = parts[0]
            arrival = int(parts[1])
            burst = int(parts[2])
            priority = int(parts[3]) if len(parts) > 3 else 1
            processes.append(Process(pid, arrival, burst, priority))
    return processes

def compress_intervals(intervals: List[Tuple[int, int, str]]) -> List[Tuple[int, int, str]]:
    """Объединяет последовательные смежные интервалы одного и того же процесса."""
    if not intervals:
        return []
    res = []
    cur_start, cur_end, cur_pid = intervals[0]
    for s, e, p in intervals[1:]:
        if p == cur_pid and s == cur_end:
            cur_end = e
        else:
            res.append((cur_start, cur_end, cur_pid))
            cur_start, cur_end, cur_pid = s, e, p
    res.append((cur_start, cur_end, cur_pid))
    return res

def simulate_fcfs(procs: List[Process]) -> List[Tuple[int, int, str]]:
    procs = sorted(procs, key=lambda p: (p.arrival, p.pid))
    t = 0
    raw_intervals = []
    for p in procs:
        if t < p.arrival:
            raw_intervals.append((t, p.arrival, "IDLE"))
            t = p.arrival
        if p.first_start is None:
            p.first_start = t
        start = t
        t += p.burst
        p.finish_time = t
        p.remaining = 0
        raw_intervals.append((start, t, p.pid))
    return raw_intervals

def simulate_sjf(procs: List[Process]) -> List[Tuple[int, int, str]]:
    """SJF (невытесняющий). При равенстве burst выбирается по arrival, затем по PID."""
    unstarted = sorted([p for p in procs], key=lambda x: x.arrival)
    ready = []
    t = 0
    raw_intervals = []
    finished = 0
    n = len(procs)

    while finished < n:
        while unstarted and unstarted[0].arrival <= t:
            ready.append(unstarted.pop(0))

        if not ready:
            next_arr = unstarted[0].arrival
            raw_intervals.append((t, next_arr, "IDLE"))
            t = next_arr
            continue

        # Выбираем процесс с наименьшим burst
        ready.sort(key=lambda p: (p.burst, p.arrival, p.pid))
        p = ready.pop(0)

        if p.first_start is None:
            p.first_start = t
        start = t
        t += p.burst
        p.finish_time = t
        p.remaining = 0
        finished += 1
        raw_intervals.append((start, t, p.pid))

    return raw_intervals

def simulate_srtf(procs: List[Process]) -> List[Tuple[int, int, str]]:
    """SRTF (вытесняющий SJF). Шаг симуляции 1 такт или до ближайшего события."""
    unstarted = sorted([p for p in procs], key=lambda x: x.arrival)
    ready: List[Process] = []
    t = 0
    raw_intervals = []
    finished = 0
    n = len(procs)
    cur_proc: Optional[Process] = None

    while finished < n:
        while unstarted and unstarted[0].arrival == t:
            ready.append(unstarted.pop(0))

        if cur_proc is not None:
            ready.append(cur_proc)
            cur_proc = None

        if not ready:
            next_t = unstarted[0].arrival if unstarted else t + 1
            raw_intervals.append((t, next_t, "IDLE"))
            t = next_t
            continue

        # Выбираем с минимальным remaining
        ready.sort(key=lambda p: (p.remaining, p.arrival, p.pid))
        cur_proc = ready.pop(0)

        if cur_proc.first_start is None:
            cur_proc.first_start = t

        raw_intervals.append((t, t + 1, cur_proc.pid))
        cur_proc.remaining -= 1
        t += 1

        if cur_proc.remaining == 0:
            cur_proc.finish_time = t
            finished += 1
            cur_proc = None

    return compress_intervals(raw_intervals)

def simulate_priority(procs: List[Process], aging: bool = False, aging_interval: int = 5) -> List[Tuple[int, int, str]]:
    """Вытесняющее приоритетное планирование. Меньшее число = более высокий приоритет."""
    unstarted = sorted([p for p in procs], key=lambda x: x.arrival)
    ready: List[Process] = []
    t = 0
    raw_intervals = []
    finished = 0
    n = len(procs)
    cur_proc: Optional[Process] = None

    while finished < n:
        while unstarted and unstarted[0].arrival == t:
            ready.append(unstarted.pop(0))

        # Применяем механизм старения (aging) к процессам, ожидающим в ready queue
        if aging:
            for p in ready:
                p.wait_time_ready += 1
                if p.wait_time_ready >= aging_interval:
                    if p.dynamic_priority > 1:
                        p.dynamic_priority -= 1
                    p.wait_time_ready = 0

        if cur_proc is not None:
            ready.append(cur_proc)
            cur_proc = None

        if not ready:
            next_t = unstarted[0].arrival if unstarted else t + 1
            raw_intervals.append((t, next_t, "IDLE"))
            t = next_t
            continue

        # Сортировка по приоритету (меньшее значение -> выше), затем по arrival, затем по PID
        ready.sort(key=lambda p: (p.dynamic_priority, p.arrival, p.pid))
        cur_proc = ready.pop(0)

        if cur_proc.first_start is None:
            cur_proc.first_start = t

        raw_intervals.append((t, t + 1, cur_proc.pid))
        cur_proc.remaining -= 1
        t += 1

        if cur_proc.remaining == 0:
            cur_proc.finish_time = t
            finished += 1
            cur_proc = None

    return compress_intervals(raw_intervals)

def simulate_rr(procs: List[Process], quantum: int = 3) -> List[Tuple[int, int, str]]:
    """
    Round Robin (RR).
    Соглашение: процесс, прибывший в момент t, ставится в очередь раньше процесса,
    вытесненного в тот же момент t!
    """
    unstarted = sorted([p for p in procs], key=lambda x: x.arrival)
    queue: deque = deque()
    t = 0
    raw_intervals = []
    finished = 0
    n = len(procs)

    while finished < n:
        # Проверяем прибытие в момент t
        while unstarted and unstarted[0].arrival <= t:
            queue.append(unstarted.pop(0))

        if not queue:
            next_t = unstarted[0].arrival
            raw_intervals.append((t, next_t, "IDLE"))
            t = next_t
            while unstarted and unstarted[0].arrival <= t:
                queue.append(unstarted.pop(0))

        cur = queue.popleft()
        if cur.first_start is None:
            cur.first_start = t

        run_time = min(quantum, cur.remaining)
        start = t
        t += run_time
        cur.remaining -= run_time
        raw_intervals.append((start, t, cur.pid))

        # ВАЖНО: Сначала добавляем все процессы, прибывшие во время работы или ровно в момент t
        while unstarted and unstarted[0].arrival <= t:
            queue.append(unstarted.pop(0))

        # И только затем, если текущий процесс не завершился, возвращаем его в конец очереди
        if cur.remaining > 0:
            queue.append(cur)
        else:
            cur.finish_time = t
            finished += 1

    return compress_intervals(raw_intervals)

def simulate(processes: List[Process], algorithm: str, **params) -> Tuple[List[Process], List[Tuple[int, int, str]]]:
    """Единая точка входа симуляции."""
    # Создаем независимые копии процессов для симуляции
    procs = [p.copy() for p in processes]
    algo = algorithm.lower()

    if algo == "fcfs":
        intervals = simulate_fcfs(procs)
    elif algo == "sjf":
        intervals = simulate_sjf(procs)
    elif algo == "srtf":
        intervals = simulate_srtf(procs)
    elif algo == "priority":
        aging = params.get("aging", False)
        aging_interval = params.get("aging_interval", 5)
        intervals = simulate_priority(procs, aging=aging, aging_interval=aging_interval)
    elif algo == "rr":
        q = int(params.get("quantum", 3))
        intervals = simulate_rr(procs, quantum=q)
    else:
        raise ValueError(f"Неизвестный алгоритм: {algorithm}")

    return procs, intervals

def calculate_metrics(procs: List[Process], intervals: List[Tuple[int, int, str]]) -> Dict[str, Any]:
    n = len(procs)
    total_waiting = 0
    total_turnaround = 0
    total_response = 0

    proc_metrics = {}
    for p in procs:
        turnaround = p.finish_time - p.arrival
        waiting = turnaround - p.burst
        response = p.first_start - p.arrival
        total_waiting += waiting
        total_turnaround += turnaround
        total_response += response
        proc_metrics[p.pid] = {
            "arrival": p.arrival,
            "burst": p.burst,
            "finish": p.finish_time,
            "turnaround": turnaround,
            "waiting": waiting,
            "response": response,
        }

    # Подсчет переключений контекста (смена PID)
    context_switches = 0
    total_busy = 0
    last_pid = None
    for s, e, pid in intervals:
        if pid != "IDLE":
            total_busy += (e - s)
            if last_pid is not None and last_pid != pid:
                context_switches += 1
            last_pid = pid

    total_time = intervals[-1][1] if intervals else 0
    cpu_util = (total_busy / total_time * 100.0) if total_time > 0 else 0.0

    return {
        "avg_waiting": total_waiting / n,
        "avg_turnaround": total_turnaround / n,
        "avg_response": total_response / n,
        "cpu_utilization": cpu_util,
        "context_switches": context_switches,
        "total_time": total_time,
        "per_process": proc_metrics
    }

def print_gantt_chart(intervals: List[Tuple[int, int, str]]):
    print("Диаграмма Ганта:")
    timeline = "|"
    time_marks = f"{intervals[0][0]}"
    for s, e, pid in intervals:
        block = f" {pid} |"
        timeline += block
        time_marks += f"{e:>{len(block)}}"
    print(timeline)
    print(time_marks)

def main():
    parser = argparse.ArgumentParser(description="Симулятор планирования CPU (ПР-5 Вариант B)")
    parser.add_argument("file", help="Файл с описанием процессов (например: set1.txt)")
    parser.add_argument("--algo", default="rr", choices=["fcfs", "sjf", "srtf", "priority", "rr"], help="Алгоритм")
    parser.add_argument("--quantum", type=int, default=3, help="Квант времени для RR (по умолчанию 3)")
    parser.add_argument("--aging", action="store_true", help="Включить старение для Priority")
    parser.add_argument("--all", action="store_true", help="Сравнить все алгоритмы на переданном файле")
    parser.add_argument("--sweep-rr", action="store_true", help="Исследовать зависимость RR от кванта (1..10)")

    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Ошибка: файл {args.file} не найден.", file=sys.stderr)
        sys.exit(1)

    procs = load_processes(args.file)
    print(f"Загружено {len(procs)} процессов из {args.file}:")
    for p in procs:
        print(f"  {p.pid}: arrival={p.arrival}, burst={p.burst}, priority={p.priority}")
    print()

    if args.sweep_rr:
        print(f"=== Исследование Round Robin (квант 1..10) на файле {args.file} ===")
        print(f"{'Квант (q)':<10} | {'Среднее ожидание':<18} | {'Средний оборот':<16} | {'Переключения контекста':<22}")
        print("-" * 72)
        for q in range(1, 11):
            sim_procs, intervals = simulate(procs, "rr", quantum=q)
            m = calculate_metrics(sim_procs, intervals)
            print(f"{q:<10} | {m['avg_waiting']:<18.2f} | {m['avg_turnaround']:<16.2f} | {m['context_switches']:<22}")
        return

    if args.all:
        algos = [
            ("FCFS", "fcfs", {}),
            ("SJF", "sjf", {}),
            ("SRTF", "srtf", {}),
            ("Priority (без старения)", "priority", {"aging": False}),
            ("Priority (со старением)", "priority", {"aging": True, "aging_interval": 3}),
            (f"RR (q={args.quantum})", "rr", {"quantum": args.quantum}),
        ]
        print(f"=== Сравнение всех алгоритмов на наборе {args.file} ===")
        print(f"{'Алгоритм':<26} | {'Ср. ожидание':<14} | {'Ср. оборот':<13} | {'Ср. отклик':<12} | {'Загрузка CPU':<13} | {'Переключения':<12}")
        print("-" * 105)
        for label, algo_name, params in algos:
            sim_procs, intervals = simulate(procs, algo_name, **params)
            m = calculate_metrics(sim_procs, intervals)
            print(f"{label:<26} | {m['avg_waiting']:<14.2f} | {m['avg_turnaround']:<13.2f} | {m['avg_response']:<12.2f} | {m['cpu_utilization']:<11.1f}% | {m['context_switches']:<12}")
        return

    # Одиночный запуск
    sim_procs, intervals = simulate(procs, args.algo, quantum=args.quantum, aging=args.aging)
    metrics = calculate_metrics(sim_procs, intervals)

    print(f"=== Результаты: {args.algo.upper()} (quantum={args.quantum if args.algo == 'rr' else '-'}) ===")
    print_gantt_chart(intervals)
    print()
    print("Метрики по процессам:")
    print(f"{'PID':<6} | {'Прибытие':<10} | {'Длительность':<13} | {'Завершение':<12} | {'Оборот':<8} | {'Ожидание':<10} | {'Отклик':<8}")
    print("-" * 75)
    for pid, pm in metrics["per_process"].items():
        print(f"{pid:<6} | {pm['arrival']:<10} | {pm['burst']:<13} | {pm['finish']:<12} | {pm['turnaround']:<8} | {pm['waiting']:<10} | {pm['response']:<8}")
    print("-" * 75)
    print(f"Среднее время ожидания (Average Waiting Time):   {metrics['avg_waiting']:.2f}")
    print(f"Среднее время оборота (Average Turnaround Time): {metrics['avg_turnaround']:.2f}")
    print(f"Среднее время отклика (Average Response Time):   {metrics['avg_response']:.2f}")
    print(f"Загрузка CPU (CPU Utilization):                  {metrics['cpu_utilization']:.1f}%")
    print(f"Число переключений контекста (Context switches): {metrics['context_switches']}")

if __name__ == "__main__":
    main()
