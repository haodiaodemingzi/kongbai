from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.models.player import Person, PlayerGroup
from app.extensions import db
from sqlalchemy import or_, and_
from datetime import datetime
import json

bp = Blueprint('player_group', __name__)

@bp.route('/player_group/list')
def player_group_list():
    """玩家分组列表页面"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    per_page = 10
    query = PlayerGroup.query
    
    # 构建搜索条件
    if search:
        query = query.filter(
            or_(
                PlayerGroup.group_name.like(f'%{search}%'),
                PlayerGroup.description.like(f'%{search}%')
            )
        )
    
    pagination = query.order_by(PlayerGroup.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 获取每个分组下的玩家列表
    groups_with_players = []
    for group in pagination.items:
        players = Person.query.filter_by(player_group_id=group.id, deleted_at=None).all()
        groups_with_players.append({
            'group': group,
            'players': players
        })
    
    return render_template('player_group/list.html', 
                         groups=groups_with_players, 
                         pagination=pagination,
                         search=search)

@bp.route('/player_group/add', methods=['GET', 'POST'])
def player_group_add():
    """添加玩家分组"""
    if request.method == 'GET':
        # 获取所有未分组的玩家
        unassigned_players = Person.query.filter_by(player_group_id=None, deleted_at=None).all()
        return render_template('player_group/add.html', unassigned_players=unassigned_players)

    # POST请求处理
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'code': 1, 'message': '未接收到数据'})
        
        # 验证必填字段
        if not data.get('group_name'):
            return jsonify({'code': 1, 'message': '分组名称不能为空'})
        
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
                if player:
                    player.player_group_id = group.id
                    player.updated_at = datetime.now()
                    player.update_by = 1  # 这里应该是当前登录用户的ID
        
        db.session.commit()
        return jsonify({'code': 0, 'message': '添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'message': f'添加失败：{str(e)}'})

@bp.route('/player_group/edit/<int:id>', methods=['GET', 'POST'])
def player_group_edit(id):
    """编辑玩家分组"""
    # 获取要编辑的分组
    group = PlayerGroup.query.get_or_404(id)
    
    if request.method == 'GET':
        # 获取已分配到此分组的玩家
        assigned_players = Person.query.filter_by(player_group_id=id, deleted_at=None).all()
        
        # 获取所有未分组的玩家
        unassigned_players = Person.query.filter_by(player_group_id=None, deleted_at=None).all()
        
        return render_template('player_group/edit.html', 
                             group=group,
                             assigned_players=assigned_players,
                             unassigned_players=unassigned_players)
    
    # POST请求处理
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'code': 1, 'message': '未接收到数据'})
        
        # 验证必填字段
        if not data.get('group_name'):
            return jsonify({'code': 1, 'message': '分组名称不能为空'})
        
        # 更新分组信息
        group.group_name = data['group_name']
        group.description = data.get('description', '')
        group.updated_at = datetime.now()
        group.update_by = 1  # 这里应该是当前登录用户的ID
        
        # 清除之前所有指向这个分组的关联
        old_players = Person.query.filter_by(player_group_id=id, deleted_at=None).all()
        for player in old_players:
            player.player_group_id = None
            player.updated_at = datetime.now()
            player.update_by = 1  # 这里应该是当前登录用户的ID
        
        # 处理新的玩家ID列表
        player_ids = data.get('player_ids', [])
        if player_ids:
            for player_id in player_ids:
                player = Person.query.get(player_id)
                if player and player.deleted_at is None:
                    player.player_group_id = id
                    player.updated_at = datetime.now()
                    player.update_by = 1  # 这里应该是当前登录用户的ID
        
        db.session.commit()
        return jsonify({'code': 0, 'message': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'message': f'更新失败：{str(e)}'})

@bp.route('/player_group/delete/<int:id>', methods=['POST'])
def player_group_delete(id):
    """删除玩家分组"""
    try:
        # 获取要删除的分组
        group = PlayerGroup.query.get_or_404(id)
        
        # 解除所有玩家与此分组的关联
        players = Person.query.filter_by(player_group_id=id, deleted_at=None).all()
        for player in players:
            player.player_group_id = None
            player.updated_at = datetime.now()
            player.update_by = 1  # 这里应该是当前登录用户的ID
        
        # 删除分组
        db.session.delete(group)
        db.session.commit()
        
        return jsonify({'code': 0, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'message': f'删除失败：{str(e)}'})