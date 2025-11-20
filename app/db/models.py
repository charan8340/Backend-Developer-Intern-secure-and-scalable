from sqlalchemy import Column, String, Boolean, TIMESTAMP, func, BigInteger, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from app.db.database import Base

# users
class User(Base):
    __tablename__ = "users"
    id = Column(CHAR(36), primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

class Role(Base):
    __tablename__ = "roles"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")

class UserRole(Base):
    __tablename__ = "user_roles"
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")

class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id = Column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(BigInteger, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="role_permissions")

class Product(Base):
    __tablename__ = "products"
    id = Column(CHAR(36), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String(2000))
    price = Column(DECIMAL(12,2), nullable=False, default=0.0)
    stock = Column(BigInteger, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(CHAR(36), primary_key=True)
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"))
    token_hash = Column(String(64), nullable=False)
    issued_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    expires_at = Column(TIMESTAMP)
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_tokens")
