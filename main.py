from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# -------------------------------------------------------------
# 1. 내부 라우터 및 설정 임포트
# -------------------------------------------------------------
from routes import user 
from routes import disinfestation 
from routes import pest 
# config.db에서 init_db_pool(초기화) 및 get_db_manager(관리자 가져오기) 함수 임포트
from config.db import init_db_pool, get_db_manager 

# .env 파일 로드
load_dotenv()

# -------------------------------------------------------------
# 2. 필수 환경 변수 확인
# -------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("FATAL ERROR: JWT_SECRET environment variable not set. Please check your .env file.")

# -------------------------------------------------------------
# 3. FastAPI 앱 인스턴스 생성
# -------------------------------------------------------------
app = FastAPI(
    title="AI 방제 커뮤니티 API 서버", 
    version="1.0.0",
    description="농작물 병해충 방제 및 커뮤니티 기능을 제공하는 백엔드 서버입니다."
)

# -------------------------------------------------------------
# 4. 서버 이벤트 핸들러 (DB 풀 초기화 및 종료)
# -------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """
    서버 시작 시 DB 연결 풀을 비동기적으로 초기화합니다.
    """
    await init_db_pool()
    print("INFO: FastAPI startup sequence completed.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    서버 종료 시 DB 연결 풀을 안전하게 닫습니다.
    """
    db_manager = await get_db_manager()
    await db_manager.close()
    print("INFO: DB Pool closed and FastAPI shutdown sequence completed.")


# -------------------------------------------------------------
# 5. 정적 파일 서비스 설정 (public 폴더 연결)
# -------------------------------------------------------------
# public 폴더를 웹 서버의 루트 경로('/')로 마운트
try:
    app.mount("/", StaticFiles(directory="public", html=True), name="public")
except RuntimeError as e:
    # public 디렉토리가 없는 경우에도 서버가 멈추지 않도록 예외 처리
    print(f"경고: StaticFiles 설정 중 오류 발생. 'public' 디렉토리가 없거나 접근할 수 없습니다: {e}")

# -------------------------------------------------------------
# 6. 라우트 등록 (모든 API는 /api 프리픽스를 가집니다)
# -------------------------------------------------------------
app.include_router(user.router, prefix="/api")
app.include_router(disinfestation.router, prefix="/api")
app.include_router(pest.router, prefix="/api")

# -------------------------------------------------------------
# 7. 기본 상태 확인 라우트
# -------------------------------------------------------------
@app.get("/status") 
async def api_status():
   
    return {"status": "ok", "message": "FastAPI is running and API is active!"}

