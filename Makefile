.PHONY: help setup install run test clean docker-build docker-run docker-stop logs venv init-db lint format

# Переменные
PYTHON := python3
PIP := pip
VENV := venv

# Цвета для вывода
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)📦 Telegram Bot MVP - Доступные команды:$(NC)"
	@echo ""
	@echo "$(GREEN)Инициализация:$(NC)"
	@echo "  make setup              Полная инициализация проекта (venv + install + init-db)"
	@echo "  make venv               Создать виртуальное окружение"
	@echo "  make install            Установить зависимости"
	@echo "  make init-db            Инициализировать БД и примеры"
	@echo ""
	@echo "$(GREEN)Запуск:$(NC)"
	@echo "  make run                Запустить бота"
	@echo "  make run-dev            Запустить бота в режиме разработки"
	@echo ""
	@echo "$(GREEN)Тестирование и отладка:$(NC)"
	@echo "  make test               Запустить все тесты"
	@echo "  make test-verbose       Запустить тесты с подробным выводом"
	@echo "  make lint               Проверка кода (pylint)"
	@echo "  make format             Форматировать код (black)"
	@echo "  make logs               Просмотр логов в реальном времени"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  make docker-build       Собрать Docker образ"
	@echo "  make docker-run         Запустить бота в Docker"
	@echo "  make docker-stop        Остановить Docker контейнер"
	@echo "  make docker-logs        Логи Docker контейнера"
	@echo ""
	@echo "$(GREEN)Обслуживание:$(NC)"
	@echo "  make clean              Очистить кэш и логи"
	@echo "  make clean-db           Удалить БД (пересоздает при run)"
	@echo "  make requirements-update Обновить requirements.txt"
	@echo "  make admin-add          Добавить администратора"
	@echo ""
	@echo "$(GREEN)Комплексные команды:$(NC)"
	@echo "  make all                setup + run (полный цикл)"
	@echo "  make dev                setup + run-dev"
	@echo ""

# ============================================================================
# ИНИЦИАЛИЗАЦИЯ
# ============================================================================

setup: venv install init-db
	@echo "$(GREEN)✅ Инициализация завершена!$(NC)"
	@echo "$(YELLOW)Запустите 'make run' для старта бота$(NC)"

venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(BLUE)📦 Создание виртуального окружения...$(NC)"; \
		$(PYTHON) -m venv $(VENV); \
		echo "$(GREEN)✅ Виртуальное окружение создано$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Виртуальное окружение уже существует$(NC)"; \
	fi

install: venv
	@echo "$(BLUE)📥 Установка зависимостей...$(NC)"
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Зависимости установлены$(NC)"

init-db:
	@echo "$(BLUE)🗄️  Инициализация БД...$(NC)"
	. $(VENV)/bin/activate && $(PYTHON) samples.py
	@echo "$(GREEN)✅ БД инициализирована$(NC)"

# ============================================================================
# ЗАПУСК
# ============================================================================

run: install
	@echo "$(GREEN)🚀 Запуск бота...$(NC)"
	. $(VENV)/bin/activate && $(PYTHON) main.py

run-dev: install
	@echo "$(GREEN)🚀 Запуск бота в режиме разработки...$(NC)"
	. $(VENV)/bin/activate && $(PYTHON) -u main.py

# ============================================================================
# ТЕСТИРОВАНИЕ И ОТЛАДКА
# ============================================================================

test: install
	@echo "$(BLUE)🧪 Запуск тестов...$(NC)"
	. $(VENV)/bin/activate && $(PYTHON) -m unittest discover -s . -p "test_*.py" -v

test-verbose: install
	@echo "$(BLUE)🧪 Запуск тестов (подробно)...$(NC)"
	. $(VENV)/bin/activate && $(PYTHON) -m unittest test_bot.py -v

lint: install
	@echo "$(BLUE)📝 Проверка кода...$(NC)"
	. $(VENV)/bin/activate && $(PYTHON) -m pylint *.py --disable=all --enable=E,F || true

format: install
	@echo "$(BLUE)🎨 Форматирование кода...$(NC)"
	. $(VENV)/bin/activate && $(PYTHON) -m black *.py
	@echo "$(GREEN)✅ Код отформатирован$(NC)"

logs:
	@if [ -f "bot.log" ]; then \
		echo "$(BLUE)📋 Логи (Ctrl+C для выхода):$(NC)"; \
		tail -f bot.log; \
	else \
		echo "$(YELLOW)⚠️  bot.log не найден. Сначала запустите бота: make run$(NC)"; \
	fi

# ============================================================================
# DOCKER
# ============================================================================

docker-build:
	@echo "$(BLUE)🐳 Сборка Docker образа...$(NC)"
	docker-compose build
	@echo "$(GREEN)✅ Docker образ собран$(NC)"

docker-run: docker-build
	@echo "$(BLUE)🐳 Запуск бота в Docker...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Бот запущен в Docker$(NC)"
	@echo "$(YELLOW)Логи: make docker-logs$(NC)"

docker-stop:
	@echo "$(BLUE)🐳 Остановка Docker контейнера...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Docker контейнер остановлен$(NC)"

docker-logs:
	@echo "$(BLUE)📋 Логи Docker (Ctrl+C для выхода):$(NC)"
	docker-compose logs -f bot

# ============================================================================
# ОБСЛУЖИВАНИЕ
# ============================================================================

clean:
	@echo "$(BLUE)🧹 Очистка проекта...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -f bot.log
	@echo "$(GREEN)✅ Проект очищен$(NC)"

clean-db:
	@echo "$(YELLOW)⚠️  Удаление БД...$(NC)"
	rm -f bot_data.db
	@echo "$(GREEN)✅ БД удалена$(NC)"

clean-all: clean clean-db
	@echo "$(GREEN)✅ Полная очистка завершена$(NC)"

requirements-update: install
	@echo "$(BLUE)📦 Обновление requirements.txt...$(NC)"
	. $(VENV)/bin/activate && pip freeze > requirements.txt
	@echo "$(GREEN)✅ requirements.txt обновлен$(NC)"

admin-add:
	@echo "$(BLUE)👤 Добавление администратора$(NC)"
	@read -p "Введите ID администратора: " admin_id; \
	echo "Добавьте $$admin_id в ADMIN_IDS в config.py"; \
	echo "ADMIN_IDS = [$$admin_id]"

# ============================================================================
# КОМПЛЕКСНЫЕ КОМАНДЫ
# ============================================================================

all: clean setup run
	@echo "$(GREEN)✅ Полный цикл завершен$(NC)"

dev: clean setup run-dev
	@echo "$(GREEN)✅ Режим разработки запущен$(NC)"

# ============================================================================
# ИНФОРМАЦИЯ
# ============================================================================

info:
	@echo "$(BLUE)ℹ️  Информация о проекте:$(NC)"
	@echo "Python версия: $$($(PYTHON) --version)"
	@echo "Pip версия: $$($(PIP) --version)"
	@echo "Виртуальное окружение: $(VENV)"
	@if [ -d "$(VENV)" ]; then \
		echo "Статус: $(GREEN)✅ Установлено$(NC)"; \
	else \
		echo "Статус: $(YELLOW)❌ Не установлено$(NC)"; \
	fi
	@if [ -f ".env" ]; then \
		echo "Конфиг: $(GREEN)✅ Есть$(NC)"; \
	else \
		echo "Конфиг: $(YELLOW)❌ Нет (создайте .env)$(NC)"; \
	fi
	@if [ -f "bot_data.db" ]; then \
		echo "БД: $(GREEN)✅ Создана$(NC)"; \
	else \
		echo "БД: $(YELLOW)❌ Не создана (запустите make init-db)$(NC)"; \
	fi

# ============================================================================
# ЗНАЧЕНИЯ ПО УМОЛЧАНИЮ
# ============================================================================

.DEFAULT_GOAL := help