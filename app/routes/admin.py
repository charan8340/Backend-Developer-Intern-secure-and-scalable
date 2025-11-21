from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.crud import assign_role_to_user, create_role_if_not_exists, get_role_by_name
from app.schemas import RoleAssign
from app.deps import require_admin

router = APIRouter(prefix="/v1/admin", tags=["admin"])

@router.post("/roles/ensure")
def ensure_role(role_name: str, db: Session = Depends(get_db), _ = Depends(require_admin)):
    role = create_role_if_not_exists(db, role_name)
    return {"id": role.id, "name": role.name}

@router.post("/assign-role", status_code=201)
def assign_role(payload: RoleAssign, db: Session = Depends(get_db), _ = Depends(require_admin)):
    role = get_role_by_name(db, payload.role_name)
    if not role:
        role = create_role_if_not_exists(db, payload.role_name)
    ur = assign_role_to_user(db, payload.user_id, payload.role_name)
    return {"user_id": ur.user_id, "role_id": ur.role_id}
