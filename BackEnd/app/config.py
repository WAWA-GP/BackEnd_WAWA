from datetime import timedelta

# JWT 설정
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"

# Access / Refresh Token 만료 시간
ACCESS_TOKEN_EXPIRE_MINUTES = 15   # 15분
REFRESH_TOKEN_EXPIRE_DAYS = 7      # 7일