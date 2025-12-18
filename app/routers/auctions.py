from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models import Auction, Bid, Item, User, EscrowAccount
from app.schemas import AuctionResponse
from pydantic import BaseModel

router = APIRouter(prefix="/auctions")

# Схемы для валидации входных данных
class AuctionCreate(BaseModel):
    item_id: int
    start_price: float
    duration_minutes: int = 60

class BidCreate(BaseModel):
    user_id: int
    amount: float

@router.get("/", response_model=List[AuctionResponse], tags=["Auctions"])
def get_all_auctions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Auction).offset(skip).limit(limit).all()

@router.get("/{auction_id}", response_model=AuctionResponse, tags=["Auctions"])
def get_auction(auction_id: int, db: Session = Depends(get_db)):
    auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    return auction

@router.post("/", response_model=AuctionResponse, tags=["Auctions"])
def create_auction(auction: AuctionCreate, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.item_id == auction.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Нельзя выставить один предмет на два аукциона одновременно
    existing = db.query(Auction).filter(Auction.item_id == auction.item_id, Auction.status != 'cancelled').first()
    if existing:
        raise HTTPException(status_code=400, detail="Item is already on auction")

    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=auction.duration_minutes)

    new_auction = Auction(
        item_id=auction.item_id,
        start_time=start_time,
        end_time=end_time,
        start_price=auction.start_price,
        current_price=auction.start_price,
        status='active'
    )
    db.add(new_auction)
    db.commit()
    db.refresh(new_auction)
    return new_auction

@router.delete("/{auction_id}", tags=["Auctions"])
def delete_auction(auction_id: int, db: Session = Depends(get_db)):
    auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    db.delete(auction)
    db.commit()
    return {"detail": "Auction deleted"}

@router.post("/{auction_id}/bid", tags=["Auctions"])
def place_bid(auction_id: int, bid: BidCreate, db: Session = Depends(get_db)):
    """Сделать ставку (с проверками баланса и статуса)"""
    auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    # Валидация: аукцион должен быть активен и время не истекло
    if auction.status != 'active':
        raise HTTPException(status_code=400, detail="Auction is not active")

    if datetime.now() > auction.end_time:
        auction.status = 'finished'
        db.commit()
        raise HTTPException(status_code=400, detail="Auction finished")

    if bid.amount <= auction.current_price:
        raise HTTPException(status_code=400, detail=f"Bid must be higher than {auction.current_price}")

    user = db.query(User).filter(User.user_id == bid.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем платежеспособность
    if user.balance < bid.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    new_bid = Bid(
        auction_id=auction_id,
        user_id=bid.user_id,
        amount=bid.amount,
        bid_time=datetime.now()
    )
    db.add(new_bid)
    db.commit()

    return {"status": "success", "new_price": bid.amount}

@router.post("/{auction_id}/close", tags=["Transactions Demo"])
def close_auction_transaction(auction_id: int, db: Session = Depends(get_db)):
    """
    Транзакционное закрытие аукциона.
    Создает запись в Escrow (депонирование) для победителя.
    """
    auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    if auction.status == 'finished':
        raise HTTPException(status_code=400, detail="Already finished")

    # Ищем последнюю (максимальную) ставку
    winner_bid = db.query(Bid).filter(Bid.auction_id == auction_id) \
        .order_by(Bid.amount.desc()).first()

    try:
        # Обновляем статус и создаем счет в рамках одной транзакции
        auction.status = 'finished'
        auction.end_time = datetime.now()

        if winner_bid:
            escrow = EscrowAccount(
                auction_id=auction_id,
                buyer_id=winner_bid.user_id,
                amount=winner_bid.amount,
                status='held'
            )
            db.add(escrow)

        db.commit() # Фиксируем изменения, если не было ошибок

        return {"message": "Auction closed and funds escrowed", "winner_id": winner_bid.user_id if winner_bid else None}

    except Exception as e:
        db.rollback() # Откат при любой ошибке
        raise HTTPException(status_code=500, detail=str(e))