from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import config, tasks  
from app.api.routes import router as api_router


def get_application():
    # enable CORS to tell our FastAPI to allow requests from external callers to these endpoints
    app = FastAPI(title="NextUp")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.add_event_handler("startup", tasks.start_app_handler(app))
    app.add_event_handler("shutdown", tasks.stop_app_handler(app))

    app.include_router(api_router, prefix="/api")

    return app

app = get_application()