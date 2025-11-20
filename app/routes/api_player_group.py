from flask import Blueprint, request, jsonify
from app.models.player import Person, PlayerGroup
from app.extensions import db
from app.utils.jwt_auth import token_required
from sqlalchemy import or_
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

api_player_group_bp = Blueprint('api_player_group', __name__)

@api_player_group_bp.route('/list', methods=['GET'])
@token_required
def api_player_group_list():
    """获取玩家分组列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = PlayerGroup.query
        
        # 搜索条件
        if search:
            query = query.filter(
                or_(
                    PlayerGroup.group_name.like(f'%{search}%'),
                    PlayerGroup.description.like(f'%{search}%')
                )
            )
        
        # 分页
        pagination = query.order_by(PlayerGroup.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 构建返回数据
        groups_data = []
        for group in pagination.items:
            # 获取分组下的玩家
            players = Person.query.filter_by(
                player_group_id=group.id, 
                deleted_at=None
            ).all()
            
            groups_data.append({
                'id': group.id,
                'group_name': group.group_name,
                'description': group.description or '',
                'player_count': len(players),
                'players': [{'id': p.id, 'name': p.name, 'god': p.god, 'job': p.job} for p in players],
                'created_at': group.created_at.strftime('%Y-%m-%d %H:%M:%S') if group.created_at else None,
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'groups': groups_data,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'total_pages': pagination.pages,
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取分组列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取分组列表失败: {str(e)}'
        }), 500


@api_player_group_bp.route('/add', methods=['POST'])
@token_required
def api_player_group_add():
    """添加玩家分组"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': '未接收到数据'
            }), 400
        
        # 验证必填字段
        if not data.get('group_name'):
            return jsonify({
                'status': 'error',
                'message': '分组名称不能为空'
            }), 400
        
        # 创建分组
        group = PlayerGroup(
            group_name=data['group_name'],
            description=data.get('description', ''),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            create_by=1  # 这里应该是当前登录用户的ID
        )
        
        db.session.add(group)
        db.session.flush()  # 获取新插入的ID
        
        # 处理玩家ID列表
        player_ids = data.get('player_ids', [])
        if player_ids:
            for player_id in player_ids:
                player = Person.query.get(player_id)
                if player and player.deleted_at is None:
                    player.player_group_id = group.id
                    player.updated_at = datetime.now()
                    player.update_by = 1
        
        db.session.commit()
        
        logger.info(f"添加分组成功: {group.group_name}")
        
        return jsonify({
            'status': 'success',
            'message': '添加成功',
            'data': {
                'id': group.id,
                'group_name': group.group_name
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"添加分组失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'添加失败: {str(e)}'
        }), 500


@api_player_group_bp.route('/edit/<int:id>', methods=['PUT'])
@token_required
def api_player_group_edit(id):
    """编辑玩家分组"""
    try:
        group = PlayerGroup.query.get(id)
        
        if not group:
            return jsonify({
                'status': 'error',
                'message': '分组不存在'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': '未接收到数据'
            }), 400
        
        # 验证必填字段
        if not data.get('group_name'):
            return jsonify({
                'status': 'error',
                'message': '分组名称不能为空'
            }), 400
        
        # 更新分组信息
        group.group_name = data['group_name']
        group.description = data.get('description', '')
        group.updated_at = datetime.now()
        group.update_by = 1
        
        # 清除之前所有指向这个分组的关联
        old_players = Person.query.filter_by(player_group_id=id, deleted_at=None).all()
        for player in old_players:
            player.player_group_id = None
            player.updated_at = datetime.now()
            player.update_by = 1
        
        # 处理新的玩家ID列表
        player_ids = data.get('player_ids', [])
        if player_ids:
            for player_id in player_ids:
                player = Person.query.get(player_id)
                if player and player.deleted_at is None:
                    player.player_group_id = id
                    player.updated_at = datetime.now()
                    player.update_by = 1
        
        db.session.commit()
        
        logger.info(f"更新分组成功: {group.group_name}")
        
        return jsonify({
            'status': 'success',
            'message': '更新成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新分组失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'更新失败: {str(e)}'
        }), 500


@api_player_group_bp.route('/delete/<int:id>', methods=['DELETE'])
@token_required
def api_player_group_delete(id):
    """删除玩家分组"""
    try:
        group = PlayerGroup.query.get(id)
        
        if not group:
            return jsonify({
                'status': 'error',
                'message': '分组不存在'
            }), 404
        
        # 解除所有玩家与此分组的关联
        players = Person.query.filter_by(player_group_id=id, deleted_at=None).all()
        for player in players:
            player.player_group_id = None
            player.updated_at = datetime.now()
            player.update_by = 1
        
        # 删除分组
        db.session.delete(group)
        db.session.commit()
        
        logger.info(f"删除分组成功: {group.group_name}")
        
        return jsonify({
            'status': 'success',
            'message': '删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除分组失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'删除失败: {str(e)}'
        }), 500


@api_player_group_bp.route('/detail/<int:id>', methods=['GET'])
@token_required
def api_player_group_detail(id):
    """获取分组详情"""
    try:
        group = PlayerGroup.query.get(id)
        
        if not group:
            return jsonify({
                'status': 'error',
                'message': '分组不存在'
            }), 404
        
        # 获取分组下的玩家
        players = Person.query.filter_by(
            player_group_id=id, 
            deleted_at=None
        ).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'id': group.id,
                'group_name': group.group_name,
                'description': group.description or '',
                'players': [{
                    'id': p.id,
                    'name': p.name,
                    'god': p.god,
                    'union_name': p.union_name,
                    'job': p.job,
                    'level': p.level
                } for p in players],
                'created_at': group.created_at.strftime('%Y-%m-%d %H:%M:%S') if group.created_at else None,
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取分组详情失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取分组详情失败: {str(e)}'
        }), 500


@api_player_group_bp.route('/available-players', methods=['GET'])
@token_required
def api_available_players():
    """获取可用的玩家列表（未分组的玩家）"""
    try:
        # 获取所有未分组的玩家
        players = Person.query.filter_by(
            player_group_id=None, 
            deleted_at=None
        ).order_by(Person.name).all()
        
        return jsonify({
            'status': 'success',
            'data': [{
                'id': p.id,
                'name': p.name,
                'god': p.god,
                'union_name': p.union_name,
                'job': p.job,
                'level': p.level
            } for p in players]
        }), 200
        
    except Exception as e:
        logger.error(f"获取可用玩家列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取可用玩家列表失败: {str(e)}'
        }), 500
