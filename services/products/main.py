from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from typing import List

from database import get_db, engine
import models
import schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Products Microservice", version="1.0.0")

@app.get("/")
def root():
    return {"service": "products", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "products"}

@app.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected", "service": "products"}
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail={"status": "not_ready", "database": "disconnected", "error": str(e)}
        )

@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[schemas.Product])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

def product_to_xml(product):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <product>
                <id>{product.id}</id>
                <name>{product.name}</name>
                <price>{product.price}</price>
                <stock>{product.stock}</stock>
            </product>
        </soap:Body>
    </soap:Envelope>'''

def products_to_xml(products):
    products_xml = '\n'.join([
        f'''        <product>
            <id>{p.id}</id>
            <name>{p.name}</name>
            <price>{p.price}</price>
            <stock>{p.stock}</stock>
        </product>''' for p in products
    ])
    return f'''<?xml version="1.0" encoding="UTF-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <products>
    {products_xml}
            </products>
        </soap:Body>
    </soap:Envelope>'''

# SOAP/XML ENDPOINTS
@app.get("/soap/products")
def list_products_soap(db: Session = Depends(get_db)):
    """Listar todos los productos - retorna XML SOAP"""
    products = db.query(models.Product).all()
    return Response(content=products_to_xml(products), media_type="text/xml")

@app.get("/soap/product/{product_id}")
def get_product_soap(product_id: int, db: Session = Depends(get_db)):
    """Obtener producto - retorna XML SOAP"""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return Response(content=product_to_xml(product), media_type="text/xml")

@app.post("/soap/product")
def create_product_soap(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Crear producto - retorna XML SOAP"""
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return Response(content=product_to_xml(db_product), media_type="text/xml", status_code=201)