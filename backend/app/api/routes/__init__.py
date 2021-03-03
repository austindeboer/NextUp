from fastapi import APIRouter

from app.api.routes.todos import router as todos_router
from app.api.routes.users import router as users_router
from app.api.routes.profiles import router as profiles_router  

router = APIRouter()

router.include_router(todos_router, prefix="/todos", tags=["todos"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(profiles_router, prefix="/profiles", tags=["profiles"])  