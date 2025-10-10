from fastapi import APIRouter, HTTPException, Path, Depends, Request, Response
from models.statistics_model import StatisticsResponse, User, LearningProgressResponse
from db.statistics_supabase import get_user_data_from_supabase, add_learning_log_to_user
from services.performance_monitor import measure_performance
from services.statistics_service import calculate_overall_statistics, generate_daily_feedback, \
    calculate_progress_statistics, LearningLog, generate_learning_progress, generate_overall_feedback
from core.dependencies import get_current_user
from core.database import get_db
from supabase import AsyncClient
import logging
import json
from datetime import date

router = APIRouter()

@router.post("/log/add", status_code=201)
@measure_performance("학습 로그 추가")
async def add_learning_log(
        request: Request,  # ✅ 추가: 원본 요청 확인
        log: LearningLog,
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """현재 로그인한 사용자의 학습 로그를 추가합니다."""

    # ✅ 디버깅: 요청 데이터 출력
    try:
        body = await request.body()
        print(f"=== 받은 요청 body: {body.decode('utf-8')} ===")
        print(f"=== 파싱된 log 객체: {log.model_dump()} ===")
        print(f"=== current_user: {current_user} ===")
    except Exception as e:
        print(f"요청 데이터 읽기 오류: {e}")

    user_id = current_user.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail="인증되지 않은 사용자입니다.")

    try:
        log_data = log.model_dump()

        from datetime import datetime
        if 'created_at' in log_data and isinstance(log_data['created_at'], datetime):
            log_data['created_at'] = log_data['created_at'].isoformat()

        await add_learning_log_to_user(user_id, log_data, db)
        return {"message": "학습 로그가 성공적으로 추가되었습니다."}
    except Exception as e:
        print(f"로그 추가 오류: {e}")
        raise HTTPException(status_code=500, detail=f"로그 추가 중 오류 발생: {e}")

@router.get("/statistics/{user_id}", response_model=StatisticsResponse)
@measure_performance("통계 계산")
async def get_user_statistics(
        user_id: str = Path(..., title="사용자 ID", description="통계를 조회할 사용자의 고유 ID"),
        db: AsyncClient = Depends(get_db)
):
    user_data = await get_user_data_from_supabase(user_id, db)

    if not user_data or not user_data.get('learning_logs'):
        from models.statistics_model import OverallStats
        return StatisticsResponse(
            overall_statistics=OverallStats(),
            progress_statistics=None,
            feedback="아직 기록된 학습이 없네요. 오늘부터 시작해볼까요?"
        )

    user = User(**user_data)

    # 1. 누적 통계 계산 (기존과 동일)
    overall_stats = calculate_overall_statistics(user.learning_logs)

    # 2. '목표 달성률' 계산 로직을 삭제합니다.
    # progress_stats = None
    # if user.learning_goals:
    #     progress_stats = calculate_progress_statistics(user.learning_logs, user.learning_goals)

    # 3. 새로 만든 '종합 피드백' 생성 함수를 호출합니다.
    feedback = generate_overall_feedback(overall_stats)

    # 4. progress_statistics는 항상 null로, feedback은 새로운 종합 피드백으로 반환합니다.
    return StatisticsResponse(
        overall_statistics=overall_stats,
        progress_statistics=None,
        feedback=feedback
    )
@router.get("/today-progress")
@measure_performance("오늘의 진행률 조회")
async def get_today_progress(
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """오늘의 학습 진행 상황을 반환합니다."""
    from datetime import date

    user_id = current_user.get('user_id')
    user_data = await get_user_data_from_supabase(user_id, db)

    if not user_data or not user_data.get('learning_logs'):
        return {
            'conversation': 0,
            'grammar': 0,
            'pronunciation': 0
        }

    # 오늘 날짜의 로그만 필터링
    today = date.today().isoformat()
    today_logs = [
        log for log in user_data['learning_logs']
        if log.get('created_at', '').startswith(today)
    ]

    progress = {'conversation': 0, 'grammar': 0, 'pronunciation': 0}
    for log in today_logs:
        log_type = log.get('log_type')
        if log_type == 'conversation':
            progress['conversation'] += log.get('duration', 0)
        elif log_type == 'grammar':
            progress['grammar'] += log.get('count', 0)
        elif log_type == 'pronunciation':
            progress['pronunciation'] += log.get('count', 0)

    return progress

@router.get("/progress", response_model=LearningProgressResponse)
@measure_performance("학습 진척도 조회")
async def get_learning_progress(
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """
    현재 로그인된 사용자의 학습 목표 대비 진척도를 반환합니다.
    """
    user_id = current_user.get('user_id')
    user_data = await get_user_data_from_supabase(user_id, db)

    if not user_data:
        raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다.")

    learning_goals = user_data.get('learning_goals')
    if not learning_goals:
        raise HTTPException(status_code=404, detail="설정된 학습 목표가 없습니다.")

    # learning_logs가 없거나 None일 경우 빈 리스트로 처리
    learning_logs_raw = user_data.get('learning_logs') or []
    learning_logs = [LearningLog(**log) for log in learning_logs_raw]

    # 서비스 함수를 호출하여 진척도 계산
    progress_data = generate_learning_progress(learning_logs, learning_goals)

    if not progress_data:
        raise HTTPException(status_code=500, detail="진척도 계산 중 오류가 발생했습니다.")

    return progress_data

@router.get("/daily-feedback")
@measure_performance("일일 피드백 조회")
async def get_daily_feedback(
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """오늘의 학습 진행 상황과 목표를 기반으로 동적인 피드백을 반환합니다."""
    try:
        user_id = current_user.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="인증되지 않은 사용자입니다.")

        # 사용자 데이터에서 학습 목표와 로그를 가져옵니다.
        user_data = await get_user_data_from_supabase(user_id, db)
        if not user_data:
            # 사용자는 있지만 로그나 목표가 없는 초기 상태
            return generate_daily_feedback({}, None)

        learning_goals = user_data.get('learning_goals')
        learning_logs = user_data.get('learning_logs') or []

        # 목표가 없으면 기본 피드백 반환
        if not learning_goals:
            return generate_daily_feedback({}, None)

        # 1. 오늘의 진행률 계산 (today-progress 로직과 동일)
        today = date.today().isoformat()
        today_logs = [
            log for log in learning_logs
            # ⭐️ FIX: 'timestamp' -> 'created_at' 으로 키 이름 수정
            if log and log.get('created_at', '').startswith(today)
        ]

        today_progress = {'conversation': 0, 'grammar': 0, 'pronunciation': 0}
        for log in today_logs:
            log_type = log.get('log_type')
            if log_type == 'conversation':
                today_progress['conversation'] += log.get('duration', 0)
            elif log_type == 'grammar':
                today_progress['grammar'] += log.get('count', 0)
            elif log_type == 'pronunciation':
                today_progress['pronunciation'] += log.get('count', 0)

        # 2. statistics_service의 피드백 생성 함수 호출하여 결과 반환
        feedback = generate_daily_feedback(today_progress, learning_goals)

        # 피드백이 생성되지 않은 경우(예: 목표 없음) 204 No Content 반환
        if feedback is None:
            return Response(status_code=204)

        return feedback

    except Exception as e:
        logging.error(f"일일 피드백 조회 오류: {str(e)}")
        # 에러 발생 시에도 Flutter 앱이 멈추지 않도록 기본 피드백 반환
        return {
            "message": "피드백을 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            "icon": "error_outline",
            "color": "grey"
        }
