from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics & Reports"])

@router.get("/active-lots")
def get_active_lots_report(db: Session = Depends(get_db)):
    """Отчет: Активные лоты (из VIEW v_active_lots_details)"""
    # Используем чистый SQL для обращения к VIEW
    result = db.execute(text("SELECT * FROM v_active_lots_details"))
    # Превращаем результат в список словарей
    return [dict(row._mapping) for row in result]

@router.get("/category-sales")
def get_category_sales_report(db: Session = Depends(get_db)):
    """Отчет: Продажи по категориям (из VIEW v_category_sales)"""
    result = db.execute(text("SELECT * FROM v_category_sales"))
    return [dict(row._mapping) for row in result]

@router.get("/top-bidders")
def get_top_bidders_report(db: Session = Depends(get_db)):
    """Отчет: Топ пользователей (из VIEW v_top_bidders)"""
    result = db.execute(text("SELECT * FROM v_top_bidders"))
    return [dict(row._mapping) for row in result]