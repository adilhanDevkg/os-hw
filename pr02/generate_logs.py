#!/usr/bin/env python3
"""
Скрипт генерации 50 файлов логов для ПР-2.
Формат записей: YYYY-MM-DD HH:MM:SS LEVEL module=MODULE msg=MESSAGE
"""
import os
import random
from datetime import datetime, timedelta

MODULES = ["net", "auth", "db", "api", "storage", "cache", "worker"]
LEVELS = ["INFO", "WARN", "ERROR", "DEBUG"]
MESSAGES = {
    "net": ["connection timeout", "socket reset by peer", "packet loss detected", "handshake failed"],
    "auth": ["invalid password", "token expired", "unauthorized access", "session terminated"],
    "db": ["deadlock detected", "slow query > 500ms", "connection pool exhausted", "foreign key violation"],
    "api": ["rate limit exceeded", "bad request 400", "gateway timeout 504", "internal server error 500"],
    "storage": ["disk space low", "write buffer full", "IO error sector 42", "inode exhausted"],
    "cache": ["cache miss spike", "key evictions high", "redis node unavailable", "serialization error"],
    "worker": ["task retry failed", "worker thread crashed", "memory limit exceeded", "queue backlog growing"],
}

def generate_logs(out_dir: str, num_files: int = 50, lines_per_file: int = 100):
    os.makedirs(out_dir, exist_ok=True)
    base_time = datetime(2026, 2, 14, 10, 0, 0)
    
    # Зафиксируем сид для воспроизводимости
    random.seed(42)

    for i in range(1, num_files + 1):
        filename = os.path.join(out_dir, f"{i:02d}.log")
        with open(filename, "w", encoding="utf-8") as f:
            curr_time = base_time + timedelta(minutes=i * 2)
            for _ in range(lines_per_file):
                curr_time += timedelta(seconds=random.randint(1, 15))
                level = random.choices(LEVELS, weights=[40, 25, 25, 10])[0]
                mod = random.choice(MODULES)
                msg = random.choice(MESSAGES[mod])
                f.write(f"{curr_time.strftime('%Y-%m-%d %H:%M:%S')} {level} module={mod} msg={msg}\n")
    print(f"[OK] Сгенерировано {num_files} файлов логов в каталоге {out_dir}")

if __name__ == "__main__":
    target = os.path.join(os.path.dirname(__file__), "data")
    generate_logs(target, 50, 120)
