from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.crud import get_user_by_email, get_user, list_user_roles, get_permissions_for_user

auth_scheme = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme), db: Session = Depends(get_db)):
    # credential presence
    print("DEBUG get_current_user: credentials:", credentials)
    if not credentials:
        print("DEBUG get_current_user -> missing credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization")

    token = credentials.credentials
    print("DEBUG get_current_user -> raw token (start):", token[:40], "...")

    # decode token
    try:
        payload = decode_access_token(token)
        print("DEBUG get_current_user -> decoded payload:", payload)
    except Exception as e:
        print("DEBUG get_current_user -> decode failed:", repr(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        print("DEBUG get_current_user -> no sub in payload")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    print("DEBUG get_current_user -> token sub (user_id):", user_id)

    # get user from DB
    user = get_user(db, user_id)
    print("DEBUG get_current_user -> db user:", user)
    if not user:
        print("DEBUG get_current_user -> user not found in db")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        print("DEBUG get_current_user -> user not active")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active")

    # attach roles/permissions (and log them)
    roles = list_user_roles(db, user_id)
    permissions = get_permissions_for_user(db, user_id)
    print("DEBUG get_current_user -> roles:", roles)
    print("DEBUG get_current_user -> permissions:", permissions)

    # return plain dict consumed by require_admin
    user_obj = {"id": user.id, "username": user.username, "roles": roles, "permissions": permissions}
    print("DEBUG get_current_user -> returning user_obj:", user_obj)
    return user_obj

def require_admin(user = Depends(get_current_user)):
    print("DEBUG require_admin -> user passed:", user)
    if "admin" not in user.get("roles", []):
        print("DEBUG require_admin -> admin not found in roles:", user.get("roles"))
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    print("DEBUG require_admin -> user is admin")
    return user
