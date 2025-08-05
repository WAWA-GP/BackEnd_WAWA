from datetime import timedelta

SECRET_KEY = "your_secret_key_here"  # ⚠️ 배포 시에는 반드시 .env로 관리
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30