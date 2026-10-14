# Учебно-методический комплекс: Практические работы № 1–7 (Вариант B)

**Дисциплина:** Проектирование / Операционные системы  
**Учебное заведение:** Международный колледж IT и бизнеса «Salymbekov University»  
**Сложность:** Уровень B (Основной вариант)  
**Разработчик:** Аденов А. Б.  

---

## 1. Обзор выполненных работ

Каждая практическая работа выполнена в соответствии с методическими требованиями:
* Создан отдельный каталог `prNN/`;
* Написан подробный файл `README.md` (цель, связь с лекциями, запуск, листинги, результаты измерений, ответы на теоретические и контрольные вопросы, выводы);
* Код запускается одной командой (`./run.sh`);
* Программы снабжены проверками инвариантов (`assert`), защитой от ошибок и утечек ресурсов.

| Работа | Тема работы | Ключевой навык | Основные файлы | Статус |
|---|---|---|---|---|
| **ПР-1** | Установка Linux и знакомство с терминалом | Права доступа, пользователи, группы, SGID, sticky-bit, `su` vs `sudo` | [setup_shared.sh](pr01/setup_shared.sh), [README.md](pr01/README.md) | **Выполнено** |
| **ПР-2** | Bash и системные вызовы | Парсинг и фильтрация логов, анализ системных вызовов через `strace`, Python vs `cat` | [report.sh](pr02/report.sh), [hello.py](pr02/hello.py), [README.md](pr02/README.md) | **Выполнено** |
| **ПР-3** | Процессы в Linux | Дерево процессов по `/proc`, `fork+exec` runner, Zombie, Orphan & Subreaper, Copy-On-Write | [ptree.py](pr03/ptree.py), [runner.py](pr03/runner.py), [zombie.py](pr03/zombie.py), [orphan.py](pr03/orphan.py), [cow_demo.py](pr03/cow_demo.py) | **Выполнено** |
| **ПР-4** | Потоки | Разделение памяти, GIL, CPU-bound (сумма чисел) vs I/O-bound (сетевые запросы) | [sum_benchmark.py](pr04/sum_benchmark.py), [io_benchmark.py](pr04/io_benchmark.py), [memory_sharing_demo.py](pr04/memory_sharing_demo.py) | **Выполнено** |
| **ПР-5** | Симулятор планирования CPU | FCFS, SJF, SRTF, Preemptive Priority с Aging, Round Robin (квант 1..10), верификация с эталоном | [sched.py](pr05/sched.py), [test_sched.py](pr05/test_sched.py), [set1.txt](pr05/set1.txt), [set2.txt](pr05/set2.txt), [set3.txt](pr05/set3.txt) | **Выполнено** |
| **ПР-6** | Синхронизация | Bounded Buffer (семафоры vs условная переменная), многофазный барьер, ложное пробуждение (`if` vs `while`), гонка | [prod_cons_sem.py](pr06/prod_cons_sem.py), [prod_cons_cv.py](pr06/prod_cons_cv.py), [barrier_demo.py](pr06/barrier_demo.py), [spurious_wakeup_demo.py](pr06/spurious_wakeup_demo.py) | **Выполнено** |
| **ПР-7** | Межпроцессное взаимодействие (IPC) | Клиент-сервер на FIFO, параллельный UDS сервер (fork), Shared Memory vs Pipe (10^7 чисел) | [fifo_server.py](pr07/fifo_server.py), [uds_server.py](pr07/uds_server.py), [shm_vs_pipe.py](pr07/shm_vs_pipe.py) | **Выполнено** |

---

## 2. Структура репозитория

```text
os-practicals/
├── README.md                 # Общее описание и навигация по всему курсу
├── run_all.sh                # Запуск всех практических работ одной командой
├── pr01/                     # ПР-1: Пользователи, права, bashrc, su/sudo
│   ├── README.md
│   ├── setup_shared.sh
│   └── run.sh
├── pr02/                     # ПР-2: Автоматизация bash, системные вызовы strace
│   ├── README.md
│   ├── report.sh
│   ├── hello.py
│   ├── generate_logs.py
│   ├── trace.txt
│   └── run.sh
├── pr03/                     # ПР-3: Процессы, ptree (/proc), fork/exec, COW, Zombie/Orphan
│   ├── README.md
│   ├── ptree.py
│   ├── runner.py
│   ├── zombie.py
│   ├── orphan.py
│   ├── cow_demo.py
│   └── run.sh
├── pr04/                     # ПР-4: Потоки, GIL, бенчмарки CPU/IO, разделение памяти
│   ├── README.md
│   ├── generate_numbers.py
│   ├── sum_benchmark.py
│   ├── io_benchmark.py
│   ├── memory_sharing_demo.py
│   └── run.sh
├── pr05/                     # ПР-5: Симулятор планирования CPU (FCFS, SJF, SRTF, RR, Priority)
│   ├── README.md
│   ├── sched.py
│   ├── test_sched.py
│   ├── set1.txt
│   ├── set2.txt
│   ├── set3.txt
│   └── run.sh
├── pr06/                     # ПР-6: Синхронизация (Семафоры, Condition, Барьер, Mesa-пробуждение)
│   ├── README.md
│   ├── prod_cons_sem.py
│   ├── prod_cons_cv.py
│   ├── barrier_demo.py
│   ├── spurious_wakeup_demo.py
│   ├── race_condition_demo.py
│   ├── race_condition_fixed.py
│   └── run.sh
└── pr07/                     # ПР-7: Межпроцессное взаимодействие (FIFO, UDS, Shared Memory, Pipe)
    ├── README.md
    ├── fifo_server.py
    ├── fifo_client.py
    ├── uds_server.py
    ├── uds_client.py
    ├── shm_vs_pipe.py
    └── run.sh
```

---

## 3. Запуск

### Запуск всех работ разом:
```bash
chmod +x run_all.sh
./run_all.sh
```

### Запуск любой отдельной работы:
```bash
cd pr05
./run.sh
```
