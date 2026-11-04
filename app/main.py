# app/main.py

from fastapi import FastAPI

# Импортируем роутер.
from app.api.routers import main_router
from app.core.config import settings
import app.core.base as _models_registry  # noqa: F401

app = FastAPI(title=settings.app_title)

# Подключаем роутер.
app.include_router(main_router)
