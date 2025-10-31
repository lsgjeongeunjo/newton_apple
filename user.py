from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# get_db_manager 대신 get_db를 임포트하도록 수정합니다.
from config.db import get_db

# User 모델과 스키마는 아직 정의하지 않았으므로, 임시로 주석 처리하거나 빈 상태로 둡니다.
# from models.user import User as UserModel
# from schemas.user import User as UserSchema

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/")
def get_all_users(db: Session = Depends(get_db)):
    """
    모든 사용자 목록을 반환합니다.
    (현재는 임시 응답만 반환합니다. 모델 구현 후 실제 DB 조회를 추가합니다.)
    """
    # 실제 DB 조회가 아닌 임시 응답입니다.
    # users = db.query(UserModel).all() 
    return {"message": "User Router is running! DB session retrieved successfully.", "data": []}

@router.get("/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """특정 ID의 사용자 정보를 반환합니다."""
    return {"message": f"Fetching user with ID: {user_id}"}

# TODO: 여기에 회원가입(POST), 수정(PUT), 삭제(DELETE) 라우트를 추가해야 합니다.
