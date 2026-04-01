# 🔮 Tarot Magerie Bot

Телеграм-бот для гадания на Таро. Карта дня, перевёрнутые карты, случайная рубашка, одноразовый реролл.

---

## 🃏 Особенности

- **78 карт Таро** с прямыми и перевёрнутыми толкованиями (156 значений)
- **Случайная рубашка** из коллекции (админка для загрузки/удаления)
- **Одноразовый реролл** — кнопка исчезает после использования
- **Карта дня** — одна карта в сутки (сброс в полночь)
- **Админ-панель** — загрузка рубашек, получение file_id
- **PostgreSQL** — готова к масштабированию
- **Тесты** — 27 тестов (pytest, покрытие CRUD, сервисов, хэндлеров)

---

## 🐳 Стек

| Компонент | Технология |
|-----------|------------|
| **Язык** | Python 3.10+ |
| **Фреймворк** | aiogram 3.x |
| **База данных** | PostgreSQL / asyncpg |
| **Тестирование** | pytest, pytest-asyncio |
| **Контейнеризация** | Docker (в плане) |

---

## 🚀 Запуск

### Локально (PostgreSQL)

1. **Установить PostgreSQL** и создать БД:
   ```sql
   CREATE DATABASE tarot_bot;
   CREATE USER bot_user WITH PASSWORD 'bot_pass';
   GRANT ALL PRIVILEGES ON DATABASE tarot_bot TO bot_user;
   
2. **Клонировать репозиторий:**
    ```bash 
    git clone https://github.com/mageri9/TAROT_magerie_BOT.git
    cd tarot-bot

3. **Установить зависимости:**
    ```bash
    pip install -r requirements.txt
   (для тестов и скриптов)
    pip install -r requirements-dev.txt
   
4. **Создать .env по примеру .env.example**

5. **Запустить бота**


### 🧪Тестирование
    ```bash
    pytest tests/ -v

### 📁 Структура
src/
├── core/          # ядро (config, db, router)
├── crud/          # работа с БД
├── services/      # бизнес-логика
├── handlers/      # обработчики команд и колбэков
├── keyboards/     # клавиатуры
├── filters/       # фильтры (IsAdmin, ChatType)
├── middlewares/   # логирование
└── database/      # инициализация таблиц

scripts/
├── upload_deck.py        # загрузка колоды карт
├── migrate_cards.py      # миграция данных из SQLite
└── drop_table.py         # утилита для сброса таблиц

tests/
├── crud/                 # тесты CRUD
├── handlers/             # тесты хендлеров
├── services/             # тесты сервисов
└── conftest.py           # фикстуры для тестов


### 🔧 Команды бота
Команда	Описание
/start	Приветствие и главное меню
/admin	Админ-панель (только для указанных в .env)
🔮 КАРТА ДНЯ	Получить карту дня (рубашка + кнопка «Открыть»)

### 📄 Лицензия
MIT