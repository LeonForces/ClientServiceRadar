from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from sqladmin import Admin

from prometheus_fastapi_instrumentator import Instrumentator

from redis import asyncio as aioredis

from app.core.db import delete_tables, create_tables, engine
from app.api.endpoints.users import router as user_router
from app.api.endpoints.reviews import router as review_router
from app.api.endpoints.prometheus import router as prometheus_router
from app.core.config import settings
from app.api.dependencies.admin.auth import authentication_backend
from app.api.dependencies.admin.views import UserAdmin, ReviewAdmin
from app.core.logging import setup

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
from datetime import datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(settings.redis_url, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")

    yield

app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(review_router)
app.include_router(prometheus_router)


origins = [
    "http://localhost:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin", "Authorization"],
)

# Подключаем эндпоинт для сбора метрик
instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"]
)

instrumentator.instrument(app).expose(app)


admin = Admin(app, engine, authentication_backend=authentication_backend)


BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# URL страницы с отзывами
URL = 'https://www.banki.ru/services/responses/bank/promsvyazbank/?type=all'

# Список для хранения ID пользователей
user_ids = set()

# Переменная для хранения времени последнего отзыва
last_review_time = None

# Инициализируем приложение Telegram Bot
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_ids.add(user_id)
    print(f"Пользователь добавлен: {user_id}")
    await update.message.reply_text("Вы подписаны на уведомления о новых отзывах.")

# Отправка уведомлений всем пользователям
async def send_notifications(context: CallbackContext):
    if user_ids:
        for user_id in user_ids:
            try:
                await context.bot.send_message(chat_id=user_id, text="Есть новый отзыв!")
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
    else:
        print("Нет подписчиков для отправки уведомлений.")

# Проверяет наличие новых отзывов
def check_for_new_reviews():
    global last_review_time

    # Делаем запрос к URL
    response = requests.get(URL)

    # Парсим HTML с помощью BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим последний элемент с отзывом (предполагается, что последний отзыв находится последним в списке)
    review_time_element = soup.find('span', class_='l0caf3d5f')  # предположительный селектор
    if review_time_element:
        review_time_str = review_time_element.text.strip()

        try:
            # Преобразуем строку в объект datetime
            current_review_time = datetime.strptime(review_time_str, '%d.%m.%Y %H:%M')

            if last_review_time is None or current_review_time > last_review_time:
                last_review_time = current_review_time
                print(f"{current_review_time.strftime('%Y-%m-%d %H:%M:%S')}: Есть новый отзыв!")
                application.job_queue.run_once(send_notifications, 0)
            else:
                print(f"{current_review_time.strftime('%Y-%m-%d %H:%M:%S')}: Нет новых отзывов. Последний отзыв был {last_review_time}")
        except ValueError as e:
            print(f"Ошибка при преобразовании строки даты: {e}")
    else:
        print("Не удалось найти элемент с последним отзывом.")

# Инициализация времени последнего отзыва при первом запуске
def initialize_last_review_time():
    global last_review_time

    # Делаем GET-запрос к URL
    response = requests.get(URL)

    # Парсим HTML с помощью BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим последний элемент с отзывом (предполагается, что последний отзыв находится последним в списке)
    review_time_element = soup.find('span', class_='l0caf3d5f')  # предположительный селектор
    if review_time_element:
        review_time_str = review_time_element.text.strip()

        try:
            # Преобразуем строку в объект datetime
            last_review_time = datetime.strptime(review_time_str, '%d.%m.%Y %H:%M')
            print(f'Последнее время отзыва установлено: {last_review_time.strftime("%Y-%m-%d %H:%M:%S")}')
        except ValueError as e:
            print(f'Ошибка при преобразовании строки даты: {e}')
            return None
    else:
        print("Не удалось найти элемент с последним отзывом.")
        return None

# Маршрут для обработки входящих запросов от Telegram
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot=application.bot)
    application.dispatcher.process_update(update)
    return JSONResponse({"ok": True})

# Добавляем обработчик команды /start
application.add_handler(CommandHandler("start", start))

# Инициализируем последнее время отзыва
initialize_last_review_time()

# Запускаем проверку каждые 60 секунд
schedule.every(60).seconds.do(check_for_new_reviews)

# Запускаем планировщик задач в отдельном потоке
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

