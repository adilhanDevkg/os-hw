#!/usr/bin/env python3
"""
Автоматический тест верификации симулятора планирования с эталоном из методички (set1.txt).
"""
import os
import sys
from sched import load_processes, simulate, calculate_metrics

def main():
    set1_path = os.path.join(os.path.dirname(__file__), "set1.txt")
    procs = load_processes(set1_path)

    print("=== Самопроверка симулятора по контрольному набору set1.txt ===")

    # 1. SRTF
    sim_p, intervals = simulate(procs, "srtf")
    m_srtf = calculate_metrics(sim_p, intervals)
    print(f"SRTF: avg_waiting={m_srtf['avg_waiting']:.2f} (эталон: 6.50), avg_turnaround={m_srtf['avg_turnaround']:.2f} (эталон: 13.00)")
    assert abs(m_srtf['avg_waiting'] - 6.5) < 1e-4, f"SRTF avg_waiting mismatch: {m_srtf['avg_waiting']}"
    assert abs(m_srtf['avg_turnaround'] - 13.0) < 1e-4, f"SRTF avg_turnaround mismatch: {m_srtf['avg_turnaround']}"
    print("  [✓] SRTF полностью совпадает с эталоном!")

    # 2. RR (q = 3)
    sim_p, intervals = simulate(procs, "rr", quantum=3)
    m_rr = calculate_metrics(sim_p, intervals)
    print(f"RR(q=3): avg_waiting={m_rr['avg_waiting']:.2f} (эталон: 13.50), avg_turnaround={m_rr['avg_turnaround']:.2f} (эталон: 20.00)")
    assert abs(m_rr['avg_waiting'] - 13.5) < 1e-4, f"RR avg_waiting mismatch: {m_rr['avg_waiting']}"
    assert abs(m_rr['avg_turnaround'] - 20.0) < 1e-4, f"RR avg_turnaround mismatch: {m_rr['avg_turnaround']}"
    print("  [✓] RR (q=3) полностью совпадает с эталоном!")

    print("\n[✓] ВСЕ ТЕСТЫ ЭТАЛОНА УСПЕШНО ПРОЙДЕНЫ!")

if __name__ == "__main__":
    main()
