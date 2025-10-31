from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

# 내부 모듈 임포트
from config.db import db_manager
from utils.auth import verify_token 

# 라우터 인스턴스 생성
router = APIRouter(
    prefix="/disinfestation", 
    tags=["Disinfestation"]
)

# -------------------------------------------------------------
# Pydantic 모델 정의
# -------------------------------------------------------------

# 방제 기록 등록 요청 데이터 모델 (pest_name을 받아서 ID를 조회할 것임)
class DisinfestationCreate(BaseModel):
    pest_name: str # 🌟 클라이언트에서 병해충 이름을 받습니다. (예: "탄저병")
    disf_at: datetime # 방제 일시 (YYYY-MM-DD HH:MM:SS 형식)
    chemical_name: str # 사용한 약품 이름
    dosage: str # 사용량
    disf_memo: str # 특이사항/메모

# 방제 기록 응답 데이터 모델 (조회용)
class DisinfestationRecord(BaseModel):
    disf_idx: int
    user_id: str
    pest_idx: int
    disf_at: datetime
    chemical_name: str
    dosage: str
    disf_memo: str
    created_at: datetime

# -------------------------------------------------------------
# API 구현
# -------------------------------------------------------------

@router.post("/", response_model=Dict[str, Any])
async def create_disinfestation_record(
    record: DisinfestationCreate, 
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """
    방제 기록 등록 API (POST /disinfestation/)
    - 인증된 사용자만 등록 가능
    - pest_name을 pest_idx로 변환하여 저장합니다.
    """
    try:
        user_id = current_user.get('sub') 

        # 1. tb_pest 테이블에서 pest_name을 이용하여 pest_idx를 조회합니다.
        pest_query = "SELECT pest_idx FROM tb_pest WHERE pest_name = %s"
        pest_result = db_manager.execute_query(pest_query, (record.pest_name,), fetch_one=True)
        
        if not pest_result:
            # pest_idx를 찾지 못하면 404 오류를 반환하여, 사용자에게 병해충 이름이 잘못되었음을 알립니다.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"병해충 정보 '{record.pest_name}'을(를) 데이터베이스에서 찾을 수 없습니다. 먼저 tb_pest에 등록하세요."
            )
        
        # 2. 조회된 pest_idx(정수)를 추출합니다.
        pest_idx = pest_result['pest_idx']

        # 3. 방제 기록을 tb_disinfestation에 삽입합니다.
        insert_query = """
            INSERT INTO tb_disinfestation 
            (user_id, pest_idx, disf_at, chemical_name, dosage, disf_memo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            user_id,
            pest_idx, # 🌟 정수형 ID가 사용됨
            record.disf_at,
            record.chemical_name,
            record.dosage,
            record.disf_memo
        )
        
        result = db_manager.execute_query(insert_query, params)
        
        return {
            "message": "방제 기록이 성공적으로 등록되었습니다.",
            "disf_idx": result.get('last_row_id')
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"방제 기록 등록 중 서버 오류 발생: {e}")
        # DB 연결 오류 등을 포함한 500 오류 처리
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="방제 기록 등록 중 서버 오류가 발생했습니다. 로그를 확인하세요."
        )


@router.get("/list", response_model=List[DisinfestationRecord])
async def get_disinfestation_list(
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """
    사용자 방제 기록 목록 조회 API (GET /disinfestation/list)
    """
    try:
        user_id = current_user.get('sub')
        
        select_query = """
            SELECT 
                disf_idx, user_id, pest_idx, disf_at, chemical_name, dosage, disf_memo, created_at 
            FROM tb_disinfestation 
            WHERE user_id = %s
            ORDER BY disf_at DESC
        """
        
        records = db_manager.execute_query(select_query, (user_id,))
        return records

    except Exception as e:
        print(f"방제 기록 조회 중 서버 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="방제 기록 조회 중 오류가 발생했습니다."
        )
