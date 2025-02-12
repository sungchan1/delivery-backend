from fastapi import FastAPI

from app.apis.category.v1.home_category_router import router as home_category_router
from app.entities.collections import set_indexes

app = FastAPI()
app.include_router(home_category_router)


@app.on_event("startup")
async def on_startup() -> None:
    await set_indexes()
