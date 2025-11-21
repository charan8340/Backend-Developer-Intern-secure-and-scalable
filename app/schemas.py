from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterIn(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str

# products
class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    stock: int = 0

class ProductOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: float
    stock: int

    class Config:
        orm_mode = True

# role assign
class RoleAssign(BaseModel):
    user_id: str
    role_name: str

class RefreshIn(BaseModel):
    refresh_token: str
