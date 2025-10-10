from supabase import AsyncClient
from typing import List, Optional, Dict, Any

async def create_study_group(
        db: AsyncClient,
        name: str,
        description: Optional[str],
        created_by: str,
        max_members: int
) -> Dict[str, Any]:
    """학습 그룹 생성"""
    response = await db.table('study_groups').insert({
        'name': name,
        'description': description,
        'created_by': created_by,
        'max_members': max_members
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
            .select('user_id, role') \
            .eq('group_id', group['id']) \
            .execute()

        member_count = len(members_response.data)
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

async def join_study_group(db: AsyncClient, group_id: int, user_id: str) -> bool:
    """그룹 참여"""
    # 그룹 정보 조회
    group = await db.table('study_groups').select('max_members').eq('id', group_id).single().execute()

    # 현재 멤버 수 확인
    members = await db.table('group_members').select('user_id').eq('group_id', group_id).execute()

    if len(members.data) >= group.data['max_members']:
        raise Exception('그룹 인원이 가득 찼습니다.')

    # 멤버 추가
    await db.table('group_members').insert({
        'group_id': group_id,
        'user_id': user_id,
        'role': 'member'
    }).execute()

    return True

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
