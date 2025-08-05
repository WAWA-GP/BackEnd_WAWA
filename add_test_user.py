# add_test_user.py
from app.database import SessionLocal
from app.models import User

db = SessionLocal()
new_user = User(username="admin_test", password="1234", is_admin=True)
db.add(new_user)
db.commit()
db.close()

print("✅ 테스트 사용자 생성 완료!")
