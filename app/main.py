from contextlib import asynccontextmanager

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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


