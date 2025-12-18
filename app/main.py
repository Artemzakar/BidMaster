from fastapi import FastAPI
from app.database import engine, Base
from app.routers import importer, auctions, analytics

# Создаем таблицы при старте (если их нет)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BidMaster API",
    description="Система онлайн-аукционов предметов искусства",
    version="1.0.0"
)

# Подключаем наши маршруты
app.include_router(importer.router)
app.include_router(auctions.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to BidMaster API! Go to /docs to use Swagger."}