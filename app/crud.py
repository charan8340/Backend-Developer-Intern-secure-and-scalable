from sqlalchemy.orm import Session
from app.db import models
import uuid
from app.core.security import hash_password, hash_refresh_token

# users
def create_user(db: Session, username: str, email: str, password: str):
    uid = str(uuid.uuid4())
    user = models.User(id=uid, username=username, email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

# roles/permissions
def get_role_by_name(db: Session, name: str):
    return db.query(models.Role).filter(models.Role.name == name).first()

def create_role_if_not_exists(db: Session, name: str):
    role = get_role_by_name(db, name)
    if role:
        return role
    role = models.Role(name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

def assign_role_to_user(db: Session, user_id: str, role_name: str):
    role = get_role_by_name(db, role_name)
    if not role:
        role = create_role_if_not_exists(db, role_name)
    # check existing
    exists = db.query(models.UserRole).filter(models.UserRole.user_id == user_id, models.UserRole.role_id == role.id).first()
    if exists:
        return exists
    ur = models.UserRole(user_id=user_id, role_id=role.id)
    db.add(ur)
    db.commit()
    return ur

def list_user_roles(db: Session, user_id: str):
    rows = db.query(models.Role).join(models.UserRole, models.UserRole.role_id == models.Role.id).filter(models.UserRole.user_id == user_id).all()
    return [r.name for r in rows]

def get_permissions_for_user(db: Session, user_id: str):
    q = db.query(models.Permission.name).join(models.RolePermission, models.RolePermission.permission_id == models.Permission.id) \
        .join(models.UserRole, models.UserRole.role_id == models.RolePermission.role_id) \
        .filter(models.UserRole.user_id == user_id).distinct()
    return [r[0] for r in q.all()]

# products
def create_product(db: Session, title, description, price, stock):
    pid = str(uuid.uuid4())
    p = models.Product(id=pid, title=title, description=description, price=price, stock=stock)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def list_products(db: Session, skip=0, limit=100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def get_product(db: Session, product_id: str):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def update_product(db: Session, product_id: str, **fields):
    p = get_product(db, product_id)
    if not p:
        return None
    for k,v in fields.items():
        if hasattr(p, k) and v is not None:
            setattr(p, k, v)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def delete_product(db: Session, product_id: str):
    p = get_product(db, product_id)
    if not p:
        return False
    db.delete(p)
    db.commit()
    return True

# refresh tokens
def store_refresh_token(db: Session, user_id: str, raw_token: str, expires_at):
    import uuid
    hashed = hash_refresh_token(raw_token)
    rid = str(uuid.uuid4())
    rt = models.RefreshToken(id=rid, user_id=user_id, token_hash=hashed, expires_at=expires_at)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt

def find_refresh_token_by_hash(db: Session, raw_token: str):
    hashed = hash_refresh_token(raw_token)
    return db.query(models.RefreshToken).filter(models.RefreshToken.token_hash == hashed, models.RefreshToken.revoked == False, models.RefreshToken.expires_at > func.current_timestamp()).first()

def revoke_refresh_token(db: Session, token_id: str):
    rt = db.query(models.RefreshToken).filter(models.RefreshToken.id == token_id).first()
    if not rt:
        return False
    rt.revoked = True
    db.add(rt)
    db.commit()
    return True
