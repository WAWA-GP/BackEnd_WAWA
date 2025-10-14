import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from supabase import AsyncClient
from models.challenge_model import ChallengeCreate, ChallengeUpdate


async def create_study_group(
        db: AsyncClient,
        name: str,
        description: Optional[str],
        created_by: str,
        max_members: int,
        requires_approval: bool
) -> Dict[str, Any]:
    """학습 그룹 생성"""
    response = await db.table('study_groups').insert({
        'name': name,
        'description': description,
        'created_by': created_by,
        'max_members': max_members,
        'requires_approval': requires_approval
    }).execute()

    group_id = response.data[0]['id']

    await db.table('group_members').insert({
        'group_id': group_id,
        'user_id': created_by,
        'role': 'owner'
    }).execute()

    return response.data[0]

async def get_all_study_groups(db: AsyncClient, current_user_id: str) -> List[Dict[str, Any]]:
    """모든 활성 그룹 조회 (현재 사용자의 멤버십 정보 포함)"""
    groups_response = await db.table('study_groups') \
        .select('*, user_account!created_by(name)') \
        .eq('is_active', True) \
        .order('created_at', desc=True) \
        .execute()

    groups = []
    for group in groups_response.data:
        members_response = await db.table('group_members') \
            .select('user_id, role', count='exact') \
            .eq('group_id', group['id']) \
            .execute()

        member_count = members_response.count
        is_member = any(m['user_id'] == current_user_id for m in members_response.data)
        is_owner = any(m['user_id'] == current_user_id and m['role'] == 'owner'
                       for m in members_response.data)

        groups.append({
            **group,
            'member_count': member_count,
            'is_member': is_member,
            'is_owner': is_owner,
            'creator_name': group['user_account']['name'] if group.get('user_account') else None
        })

    return groups

async def join_study_group(db: AsyncClient, group_id: int, user_id: str) -> str:
    """그룹 참여 또는 참여 요청"""
    group_res = await db.table('study_groups').select('max_members, requires_approval').eq('id', group_id).single().execute()
    group = group_res.data

    members_res = await db.table('group_members').select('user_id', count='exact').eq('group_id', group_id).execute()

    if members_res.count >= group['max_members']:
        raise Exception('그룹 인원이 가득 찼습니다.')

    if group['requires_approval']:
        req_res = await db.table('study_group_join_requests').select('id').eq('group_id', group_id).eq('user_id', user_id).eq('status', 'pending').execute()
        if req_res.data:
            raise Exception('이미 가입을 요청했습니다.')

        await db.table('study_group_join_requests').insert({
            'group_id': group_id,
            'user_id': user_id,
            'status': 'pending'
        }).execute()
        return "가입 요청이 완료되었습니다. 그룹장의 승인을 기다려주세요."
    else:
        await db.table('group_members').insert({
            'group_id': group_id,
            'user_id': user_id,
            'role': 'member'
        }).execute()
        return "그룹에 참여했습니다."

async def leave_study_group(db: AsyncClient, group_id: int, user_id: str) -> bool:
    """그룹 탈퇴"""
    member = await db.table('group_members') \
        .select('role') \
        .eq('group_id', group_id) \
        .eq('user_id', user_id) \
        .single() \
        .execute()

    if member.data['role'] == 'owner':
        raise Exception('그룹 소유자는 탈퇴할 수 없습니다.')

    await db.table('group_members') \
        .delete() \
        .eq('group_id', group_id) \
        .eq('user_id', user_id) \
        .execute()

    return True

async def get_group_members(db: AsyncClient, group_id: int) -> List[Dict[str, Any]]:
    """그룹 멤버 목록 조회"""
    response = await db.table('group_members') \
        .select('user_id, role, joined_at, user_account(name)') \
        .eq('group_id', group_id) \
        .order('joined_at') \
        .execute()

    members = []
    for member in response.data:
        members.append({
            'user_id': member['user_id'],
            'user_name': member['user_account']['name'] if member.get('user_account') else 'Unknown',
            'role': member['role'],
            'joined_at': member['joined_at']
        })

    return members

async def delete_study_group(db: AsyncClient, group_id: int, user_id: str) -> bool:
    """그룹 삭제 (owner만 가능)"""
    member = await db.table('group_members') \
        .select('role') \
        .eq('group_id', group_id) \
        .eq('user_id', user_id) \
        .single() \
        .execute()

    if member.data['role'] != 'owner':
        raise Exception('그룹 삭제 권한이 없습니다.')

    await db.table('study_groups') \
        .update({'is_active': False}) \
        .eq('id', group_id) \
        .execute()

    return True

async def get_group_messages(db: AsyncClient, group_id: int) -> List[Dict[str, Any]]:
    """그룹 채팅 메시지 목록 조회"""
    response = await db.table('study_group_messages') \
        .select('*, user_account(name)') \
        .eq('group_id', group_id) \
        .order('created_at', desc=False) \
        .limit(100) \
        .execute()

    messages = []
    for msg in response.data:
        user_name = "알 수 없는 사용자"
        user_account_info = msg.get('user_account')
        if user_account_info and user_account_info.get('name'):
            user_name = user_account_info['name']

        messages.append({
            'id': msg['id'],
            'group_id': msg['group_id'],
            'user_id': msg['user_id'],
            'user_name': user_name,
            'content': msg['content'],
            'created_at': msg['created_at']
        })
    return messages

async def create_group_message(db: AsyncClient, group_id: int, user_id: str, content: str) -> Dict[str, Any]:
    """그룹 채팅 메시지 생성"""
    try:
        await asyncio.sleep(0.01)
        response = await db.table('study_group_messages').insert({
            'group_id': group_id,
            'user_id': user_id,
            'content': content
        }).execute()

        if not response.data:
            raise Exception("메시지 삽입 후 데이터가 반환되지 않았습니다.")

        return response.data[0]
    except Exception as e:
        raise Exception(f"create_group_message DB 작업 실패: {e}")

async def get_join_requests(db: AsyncClient, group_id: int) -> List[Dict[str, Any]]:
    """특정 그룹의 'pending' 상태인 가입 요청 목록 조회"""
    try:
        response = await db.table('study_group_join_requests') \
            .select('*, user_account(name)') \
            .eq('group_id', group_id) \
            .eq('status', 'pending') \
            .order('created_at', desc=True) \
            .execute()

        if not response.data:
            return []

        requests = []
        for req in response.data:
            requests.append({
                'request_id': req['id'],
                'user_id': req['user_id'],
                'user_name': req.get('user_account', {}).get('name') if req.get('user_account') else 'Unknown',
                'requested_at': req['created_at']
            })
        return requests
    except Exception as e:
        print(f"--- [DB] 데이터베이스 쿼리 중 심각한 오류 발생 ---")
        print(e)
        raise e

async def process_join_request(db: AsyncClient, request_id: int, new_status: str) -> bool:
    """가입 요청 처리 (승인 또는 거절)"""
    req_res = await db.table('study_group_join_requests').select('group_id, user_id, status').eq('id', request_id).single().execute()
    if not req_res.data or req_res.data['status'] != 'pending':
        raise Exception('처리할 수 없는 요청입니다.')

    request_data = req_res.data

    if new_status == 'approved':
        group_res = await db.table('study_groups').select('max_members').eq('id', request_data['group_id']).single().execute()
        members_res = await db.table('group_members').select('user_id', count='exact').eq('group_id', request_data['group_id']).execute()

        if members_res.count >= group_res.data['max_members']:
            raise Exception('그룹 인원이 가득 찼습니다.')

        await db.table('group_members').insert({
            'group_id': request_data['group_id'],
            'user_id': request_data['user_id'],
            'role': 'member'
        }).execute()

    await db.table('study_group_join_requests').update({'status': new_status}).eq('id', request_id).execute()
    return True

async def get_group_owner(db: AsyncClient, group_id: int) -> Optional[str]:
    """그룹 소유자의 user_id를 반환"""
    owner_res = await db.table('group_members') \
        .select('user_id') \
        .eq('group_id', group_id) \
        .eq('role', 'owner') \
        .maybe_single() \
        .execute()
    return owner_res.data['user_id'] if owner_res.data else None

async def create_challenge(db: AsyncClient, group_id: int, user_id: str, challenge_data: ChallengeCreate) -> Dict[str, Any]:
    """group_challenges 테이블에 새로운 자유 형식 챌린지 생성"""
    end_date = datetime.now(timezone.utc) + timedelta(days=challenge_data.duration_days)

    response = await db.table('group_challenges').insert({
        'group_id': group_id,
        'created_by_user_id': user_id,
        'title': challenge_data.title,
        'description': challenge_data.description,
        'end_date': end_date.isoformat(),
    }).execute()

    return response.data[0]

# ▼▼▼ [수정 완료] get_challenges_by_group_id 함수 ▼▼▼
async def get_challenges_by_group_id(db: AsyncClient, group_id: int, current_user_id: str) -> List[Dict[str, Any]]:
    """특정 그룹의 모든 챌린지와 완료한 참여자 정보 조회 (최적화 버전)"""
    challenges_res = await db.table('group_challenges') \
        .select('*, creator:user_account!created_by_user_id(name)') \
        .eq('group_id', group_id) \
        .order('end_date', desc=True) \
        .execute()

    if not challenges_res.data:
        return []

    challenges = challenges_res.data
    challenge_ids = [c['id'] for c in challenges]

    participants_res = await db.table('challenge_participants') \
        .select('challenge_id, user_id, completed_at, user_account(name)') \
        .in_('challenge_id', challenge_ids) \
        .eq('status', 'approved') \
        .execute()

    participants_data = participants_res.data

    participants_by_challenge = {cid: [] for cid in challenge_ids}
    for p in participants_data:
        if p.get('user_account'):
            participants_by_challenge[p['challenge_id']].append({
                'user_id': p['user_id'],
                'user_name': p['user_account']['name'],
                'completed_at': p['completed_at']
            })

    response_data = []
    for challenge in challenges:
        challenge_id = challenge['id']
        participants = participants_by_challenge.get(challenge_id, [])
        user_has_completed = any(p['user_id'] == current_user_id for p in participants)

        # [핵심 수정] **challenge 대신, 필드를 명시적으로 매핑합니다.
        response_data.append({
            'id': challenge['id'],
            'group_id': challenge['group_id'],
            'creator_id': challenge['created_by_user_id'], # DB 컬럼명을 모델 필드명으로 변경
            'creator_name': challenge.get('creator', {}).get('name', 'Unknown'),
            'title': challenge['title'],
            'description': challenge['description'],
            'end_date': challenge['end_date'],
            'created_at': challenge['created_at'],
            'participants': participants,
            'user_has_completed': user_has_completed,
        })

    return response_data

async def create_challenge_submission(db: AsyncClient, challenge_id: int, user_id: str, content: str, image_url: Optional[str]) -> Dict[str, Any]:
    """챌린지 인증 제출"""
    existing_sub = await db.table('challenge_submissions') \
        .select('id, status') \
        .eq('challenge_id', challenge_id) \
        .eq('user_id', user_id) \
        .in_('status', ['pending', 'approved']) \
        .execute()

    if existing_sub.data:
        raise Exception(f"이미 '{existing_sub.data[0]['status']}' 상태의 인증 내역이 존재합니다.")

    response = await db.table('challenge_submissions').insert({
        'challenge_id': challenge_id,
        'user_id': user_id,
        'proof_content': content,
        'proof_image_url': image_url
    }).execute()
    return response.data[0]

async def get_submissions_for_challenge(db: AsyncClient, challenge_id: int) -> List[Dict[str, Any]]:
    """특정 챌린지의 모든 인증 내역 조회 (그룹장용)"""
    response = await db.table('challenge_submissions') \
        .select('*, user_account(name)') \
        .eq('challenge_id', challenge_id) \
        .order('submitted_at', desc=True) \
        .execute()
    return response.data

async def process_submission(db: AsyncClient, submission_id: int, new_status: str) -> Dict[str, Any]:
    """인증 승인/거절 처리"""
    submission_update_res = await db.table('challenge_submissions') \
        .update({'status': new_status}) \
        .eq('id', submission_id) \
        .select('challenge_id, user_id') \
        .execute()

    if not submission_update_res.data:
        raise Exception("존재하지 않는 인증 내역입니다.")

    submission_info = submission_update_res.data[0]

    if new_status == 'approved':
        existing_participant = await db.table('challenge_participants') \
            .select('id') \
            .eq('challenge_id', submission_info['challenge_id']) \
            .eq('user_id', submission_info['user_id']) \
            .execute()

        if not existing_participant.data:
            await db.table('challenge_participants').insert({
                'challenge_id': submission_info['challenge_id'],
                'user_id': submission_info['user_id'],
                'status': 'approved'
            }).execute()

    return submission_info

async def get_challenge_by_id(db: AsyncClient, challenge_id: int) -> Dict[str, Any]:
    """ID로 단일 챌린지 조회 (권한 확인용)"""
    response = await db.table('group_challenges').select('*').eq('id', challenge_id).maybe_single().execute()
    return response.data

async def update_challenge(db: AsyncClient, challenge_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """챌린지 정보 업데이트"""
    response = await db.table('group_challenges').update(update_data).eq('id', challenge_id).execute()
    return response.data[0]

async def delete_challenge(db: AsyncClient, challenge_id: int):
    """챌린지 삭제"""
    await db.table('group_challenges').delete().eq('id', challenge_id).execute()

async def is_user_group_member(db: AsyncClient, group_id: int, user_id: str) -> bool:
    """사용자가 특정 그룹의 멤버인지 확인합니다."""
    response = await db.table('group_members') \
        .select('user_id', count='exact') \
        .eq('group_id', group_id) \
        .eq('user_id', user_id) \
        .execute()

    return response.count > 0