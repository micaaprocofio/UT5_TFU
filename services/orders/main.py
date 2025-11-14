from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from typing import List
import os
import httpx
from database import get_db, engine
import models
import schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orders Microservice", version="1.0.0")

CUSTOMERS_SERVICE_URL = os.getenv("CUSTOMERS_SERVICE_URL", "http://customers-service:8000")

@app.get("/")
def root():
    return {"service": "orders", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "orders"}

@app.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected", "service": "orders"}
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail={"status": "not_ready", "database": "disconnected", "error": str(e)}
        )

async def verify_customer_exists(customer_id: int) -> bool:
    """Verifica si el cliente existe llamando al microservicio de customers"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CUSTOMERS_SERVICE_URL}/customers/{customer_id}/exists", 
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json().get("exists", False)
            return False
    except:
        return True

@app.post("/orders/", response_model=schemas.Order)
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):

    customer_exists = await verify_customer_exists(order.customer_id)
    if not customer_exists:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    new_order = models.Order(**order.dict())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@app.get("/orders/", response_model=List[schemas.Order])
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

@app.get("/orders/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order

@app.get("/orders/customer/{customer_id}", response_model=List[schemas.Order])
def get_orders_by_customer(customer_id: int, db: Session = Depends(get_db)):
    """Obtiene todas las órdenes de un cliente específico"""
    return db.query(models.Order).filter(models.Order.customer_id == customer_id).all()