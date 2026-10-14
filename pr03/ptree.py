#!/usr/bin/env python3
"""
Практическая работа № 3. Вариант B. Задание 1.
ptree.py: Построение дерева процессов текущего пользователя по данным /proc (без вызова ps).
Отображает: PID, состояние процесса (State), использование физической памяти (RSS).
"""
import os
import sys

def parse_proc_status(pid_dir: str):
    """Парсит файл /proc/<pid>/status и возвращает словарь с полями."""
    status_file = os.path.join(pid_dir, "status")
    if not os.path.isfile(status_file):
        return None
    
    info = {"pid": None, "ppid": None, "name": "unknown", "state": "?", "rss": "0 kB", "uid": None}
    try:
        with open(status_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                parts = line.split(":", 1)
                if len(parts) != 2:
                    continue
                key, val = parts[0].strip(), parts[1].strip()
                if key == "Name":
                    info["name"] = val
                elif key == "State":
                    # Например: S (sleeping) -> берем 'S'
                    info["state"] = val.split()[0]
                elif key == "Pid":
                    info["pid"] = int(val)
                elif key == "PPid":
                    info["ppid"] = int(val)
                elif key == "Uid":
                    # Uid: real effective saved fs
                    info["uid"] = int(val.split()[0])
                elif key == "VmRSS":
                    info["rss"] = val
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return None
    return info

def get_user_processes():
    """Считывает процессы текущего пользователя из /proc."""
    proc_root = "/proc"
    my_uid = os.getuid()
    processes = {}

    if not os.path.exists(proc_root):
        # Режим fallback для сред без виртуальной ФС /proc (например, macOS)
        print("[!] Внимание: /proc не обнаружен (ОС отлична от Linux). Используется демонстрационный режим.", file=sys.stderr)
        # Генерируем репрезентативное дерево для демонстрации структуры
        return {
            1001: {"pid": 1001, "ppid": 1, "name": "systemd", "state": "S", "rss": "15340 kB", "uid": my_uid},
            1050: {"pid": 1050, "ppid": 1001, "name": "bash", "state": "S", "rss": "6120 kB", "uid": my_uid},
            1102: {"pid": 1102, "ppid": 1050, "name": "python3", "state": "R", "rss": "18400 kB", "uid": my_uid},
            1103: {"pid": 1103, "ppid": 1102, "name": "worker_1", "state": "S", "rss": "12300 kB", "uid": my_uid},
            1104: {"pid": 1104, "ppid": 1102, "name": "worker_2", "state": "S", "rss": "12310 kB", "uid": my_uid},
            1060: {"pid": 1060, "ppid": 1001, "name": "sshd-session", "state": "S", "rss": "4200 kB", "uid": my_uid},
        }

    for entry in os.listdir(proc_root):
        if entry.isdigit():
            pid_dir = os.path.join(proc_root, entry)
            info = parse_proc_status(pid_dir)
            if info and info["uid"] == my_uid and info["pid"] is not None:
                processes[info["pid"]] = info

    return processes

def print_tree(tree, pid, prefix="", is_last=True):
    node = tree[pid]
    connector = "└── " if is_last else "├── "
    state_desc = {
        "R": "Running",
        "S": "Sleeping",
        "D": "Disk sleep",
        "Z": "Zombie",
        "T": "Stopped"
    }.get(node["state"], node["state"])

    print(f"{prefix}{connector}{node['name']} (PID: {node['pid']}, State: {node['state']} [{state_desc}], RSS: {node['rss']})")

    children = tree[pid].get("children", [])
    new_prefix = prefix + ("    " if is_last else "│   ")
    for i, child_pid in enumerate(children):
        print_tree(tree, child_pid, new_prefix, i == len(children) - 1)

def main():
    procs = get_user_processes()
    if not procs:
        print("Процессов для текущего пользователя не найдено.")
        return

    # Добавляем список детей
    for p in procs.values():
        p["children"] = []

    roots = []
    for pid, p in procs.items():
        ppid = p["ppid"]
        if ppid in procs and ppid != pid:
            procs[ppid]["children"].append(pid)
        else:
            roots.append(pid)

    print(f"=== Дерево процессов пользователя UID={os.getuid()} (по данным /proc) ===")
    for i, root_pid in enumerate(sorted(roots)):
        print_tree(procs, root_pid, is_last=(i == len(roots) - 1))

if __name__ == "__main__":
    main()
