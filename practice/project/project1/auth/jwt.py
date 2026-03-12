# JWT -> 형식
# 누구나 열어볼 수 있기때문에 비번처럼 중요정보는 담지 않기
# access_token -> 역할
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, status

from config import settings



def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),    # subject: 사용자 식별 정보
        "exp": datetime.now(timezone.utc) + timedelta(hours=24) # 24시간 후 자동 만료
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def verify_access_token(access_token: str) -> dict:
    try:
        payload = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid expired")
    return payload

http_bearer = HTTPBearer()

def verify_user(
    auth_header: HTTPAuthorizationCredentials = Depends(http_bearer) 
) -> int:
    access_token = auth_header.credentials
    payload = verify_access_token(access_token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    return user_id