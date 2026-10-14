#!/usr/bin/env bash
# ==============================================================================
# Практическая работа № 1. Вариант B
# Скрипт автоматизированной демонстрации и настройки окружения
# ==============================================================================
set -euo pipefail

SHARED_DIR="/srv/shared"
DEV_GROUP="developers"
TEST_USER="student2"

echo "=== [1/5] Проверка прав суперпользователя ==="
if [[ $EUID -ne 0 ]]; then
    echo "Внимание: данный скрипт выполняет системное администрирование (/srv/shared, useradd)."
    echo "Запуск от обычного пользователя выполнит безопасную симуляцию в локальном каталоге."
    RUN_MODE="simulation"
    SHARED_DIR="/tmp/os_pr01_srv_shared"
else
    RUN_MODE="real"
fi

echo "Режим выполнения: $RUN_MODE"
echo "Целевой каталог: $SHARED_DIR"

echo ""
echo "=== [2/5] Создание группы $DEV_GROUP и пользователя $TEST_USER ==="
if [[ "$RUN_MODE" == "real" ]]; then
    if ! getent group "$DEV_GROUP" >/dev/null 2>&1; then
        groupadd "$DEV_GROUP"
        echo "Группа $DEV_GROUP успешно создана."
    else
        echo "Группа $DEV_GROUP уже существует."
    fi

    if ! id -u "$TEST_USER" >/dev/null 2>&1; then
        useradd -m -s /bin/bash -g "$DEV_GROUP" "$TEST_USER"
        echo "Пользователь $TEST_USER успешно создан и добавлен в группу $DEV_GROUP."
    else
        echo "Пользователь $TEST_USER уже существует."
    fi
else
    echo "[Симуляция] Команды для Ubuntu:"
    echo "  sudo groupadd $DEV_GROUP"
    echo "  sudo useradd -m -s /bin/bash -g $DEV_GROUP $TEST_USER"
fi

echo ""
echo "=== [3/5] Настройка каталога $SHARED_DIR и прав доступа ==="
mkdir -p "$SHARED_DIR"

if [[ "$RUN_MODE" == "real" ]]; then
    chown root:"$DEV_GROUP" "$SHARED_DIR"
    # 2775: rwxrwxr-x c SGID (2) - все создаваемые внутри файлы наследуют группу developers
    chmod 2775 "$SHARED_DIR"
    echo "Права на $SHARED_DIR установлены в 2775 (rwxrwxr-x + SGID)."
else
    chmod 775 "$SHARED_DIR"
    echo "[Симуляция] Права на $SHARED_DIR установлены: rwxrwxr-x"
fi

ls -ld "$SHARED_DIR"

echo ""
echo "=== [4/5] Тест создания файла от $TEST_USER и попытка удаления ==="
TEST_FILE="$SHARED_DIR/student2_work.txt"

if [[ "$RUN_MODE" == "real" ]]; then
    # Создаем файл от имени student2
    su - "$TEST_USER" -c "echo 'Данные студента student2' > '$TEST_FILE'"
    echo "Файл создан от имени $TEST_USER:"
    ls -l "$TEST_FILE"

    echo ""
    echo "Попытка удаления файла от имени основного пользователя (non-root):"
    MAIN_USER="${SUDO_USER:-$(logname 2>/dev/null || whoami)}"
    echo "Основной пользователь: $MAIN_USER"

    # Проверка, входит ли основной пользователь в developers
    if id -nG "$MAIN_USER" | grep -qw "$DEV_GROUP"; then
        echo "Пользователь $MAIN_USER входит в группу $DEV_GROUP."
        echo "Поскольку SGID=2775 (без sticky bit), член группы МОЖЕТ удалить файл."
        echo "Проверяем удаление:"
        su - "$MAIN_USER" -c "rm -f '$TEST_FILE'" && echo "Файл успешно удален (права записи каталога позволили удаление)."
    else
        echo "Пользователь $MAIN_USER НЕ входит в группу $DEV_GROUP (только чтение r-x)."
        echo "Попытка удаления завершится отказом в доступе (Permission denied):"
        su - "$MAIN_USER" -c "rm -f '$TEST_FILE'" 2>&1 || true
    fi

    echo ""
    echo "Демонстрация Sticky Bit (t-бит, как в /tmp, 1775):"
    chmod 1775 "$SHARED_DIR"
    su - "$TEST_USER" -c "echo 'Защищенные данные' > '$TEST_FILE'"
    echo "Создан новый файл со sticky-bit на каталоге. Попытка удаления другим членом группы:"
    # Даже если пользователь в группе, удалить чужой файл при sticky bit он не сможет
    ls -ld "$SHARED_DIR"
else
    echo "[Симуляция] Создание и проверка прав:"
    echo "Hello from student2" > "$TEST_FILE"
    ls -l "$TEST_FILE"
    echo "Файл успешно создан в $SHARED_DIR."
fi

echo ""
echo "=== [5/5] Настройка ~/.bashrc: алиасы и переменная окружения ==="
BASHRC_SAMPLE="/tmp/sample_bashrc"
cat << 'EOF' > "$BASHRC_SAMPLE"
# Добавлено для ПР-1 (Вариант B)
export OS_LAB_ENV="OperatingSystems_Salymbekov_2026"
alias ll='ls -lah --color=auto'
alias myproc='ps -u $USER -o pid,stat,time,comm'
EOF

echo "Сгенерирован блок настроек для ~/.bashrc:"
cat "$BASHRC_SAMPLE"
echo ""
echo "Проверка работы в подоболочке bash:"
bash --rcfile "$BASHRC_SAMPLE" -i -c 'echo "OS_LAB_ENV = $OS_LAB_ENV"; alias ll; alias myproc'

echo ""
echo "=== Скрипт ПР-1 успешно завершил работу! ==="
