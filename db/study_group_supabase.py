import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from supabase import AsyncClient


async def create_study_group(
        db: AsyncClient,
        name: str,
        description: Optional[str],
        created_by: str,
        max_members: int,
        requires_approval: bool # << [추가]
) -> Dict[str, Any]:
    """학습 그룹 생성"""
    response = await db.table('study_groups').insert({
        'name': name,
        'description': description,
        'created_by': created_by,
        'max_members': max_members,
        'requires_approval': requires_approval # << [추가]
    }).execute()

    group_id = response.data[0]['id']

    # 생성자를 owner로 자동 추가
    await db.table('group_members').insert({
        'group_id': group_id,
        'user_id': created_by,
        'role': 'owner'
    }).execute()

    return response.data[0]

async def get_all_study_groups(db: AsyncClient, current_user_id: str) -> List[Dict[str, Any]]:
    """모든 활성 그룹 조회 (현재 사용자의 멤버십 정보 포함)"""
    # 그룹 목록 조회
    groups_response = await db.table('study_groups') \
        .select('*, user_account!created_by(name)') \
        .eq('is_active', True) \
        .order('created_at', desc=True) \
        .execute()

    groups = []
    for group in groups_response.data:
        # 각 그룹의 멤버 수 조회
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

async def join_study_group(db: AsyncClient, group_id: int, user_id: str) -> str: # << [수정] 반환타입 변경
    """그룹 참여 또는 참여 요청"""
    # 그룹 정보 조회
    group_res = await db.table('study_groups').select('max_members, requires_approval').eq('id', group_id).single().execute()
    group = group_res.data

    # 현재 멤버 수 확인
    members_res = await db.table('group_members').select('user_id', count='exact').eq('group_id', group_id).execute()

    if members_res.count >= group['max_members']:
        raise Exception('그룹 인원이 가득 찼습니다.')

    # 승인이 필요한 그룹인 경우
    if group['requires_approval']:
        # 이미 멤버인지, 요청했는지 확인
        req_res = await db.table('study_group_join_requests').select('id').eq('group_id', group_id).eq('user_id', user_id).eq('status', 'pending').execute()
        if req_res.data:
            raise Exception('이미 가입을 요청했습니다.')

        await db.table('study_group_join_requests').insert({
            'group_id': group_id,
            'user_id': user_id,
            'status': 'pending'
        }).execute()
        return "가입 요청이 완료되었습니다. 그룹장의 승인을 기다려주세요."
    # 즉시 가입 가능한 그룹인 경우
    else:
        await db.table('group_members').insert({
            'group_id': group_id,
            'user_id': user_id,
            'role': 'member'
        }).execute()
        return "그룹에 참여했습니다."

async def leave_study_group(db: AsyncClient, group_id: int, user_id: str) -> bool:
    """그룹 탈퇴"""
    # owner는 탈퇴 불가
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
    # owner 확인
    member = await db.table('group_members') \
        .select('role') \
        .eq('group_id', group_id) \
        .eq('user_id', user_id) \
        .single() \
        .execute()

    if member.data['role'] != 'owner':
        raise Exception('그룹 삭제 권한이 없습니다.')

    # 그룹 비활성화 (실제 삭제 대신)
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
        # ▼▼▼ [최종 안정성 강화 코드] ▼▼▼
        # 어떤 경우에도 안전하게 이름을 가져오도록 로직을 강화합니다.
        user_name = "알 수 없는 사용자"  # 1. 기본값을 먼저 설정합니다.
        user_account_info = msg.get('user_account')

        # 2. 사용자 정보가 있고(not None), 그 안에 이름이 있을 때만 user_name을 덮어씁니다.
        if user_account_info and user_account_info.get('name'):
            user_name = user_account_info['name']
        # ▲▲▲ [최종 안정성 강화 코드] ▲▲▲

        messages.append({
            'id': msg['id'],
            'group_id': msg['group_id'],
            'user_id': msg['user_id'],
            'user_name': user_name, # 이제 이 값은 절대 비어있지 않습니다.
            'content': msg['content'],
            'created_at': msg['created_at']
        })
    return messages

async def create_group_message(db: AsyncClient, group_id: int, user_id: str, content: str) -> Dict[str, Any]:
    """그룹 채팅 메시지 생성"""
    try:
        # 2. 데이터베이스에 접근하기 직전에 아주 짧은(0.01초) 대기 시간을 추가합니다.
        # 이 코드가 '숨 고르기' 역할을 하여 타이밍 문제를 해결합니다.
        await asyncio.sleep(0.01)

        response = await db.table('study_group_messages').insert({
            'group_id': group_id,
            'user_id': user_id,
            'content': content
        }).execute()

        # 데이터가 반환되지 않았을 경우를 대비한 방어 코드
        if not response.data:
            raise Exception("메시지 삽입 후 데이터가 반환되지 않았습니다. RLS 정책 또는 DB 트리거 지연 문제일 수 있습니다.")

        return response.data[0]
    except Exception as e:
        # 오류가 발생하면 더 명확한 메시지를 포함하여 다시 발생시킵니다.
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
    # 1. 요청 정보 가져오기
    req_res = await db.table('study_group_join_requests').select('group_id, user_id, status').eq('id', request_id).single().execute()
    if not req_res.data or req_res.data['status'] != 'pending':
        raise Exception('처리할 수 없는 요청입니다.')

    request_data = req_res.data

    # 2. 승인(approve) 처리
    if new_status == 'approved':
        # 그룹 정원 확인
        group_res = await db.table('study_groups').select('max_members').eq('id', request_data['group_id']).single().execute()
        members_res = await db.table('group_members').select('user_id', count='exact').eq('group_id', request_data['group_id']).execute()

        if members_res.count >= group_res.data['max_members']:
            raise Exception('그룹 인원이 가득 찼습니다.')

        # group_members 테이블에 추가
        await db.table('group_members').insert({
            'group_id': request_data['group_id'],
            'user_id': request_data['user_id'],
            'role': 'member'
        }).execute()

    # 3. 요청 상태 업데이트 ('approved' 또는 'rejected')
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

async def create_challenge(db: AsyncClient, group_id: int, user_id: str, challenge_data: Dict[str, Any]) -> Dict[str, Any]:
    """group_challenges 테이블에 새로운 챌린지 생성"""
    # ▼▼▼ [2. 현재 시간을 UTC 기준으로 가져오도록 수정] ▼▼▼
    end_date = datetime.now(timezone.utc) + timedelta(days=challenge_data['duration_days'])

    response = await db.table('group_challenges').insert({
        'group_id': group_id,
        'created_by_user_id': user_id,
        'title': challenge_data['title'],
        'description': challenge_data['description'],
        'challenge_type': challenge_data['challenge_type'],
        'target_value': challenge_data['target_value'],
        'end_date': end_date.isoformat(),
    }).execute()

    return response.data[0]

async def get_challenges_by_group_id(db: AsyncClient, group_id: int) -> List[Dict[str, Any]]:
    """특정 그룹의 모든 챌린지와 각 챌린지 생성자의 진행률 조회 (안정성 강화 버전)"""

    challenges_res = await db.table('group_challenges') \
        .select('*, creator:user_account!created_by_user_id(name)') \
        .eq('group_id', group_id) \
        .order('end_date', desc=True) \
        .execute()

    if not challenges_res.data:
        return []

    challenges_with_progress = []
    for challenge in challenges_res.data:
        creator_id = challenge['created_by_user_id']

        progress_res = await db.table('user_challenge_progress') \
            .select('current_value') \
            .eq('challenge_id', challenge['id']) \
            .eq('user_id', creator_id) \
            .execute()

        creator_name = challenge.get('creator', {}).get('name', 'Unknown') if challenge.get('creator') else 'Unknown'

        challenge['creator_name'] = creator_name

        user_current_value = progress_res.data[0]['current_value'] if progress_res.data else 0
        challenge['user_current_value'] = user_current_value

        # ▼▼▼ [2. is_completed 필드를 계산하여 추가] ▼▼▼
        challenge['is_completed'] = user_current_value >= challenge['target_value']
        # ▲▲▲ 여기까지 추가 ▲▲▲

        challenges_with_progress.append(challenge)

    return challenges_with_progress

async def log_progress(db: AsyncClient, user_id: str, log_type: str, value: int):
    """사용자의 학습 활동을 '자신이 만든' 활성 챌린지에만 기록 (목표치 초과 방지)"""
    try:
        # ▼▼▼ [3. 조회 시 target_value도 함께 가져오도록 select 수정] ▼▼▼
        active_challenges_res = await db.table('group_challenges') \
            .select('id, target_value') \
            .eq('created_by_user_id', user_id) \
            .eq('challenge_type', log_type) \
            .eq('is_active', True) \
            .gt('end_date', datetime.now(timezone.utc).isoformat()) \
            .execute()

        if not active_challenges_res.data:
            return

        for challenge in active_challenges_res.data:
            challenge_id = challenge['id']
            target_value = challenge['target_value'] # 목표치

            progress_res = await db.table('user_challenge_progress') \
                .select('id, current_value') \
                .eq('challenge_id', challenge_id) \
                .eq('user_id', user_id) \
                .execute()

            if progress_res.data:
                existing_progress = progress_res.data[0]
                current_value = existing_progress['current_value']

                # ▼▼▼ [4. 이미 목표를 달성했으면 더 이상 업데이트하지 않음] ▼▼▼
                if current_value >= target_value:
                    print(f"DEBUG: 챌린지 ID {challenge_id}는 이미 목표를 달성하여 진행률을 업데이트하지 않습니다.")
                    continue # 다음 챌린지로 넘어감

                # 목표치를 넘지 않도록 계산
                new_value = min(current_value + value, target_value)
                await db.table('user_challenge_progress').update({'current_value': new_value}).eq('id', existing_progress['id']).execute()
                print(f"DEBUG: 챌린지 ID {challenge_id} 진행률 업데이트 완료. 새 값: {new_value}")
            else:
                # 첫 기록 시에도 목표치를 넘지 않도록 계산
                new_value = min(value, target_value)
                await db.table('user_challenge_progress').insert({'challenge_id': challenge_id, 'user_id': user_id, 'current_value': new_value}).execute()
                print(f"DEBUG: 챌린지 ID {challenge_id} 진행률 첫 기록 완료. 값: {new_value}")
    except Exception as e:
        print(f"ERROR in log_progress: {e}")

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

    # count가 1 이상이면 멤버로 간주
    return response.count > 0