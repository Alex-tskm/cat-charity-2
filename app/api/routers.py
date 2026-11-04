# app/api/routers.py
from fastapi import APIRouter

from app.api.endpoints import charity_project, donation, user

main_router = APIRouter()

main_router.include_router(charity_project.router)
main_router.include_router(donation.router)
main_router.include_router(user.router)