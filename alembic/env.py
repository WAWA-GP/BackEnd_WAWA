from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

import os
import sys

# 🔽 현재 디렉토리 기준으로 상위 경로(app 폴더 포함)를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 🔽 app.models에서 Base (declarative_base) 불러오기
from app.models import Base  # 여기서 Base는 declarative_base()

# 🔽 Alembic 설정 객체 가져오기
config = context.config

# 🔽 config에서 logging 설정 적용
fileConfig(config.config_file_name)

# 🔽 여기에 우리가 사용할 메타데이터를 등록해야 --autogenerate 기능이 작동함
target_metadata = Base.metadata

# DB 연결 및 마이그레이션 실행 함수
def run_migrations_offline():
    """Offline 모드에서 마이그레이션 실행 (DB 연결 없이 SQL 파일로 출력)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Online 모드에서 실제 DB와 연결된 상태로 마이그레이션 실행"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

# 실행 분기
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
