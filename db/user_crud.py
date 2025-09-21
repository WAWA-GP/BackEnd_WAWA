# 'User' 모델에 대한 데이터베이스 CRUD(Create, Read, Update, Delete) 작업을 정의하는 파일입니다.
from sqlalchemy.orm import Session
from database import models as db_models
from models import user_model

# --- 사용자 조회 (Username 기준) ---
def get_user_by_username(db: Session, username: str):
    return db.query(db_models.User).filter(db_models.User.username == username).first()

# --- 사용자 조회 (ID 기준) ---
def get_user(db: Session, user_id: int):
    return db.query(db_models.User).filter(db_models.User.id == user_id).first()

# --- 사용자 생성 ---
def create_user(db: Session, user: user_model.UserCreate, hashed_password: str):
    db_user = db_models.User(
        username=user.username,
        password=hashed_password,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- 사용자 수정 ---
def update_user(db: Session, user_id: int, update_data: dict):
    db_user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
    if not db_user:
        return None # 사용자가 없으면 None 반환

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user