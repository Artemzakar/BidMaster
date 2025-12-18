import csv
import io
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    User, Category, Item, ItemCategory, Auction, Bid,
    ExpertReview, AuditLog, SystemLog,
    AutoBid, EscrowAccount
)

router = APIRouter(prefix="/import", tags=["Import"])

# Маппинг: имя файла -> (Модель БД, Приоритет загрузки)
# Приоритет важен, чтобы не нарушить Foreign Key (сначала создаем User, потом Bid)
CSV_MAPPING = {
    "users.csv": (User, 1),
    "categories.csv": (Category, 2),
    "items.csv": (Item, 3),
    "item_categories.csv": (ItemCategory, 4),
    "auctions.csv": (Auction, 5),
    "bids.csv": (Bid, 6),
    "auto_bids.csv": (AutoBid, 7),
    "escrow_accounts.csv": (EscrowAccount, 8),
    "expert_reviews.csv": (ExpertReview, 9),
    "audit_log.csv": (AuditLog, 10)
}


@router.post("/batch-import")
async def batch_import_data(
        files: List[UploadFile],
        db: Session = Depends(get_db)
):
    # Генерируем ID пакета, чтобы в логах отследить конкретную загрузку
    batch_id = str(uuid.uuid4())

    log_start = SystemLog(
        level="INFO",
        source="BATCH_IMPORT",
        message=f"Batch {batch_id}: Started uploading {len(files)} files."
    )
    db.add(log_start)
    db.commit()

    # Сортируем файлы по приоритету из CSV_MAPPING
    sorted_files = sorted(
        files,
        key=lambda f: CSV_MAPPING.get(f.filename, (None, 99))[1]
    )

    report = {}

    for file in sorted_files:
        if file.filename not in CSV_MAPPING:
            report[file.filename] = "Skipped (Unknown file)"
            continue

        model, _ = CSV_MAPPING[file.filename]

        try:
            content = await file.read()
            try:
                decoded_content = content.decode("utf-8")
            except UnicodeDecodeError:
                decoded_content = content.decode("cp1251")

            csv_file = io.StringIO(decoded_content)

            # Пытаемся автоматически определить разделитель (запятая или точка с запятой)
            try:
                dialect = csv.Sniffer().sniff(decoded_content[:1024])
                csv_reader = csv.DictReader(csv_file, dialect=dialect)
            except:
                csv_file.seek(0)
                csv_reader = csv.DictReader(csv_file)

            rows = []
            for row in csv_reader:
                clean_row = {}
                for k, v in row.items():
                    if not k: continue
                    key = k.strip()
                    value = v.strip() if v else None

                    # Ручная конвертация булевых значений из CSV
                    if key == "is_verified" and value:
                        clean_row[key] = (value == "True")
                    else:
                        clean_row[key] = value

                rows.append(clean_row)

            if rows:
                # Используем bulk_insert для скорости (вставка пачкой)
                db.bulk_insert_mappings(model, rows)
                db.commit()

                msg = f"Success: {len(rows)} records loaded."
                db.add(SystemLog(
                    level="INFO",
                    source="BATCH_IMPORT",
                    message=f"Batch {batch_id}: File {file.filename} - {msg}"
                ))
                report[file.filename] = msg
            else:
                report[file.filename] = "Empty file warning"

        except Exception as e:
            # Если ошибка в конкретном файле — откатываем только его
            db.rollback()
            error_msg = f"Error: {str(e)}"
            report[file.filename] = error_msg
            db.add(SystemLog(
                level="ERROR",
                source="BATCH_IMPORT",
                message=f"Batch {batch_id}: File {file.filename} failed. {error_msg}"
            ))
            db.commit()

    return {"batch_id": batch_id, "report": report}