# 데이터베이스 연결 및 세션 관리를 담당하는 파일
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 사용할 데이터베이스 주소를 설정합니다.
DATABASE_URL = "sqlite:///./app.db"

# SQLAlchemy 엔진을 생성합니다.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 데이터베이스 세션 생성을 위한 클래스(SessionLocal)를 만듭니다.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# API 엔드포인트에서 데이터베이스 세션을 사용하기 위한 의존성 함수입니다.
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()