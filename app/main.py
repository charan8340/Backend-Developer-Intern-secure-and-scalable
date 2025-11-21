from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.db.database import Base, engine
from app.routes import auth, products, admin
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Backend Intern Task")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve /frontend as /static
app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(admin.router)
