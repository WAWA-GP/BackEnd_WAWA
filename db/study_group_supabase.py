from supabase import AsyncClient
from typing import List, Optional, Dict, Any

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
        messages.append({
            'id': msg['id'],
            'group_id': msg['group_id'],
            'user_id': msg['user_id'],
            'user_name': msg.get('user_account', {}).get('name', 'Unknown'),
            'content': msg['content'],
            'created_at': msg['created_at']
        })
    return messages

async def create_group_message(db: AsyncClient, group_id: int, user_id: str, content: str) -> Dict[str, Any]:
    """그룹 채팅 메시지 생성"""
    response = await db.table('study_group_messages').insert({
        'group_id': group_id,
        'user_id': user_id,
        'content': content
    }).execute()
    return response.data[0]

async def get_join_requests(db: AsyncClient, group_id: int) -> List[Dict[str, Any]]:
    """특정 그룹의 'pending' 상태인 가입 요청 목록 조회"""

    print(f"--- [DB] group_id: {group_id} 에 대한 가입 요청을 'pending' 상태로 조회합니다. ---") # << 디버그 로그 추가

    try:
        response = await db.table('study_group_join_requests') \
            .select('*, user_account(name)') \
            .eq('group_id', group_id) \
            .eq('status', 'pending') \
            .order('created_at', desc=True) \
            .execute()

        # << 디버그 로그 추가: Supabase로부터 받은 원본 데이터를 출력 >>
        print("--- [DB] Supabase 응답 데이터 ---")
        print(response.data)
        print("------------------------------")

        if not response.data:
            # 이 로그가 보인다면 RLS 정책 문제일 가능성이 매우 높습니다.
            print("--- [DB] Supabase가 반환한 데이터가 없습니다. RLS 정책이나 테이블 데이터를 확인하세요. ---")
            return []

        requests = []
        for req in response.data:
            requests.append({
                'request_id': req['id'],
                'user_id': req['user_id'],
                'user_name': req.get('user_account', {}).get('name') if req.get('user_account') else 'Unknown',
                'requested_at': req['created_at']
            })

        print(f"--- [DB] 최종적으로 {len(requests)}개의 요청을 반환합니다. ---") # << 디버그 로그 추가
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