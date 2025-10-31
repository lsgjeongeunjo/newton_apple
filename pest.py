from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

# 내부 모듈 임포트
from config.db import db_manager
from utils.auth import verify_token 

# 라우터 인스턴스 생성
router = APIRouter(
    prefix="/pest", # 모든 라우트 앞에 /pest가 붙습니다.
    tags=["Pest"] # Swagger 문서 그룹 이름
)

# -------------------------------------------------------------
# Pydantic 모델 정의
# -------------------------------------------------------------

# 병해충 정보 등록 요청 데이터 모델
class PestCreate(BaseModel):
    pest_name: str
    pest_description: str
    solution_info: str # 방제 방법 정보

# 병해충 정보 응답 데이터 모델
class PestRecord(PestCreate):
    pest_idx: int
    created_at: datetime
    # updated_at은 DB에 있다면 추가해야 합니다. (여기서는 생략)


# -------------------------------------------------------------
# API 구현
# -------------------------------------------------------------

@router.post("/", response_model=Dict[str, Any])
# NOTE: 병해충 정보 등록은 관리자 권한이 필요할 수 있지만, 여기서는 일단 인증된 사용자만 등록 가능하도록 합니다.
async def create_pest_info(
    pest_data: PestCreate, 
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """
    병해충 정보 등록 API (POST /pest/)
    - 새로운 병해충 정보(이름, 설명, 해결책)를 등록합니다.
    """
    try:
        # 1. 이름 중복 확인
        check_query = "SELECT pest_idx FROM tb_pest WHERE pest_name = %s"
        existing_pest = db_manager.execute_query(check_query, (pest_data.pest_name,), fetch_one=True)
        
        if existing_pest:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"병해충 '{pest_data.pest_name}'은(는) 이미 등록되어 있습니다."
            )

        # 2. 정보 삽입
        insert_query = """
            INSERT INTO tb_pest (pest_name, pest_description, solution_info)
            VALUES (%s, %s, %s)
        """
        params = (
            pest_data.pest_name,
            pest_data.pest_description,
            pest_data.solution_info
        )
        
        result = db_manager.execute_query(insert_query, params)
        
        return {
            "message": "병해충 정보가 성공적으로 등록되었습니다.",
            "pest_idx": result.get('last_row_id')
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"병해충 정보 등록 중 서버 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="병해충 정보 등록 중 오류가 발생했습니다."
        )


@router.get("/list", response_model=List[PestRecord])
async def get_pest_list():
    """
    병해충 정보 목록 조회 API (GET /pest/list)
    - 모든 병해충 정보를 조회합니다. (인증 불필요)
    """
    try:
        select_query = """
            SELECT pest_idx, pest_name, pest_description, solution_info, created_at 
            FROM tb_pest 
            ORDER BY pest_name ASC
        """
        
        records = db_manager.execute_query(select_query)
        return records

    except Exception as e:
        print(f"병해충 정보 조회 중 서버 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="병해충 정보 조회 중 오류가 발생했습니다."
        )
