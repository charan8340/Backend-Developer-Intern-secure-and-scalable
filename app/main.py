from fastapi import FastAPI
from app.db.database import Base, engine
from app.routes import auth, products, admin

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Minimal Ecom Backend (RBAC)")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(admin.router)
