from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

# auth
class RegisterIn(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

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
