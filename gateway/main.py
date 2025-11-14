from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import httpx
import os

# SCHEMAS 
class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop",
                "price": 1200.50,
                "stock": 5
            }
        }

class CustomerCreate(BaseModel):
    name: str
    email: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Juan Pérez",
                "email": "juan@example.com"
            }
        }

class OrderCreate(BaseModel):
    customer_id: int
    total: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": 1,
                "total": 1200.50
            }
        }

# APP 

app = FastAPI(
    title="E-Commerce API Gateway",
    description="Gateway unificado para todos los microservicios",
    version="1.0.0"
)

PRODUCTS_SERVICE_URL = os.getenv("PRODUCTS_SERVICE_URL", "http://products-service:8000")
CUSTOMERS_SERVICE_URL = os.getenv("CUSTOMERS_SERVICE_URL", "http://customers-service:8000")
ORDERS_SERVICE_URL = os.getenv("ORDERS_SERVICE_URL", "http://orders-service:8000")

# HEALTH CHECKS 

@app.get("/", tags=["Gateway"])
async def root():
    return {
        "message": "E-Commerce API Gateway",
        "version": "1.0.0",
        "services": {
            "products": PRODUCTS_SERVICE_URL,
            "customers": CUSTOMERS_SERVICE_URL,
            "orders": ORDERS_SERVICE_URL
        }
    }

@app.get("/health", tags=["Gateway"])
async def health():
    return {"status": "healthy", "gateway": "ok"}

# PRODUCTS SERVICE 

@app.post("/products/", tags=["Products"])
async def create_product(product: ProductCreate):
    """Crear un nuevo producto"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{PRODUCTS_SERVICE_URL}/products/", json=product.dict())
        return JSONResponse(content=response.json(), status_code=response.status_code)

@app.get("/products/", tags=["Products"])
async def list_products():
    """Listar todos los productos"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PRODUCTS_SERVICE_URL}/products/")
        return JSONResponse(content=response.json(), status_code=response.status_code)

@app.get("/products/{product_id}", tags=["Products"])
async def get_product(product_id: int):
    """Obtener un producto por ID"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PRODUCTS_SERVICE_URL}/products/{product_id}")
        return JSONResponse(content=response.json(), status_code=response.status_code)

# SOAP/XML ENDPOINTS
@app.post("/products/soap/create", tags=["SOAP"])
async def create_product_soap(product: ProductCreate):
    """Crear producto - retorna XML"""
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{PRODUCTS_SERVICE_URL}/soap/product", json=product.dict())
        return Response(content=r.content, status_code=r.status_code, media_type='text/xml')

@app.get("/products/soap/list", tags=["SOAP"])
async def list_products_soap():
    """Listar todos los productos - retorna XML SOAP"""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{PRODUCTS_SERVICE_URL}/soap/products")
        return Response(content=r.content, status_code=r.status_code, media_type='text/xml')

@app.get("/products/soap/{product_id}", tags=["SOAP"])
async def get_product_soap(product_id: int):
    """Obtener producto - retorna XML"""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{PRODUCTS_SERVICE_URL}/soap/product/{product_id}")
        return Response(content=r.content, status_code=r.status_code, media_type='text/xml')

# CUSTOMERS SERVICE 

@app.post("/customers/", tags=["Customers"])
async def create_customer(customer: CustomerCreate):
    """Crear un nuevo cliente"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{CUSTOMERS_SERVICE_URL}/customers/", json=customer.dict())
        return JSONResponse(content=response.json(), status_code=response.status_code)

@app.get("/customers/", tags=["Customers"])
async def list_customers():
    """Listar todos los clientes"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CUSTOMERS_SERVICE_URL}/customers/")
        return JSONResponse(content=response.json(), status_code=response.status_code)

@app.get("/customers/{customer_id}", tags=["Customers"])
async def get_customer(customer_id: int):
    """Obtener un cliente por ID"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CUSTOMERS_SERVICE_URL}/customers/{customer_id}")
        return JSONResponse(content=response.json(), status_code=response.status_code)

# ORDERS SERVICE 

@app.post("/orders/", tags=["Orders"])
async def create_order(request: Request):
    """Crear una nueva orden"""
    async with httpx.AsyncClient() as client:
        body = await request.json()
        response = await client.post(f"{ORDERS_SERVICE_URL}/orders/", json=body)
        return JSONResponse(content=response.json(), status_code=response.status_code)

@app.get("/orders/", tags=["Orders"])
async def list_orders():
    """Listar todas las órdenes"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ORDERS_SERVICE_URL}/orders/")
        return JSONResponse(content=response.json(), status_code=response.status_code)

@app.get("/orders/{order_id}", tags=["Orders"])
async def get_order(order_id: int):
    """Obtener una orden por ID"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ORDERS_SERVICE_URL}/orders/{order_id}")
        return JSONResponse(content=response.json(), status_code=response.status_code)