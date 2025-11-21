from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import ProductCreate, ProductOut
from app.crud import create_product, list_products, get_product, update_product, delete_product

router = APIRouter(prefix="/v1/products", tags=["products"])

@router.get("/", response_model=list[ProductOut])
def products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rows = list_products(db, skip=skip, limit=limit)
    return rows

@router.get("/{product_id}", response_model=ProductOut)
def product_detail(product_id: str, db: Session = Depends(get_db)):
    p = get_product(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


@router.post("/", response_model=ProductOut, status_code=201)
def create(p: ProductCreate, db: Session = Depends(get_db)):  
    print("add new product", p)
    new = create_product(db, p.title, p.description, p.price, p.stock)
    return new


@router.put("/{product_id}", response_model=ProductOut)
def replace(product_id: str, p: ProductCreate, db: Session = Depends(get_db)):
    updated = update_product(
        db, product_id,
        title=p.title,
        description=p.description,
        price=p.price,
        stock=p.stock
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated


@router.patch("/{product_id}", response_model=ProductOut)
def patch(product_id: str, p: ProductCreate, db: Session = Depends(get_db)):
    updated = update_product(
        db, product_id,
        title=p.title,
        description=p.description,
        price=p.price,
        stock=p.stock
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated


@router.delete("/{product_id}", status_code=204)
def remove(product_id: str, db: Session = Depends(get_db)):
    ok = delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return
