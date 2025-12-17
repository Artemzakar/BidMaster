import csv
import codecs
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Category, Item, SystemLog

router = APIRouter(prefix="/import", tags=["Data Import"])


# Функция для логирования ошибок в БД
def log_error(db: Session, source: str, message: str):
    log = SystemLog(level="ERROR", source=source, message=message)
    db.add(log)
    db.commit()


@router.post("/users")
async def import_users(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Загрузка пользователей из CSV"""
    count = 0
    try:
        # Читаем файл потоком
        csv_reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))

        for row in csv_reader:
            # Проверяем, нет ли такого юзера (для защиты от дублей)
            existing = db.query(User).filter(User.username == row['username']).first()
            if existing:
                continue

            user = User(
                username=row['username'],
                email=row['email'],
                password_hash=row['password_hash'],
                role=row['role'],
                balance=float(row['balance'])
            )
            db.add(user)
            count += 1

        db.commit()  # Фиксируем транзакцию
        return {"status": "success", "imported_count": count}

    except Exception as e:
        db.rollback()  # Откатываем изменения, если что-то пошло не так
        log_error(db, "import_users", str(e))
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/categories")
async def import_categories(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Загрузка категорий"""
    count = 0
    try:
        csv_reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
        for row in csv_reader:
            existing = db.query(Category).filter(Category.name == row['name']).first()
            if existing:
                continue

            cat = Category(
                name=row['name'],
                description=row['description']
            )
            db.add(cat)
            count += 1
        db.commit()
        return {"status": "success", "imported_count": count}
    except Exception as e:
        db.rollback()
        log_error(db, "import_categories", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/items")
async def import_items(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Загрузка предметов (зависит от пользователей!)"""
    count = 0
    try:
        csv_reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
        for row in csv_reader:
            item = Item(
                owner_id=int(row['owner_id']),
                title=row['title'],
                description=row['description'],
                year_created=int(row['year_created']),
                is_verified=True if row['is_verified'] == 'True' else False
            )
            db.add(item)
            count += 1
        db.commit()
        return {"status": "success", "imported_count": count}
    except Exception as e:
        db.rollback()
        log_error(db, "import_items", str(e))
        raise HTTPException(status_code=500, detail=str(e))