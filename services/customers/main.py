from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from typing import List

from database import get_db, engine
import models
import schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customers Microservice", version="1.0.0")

@app.get("/")
def root():
    return {"service": "customers", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "customers"}

@app.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected", "service": "customers"}
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail={"status": "not_ready", "database": "disconnected", "error": str(e)}
        )

@app.post("/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):

    db_customer = db.query(models.Customer).filter(models.Customer.email == customer.email).first()
    if db_customer:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    new_customer = models.Customer(**customer.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@app.get("/customers/", response_model=List[schemas.Customer])
def list_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()

@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return customer

@app.get("/customers/{customer_id}/exists")
def check_customer_exists(customer_id: int, db: Session = Depends(get_db)):
    """Endpoint interno para verificar si un cliente existe"""
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    return {"exists": customer is not None, "customer_id": customer_id}