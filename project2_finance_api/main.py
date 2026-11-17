from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

import models
import schemas
from database import engine, get_db

# Create the SQLite database tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Finance & Expense Tracker API")

@app.post("/transactions/", response_model=schemas.TransactionResponse, status_code=201)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    new_tx = models.Transaction(**transaction.model_dump())
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx

@app.get("/transactions/", response_model=List[schemas.TransactionResponse])
def get_transactions(
    transaction_type: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Transaction)
    if transaction_type:
        query = query.filter(models.Transaction.transaction_type == transaction_type)
    if category:
        query = query.filter(models.Transaction.category.ilike(f"%{category}%"))
    return query.all()

@app.get("/summary/")
def get_summary(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()
    total_income = sum(tx.amount for tx in transactions if tx.transaction_type == "income")
    total_expense = sum(tx.amount for tx in transactions if tx.transaction_type == "expense")
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": total_income - total_expense,
        "transaction_count": len(transactions)
    }

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(tx)
    db.commit()
    return {"message": f"Transaction {transaction_id} deleted successfully"}

