from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.crud import create_user, get_user_by_email, store_refresh_token, revoke_refresh_token
from app.schemas import RegisterIn, LoginIn, TokenOut
from app.core.security import verify_password, create_access_token, generate_refresh_token_raw, hash_refresh_token
from datetime import datetime, timedelta
from app.core.config import settings

router = APIRouter(prefix="/v1/auth", tags=["auth"])

@router.post("/register", status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    exists = get_user_by_email(db, payload.email)
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, payload.username, payload.email, payload.password)
    # assign default role 'user' — create endpoint for admin to change roles
    # create role if not exists and assign
    from app.crud import assign_role_to_user
    assign_role_to_user(db, user.id, "user")
    return {"id": user.id, "username": user.username, "email": user.email}

@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # build roles list
    from app.crud import list_user_roles
    roles = list_user_roles(db, user.id)
    token_payload = {"sub": user.id, "roles": roles}
    access_token = create_access_token(token_payload)
    # create refresh token and store its hash
    raw_refresh = generate_refresh_token_raw()
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    store_refresh_token(db, user.id, raw_refresh, expires_at)
    return {"access_token": access_token, "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, "token_type": "bearer", "refresh_token": raw_refresh}
    # Note: in production you'd set refresh token as HttpOnly cookie. For demo we return it in body.

@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    # hash incoming and revoke matching token
    from app.core.security import hash_refresh_token
    hashed = hash_refresh_token(refresh_token)
    rt = db.query(__import__("app").db.models.RefreshToken).filter_by(token_hash=hashed).first()
    if not rt:
        raise HTTPException(status_code=400, detail="Invalid token")
    rt.revoked = True
    db.add(rt)
    db.commit()
    return {"msg": "logged out"}
