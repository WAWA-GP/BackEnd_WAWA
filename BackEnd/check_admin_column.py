# check_admin_column.py
from app.database import SessionLocal
from app.models import User

def check_admin_column():
    db = SessionLocal()
    try:
        # users 테이블에 첫 번째 사용자 가져오기
        user = db.query(User).first()
        if user:
            print(f"username: {user.username}, is_admin: {user.is_admin}")
        else:
            print("❗ users 테이블에 등록된 사용자가 없습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_column()
