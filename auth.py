from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# ----------------------------------------------------------------------
# 1. JWT 및 해싱 설정
# ----------------------------------------------------------------------
# 환경 변수가 로드되지 않으면 기본값이 사용됩니다. (실제 환경에서는 반드시 변경)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-default-secret-key") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

# 비밀번호 해시를 위한 컨텍스트 설정 (Bcrypt 사용)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 토큰 추출을 위한 OAuth2 설정. (tokenUrl은 로그인 라우트 경로입니다)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") 

# ----------------------------------------------------------------------
# 2. 유틸리티 함수
# ----------------------------------------------------------------------

def hash_password(password: str) -> str:
    """주어진 문자열 비밀번호를 해시하여 반환합니다."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해시된 비밀번호를 비교하여 일치 여부를 반환합니다."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """주어진 데이터를 포함하는 JWT 액세스 토큰을 생성합니다."""
    to_encode = data.copy()
    
    # 토큰 만료 시간 설정
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # JWT 토큰 생성
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """JWT 토큰을 디코딩하고 토큰 데이터를 반환합니다."""
    try:
        # SECRET_KEY를 사용하여 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # 토큰이 유효하지 않거나 만료된 경우 None 반환
        return None 

# ----------------------------------------------------------------------
# 3. FastAPI Dependency (verify_token)
# ----------------------------------------------------------------------

def verify_token(token: str = Depends(oauth2_scheme)):
    """
    HTTP 헤더에서 토큰을 추출하고 유효성을 검증하는 FastAPI 의존성 함수.
    유효한 경우 토큰 Payload(사용자 정보)를 반환하고, 아니면 401 에러를 발생시킵니다.
    """
    payload = decode_access_token(token)
    
    # 디코딩 실패 시 (유효하지 않은 토큰)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰 Payload 반환 (주로 사용자 ID가 포함됨)
    return payload
