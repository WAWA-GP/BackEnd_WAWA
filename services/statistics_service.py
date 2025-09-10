from datetime import datetime
from typing import List, Optional, Tuple
from models.statistics_model import LearningLog, LearningGoal, OverallStats, ProgressStats

# 누적 통계 계산
def calculate_overall_statistics(logs: List[LearningLog]) -> OverallStats:
    stats = OverallStats()
    for log in logs:
        if log.log_type == 'conversation' and log.duration is not None:
            stats.total_conversation_duration += log.duration
        elif log.log_type == 'grammar' and log.count is not None:
            stats.total_grammar_count += log.count
        elif log.log_type == 'pronunciation' and log.count is not None:
            stats.total_pronunciation_count += log.count
    return stats

# 진척도 계산
def calculate_progress_statistics(
        logs: List[LearningLog],
        goal: LearningGoal
) -> Optional[ProgressStats]:
    if not goal:
        return None

    progress_logs = [log for log in logs if log.created_at >= goal.created_at]

    current_duration = 0
    current_grammar_count = 0
    current_pronunciation_count = 0

    for log in progress_logs:
        if log.log_type == 'conversation' and log.duration is not None:
            current_duration += log.duration
        elif log.log_type == 'grammar' and log.count is not None:
            current_grammar_count += log.count
        elif log.log_type == 'pronunciation' and log.count is not None:
            current_pronunciation_count += log.count

    progress = ProgressStats(
        conversation_progress=round((current_duration / goal.conversation_goal) * 100, 2) if goal.conversation_goal > 0 else 0,
        grammar_progress=round((current_grammar_count / goal.grammar_goal) * 100, 2) if goal.grammar_goal > 0 else 0,
        pronunciation_progress=round((current_pronunciation_count / goal.pronunciation_goal) * 100, 2) if goal.pronunciation_goal > 0 else 0,
    )
    return progress