import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv


# load_dotenv()는 일반적으로 main.py에서 한 번 호출되지만, 
# 독립적인 모듈 테스트를 위해 여기서 한 번 더 호출할 수도 있습니다.
load_dotenv()

# 환경 변수에서 DB 연결 세부 정보를 가져옵니다.
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# MySQL + PyMySQL 드라이버를 사용하는 데이터베이스 URL을 구성합니다.
# 형식: mysql+pymysql://user:password@host:port/database_name
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# 1. Database Engine: 데이터베이스와의 연결을 관리합니다.
# pool_recycle=3600: MySQL 서버의 타임아웃을 방지하기 위해 1시간마다 연결을 재활용합니다.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_recycle=3600
)

# 2. SessionLocal: 실제 DB 작업(쿼리)을 위한 Session 객체를 생성하는 팩토리입니다.
# autocommit=False: 트랜잭션을 수동으로 관리합니다.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base: SQLAlchemy 모델(테이블 클래스)을 위한 기본 클래스입니다.
Base = declarative_base()

# FastAPI Dependency: 요청마다 DB 세션을 제공하고 요청 완료 후 닫아줍니다.
def get_db():
    """요청 수명 주기 동안 DB 세션을 제공하고 닫아주는 제너레이터 함수입니다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
