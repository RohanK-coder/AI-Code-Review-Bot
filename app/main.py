from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'environment': settings.app_env}
