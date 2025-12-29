# Binance Parser

## Описание проекта

Проект представляет собой асинхронный backend-сервис на **FastAPI**, реализующий:

- REST API для управления курсами валют
- WebSocket-канал для real-time уведомлений
- Фоновую задачу, периодически получающую данные с Binance
- Интеграцию с брокером сообщений **NATS**
- Асинхронную работу с базой данных **SQLite**

Архитектура построена на событийной модели: все изменения данных публикуются в NATS и рассылаются клиентам через WebSocket.

---

## Технологический стек

- Python 3.12
- FastAPI
- Uvicorn
- SQLAlchemy (async)
- SQLite
- httpx
- NATS (nats-py)
- Docker / Docker Compose

---

## Переменные окружения

Файл `.env`:

```env
SQLITE_DB_PATH=/app/data/db.sqlite
NATS_HOST=nats
NATS_PORT=4222
NATS_SUBJECT=prices.updates
FETCH_INTERVAL_SECONDS=30
DEFAULT_SYMBOLS=BTCUSDT,ETHUSDT
````

---

## Запуск проекта

### Требования

* Docker
* Docker Compose

---

### Запуск

В корне проекта выполнить:

```bash
docker-compose up --build
```

После успешного запуска будут подняты:

* backend-сервис FastAPI
* брокер сообщений NATS

---

## Проверка работы

### Swagger (REST API)

```
http://localhost:8000/docs
```

Доступные методы:

* `GET /prices`
* `GET /prices/{id}`
* `POST /prices`
* `PATCH /prices/{id}`
* `DELETE /prices/{id}`
* `POST /tasks/run`
* `POST /test/nats`

---

### WebSocket

URL подключения:

```
ws://localhost:8000/ws/prices
```

При подключении клиент будет получать JSON-сообщения о:

* создании валюты
* обновлении цены
* удалении валюты
* событиях из NATS

---

### Проверка NATS (publisher + subscriber)

1. Подключиться к WebSocket `/ws/prices`
2. Выполнить запрос:

```http
POST /test/nats
```

3. В WebSocket-клиенте отобразится событие в формате JSON

Это демонстрирует:

* публикацию события в NATS (publisher)
* получение события backend’ом (subscriber)
* рассылку события через WebSocket

---

## Фоновая задача

Фоновая задача:

* запускается автоматически при старте приложения
* периодически получает курсы валют с Binance
* обновляет данные в БД
* публикует события в NATS

Также доступен ручной запуск:

```http
POST /tasks/run
```

---

## Остановка проекта

```bash
docker-compose down
```

---

## Примечания

* База данных SQLite хранится в папке `data/`
* Данные сохраняются между перезапусками контейнеров
* NATS используется как внутренний брокер сообщений

---

