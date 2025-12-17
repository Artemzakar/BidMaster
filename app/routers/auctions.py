from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Auction, Bid, Item, User
from pydantic import BaseModel

router = APIRouter(prefix="/auctions", tags=["Auctions"])


# Pydantic-схема для приема данных от пользователя
class AuctionCreate(BaseModel):
    item_id: int
    start_price: float
    duration_minutes: int = 60  # Длительность по умолчанию


class BidCreate(BaseModel):
    user_id: int
    amount: float


@router.post("/")
def create_auction(auction: AuctionCreate, db: Session = Depends(get_db)):
    """Создать новый аукцион для предмета"""
    # 1. Проверяем, существует ли предмет
    item = db.query(Item).filter(Item.item_id == auction.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # 2. Проверяем, не на торгах ли он уже (у нас стоит UNIQUE constraint, но проверим красиво)
    existing = db.query(Auction).filter(Auction.item_id == auction.item_id, Auction.status != 'cancelled').first()
    if existing:
        raise HTTPException(status_code=400, detail="Item is already on auction")

    # 3. Создаем аукцион
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=auction.duration_minutes)

    new_auction = Auction(
        item_id=auction.item_id,
        start_time=start_time,
        end_time=end_time,
        start_price=auction.start_price,
        current_price=auction.start_price,  # Начальная цена = текущая
        status='active'
    )
    db.add(new_auction)
    db.commit()
    db.refresh(new_auction)
    return new_auction


@router.post("/{auction_id}/bid")
def place_bid(auction_id: int, bid: BidCreate, db: Session = Depends(get_db)):
    """Сделать ставку"""
    # 1. Находим аукцион
    auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    if auction.status != 'active':
        raise HTTPException(status_code=400, detail="Auction is not active")

    if datetime.now() > auction.end_time:
        auction.status = 'finished'
        db.commit()
        raise HTTPException(status_code=400, detail="Auction finished")

    # 2. Проверка: Ставка должна быть выше текущей
    if bid.amount <= auction.current_price:
        raise HTTPException(status_code=400, detail=f"Bid must be higher than {auction.current_price}")

    # 3. Проверка: У пользователя должно быть достаточно денег
    user = db.query(User).filter(User.user_id == bid.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.balance < bid.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # 4. СОЗДАЕМ СТАВКУ (Триггеры сами обновят цену и продлят время!)
    new_bid = Bid(
        auction_id=auction_id,
        user_id=bid.user_id,
        amount=bid.amount,
        bid_time=datetime.now()
    )
    db.add(new_bid)
    db.commit()

    return {"status": "success", "new_price": bid.amount}