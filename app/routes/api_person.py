#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
人员管理 API 路由
"""

from flask import Blueprint, request, jsonify
from app.models.player import Person
from app.extensions import db
from sqlalchemy import or_, and_, distinct
from datetime import datetime
from app.utils.jwt_auth import token_required
from app.utils.logger import get_logger

logger = get_logger()

api_person_bp = Blueprint('api_person', __name__)


@api_person_bp.route('/list', methods=['GET'])
@token_required
def api_person_list():
    """获取人员列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        god = request.args.get('god', '')
        job = request.args.get('job', '')
        
        query = Person.query.filter_by(deleted_at=None)
        
        # 构建搜索条件
        conditions = []
        if search:
            conditions.append(
                or_(
                    Person.name.like(f'%{search}%'),
                    Person.union_name.like(f'%{search}%'),
                    Person.job.like(f'%{search}%')
                )
            )
        
        # 添加主神筛选条件
        if god:
            conditions.append(Person.god == god)
        
        # 添加职业筛选条件
        if job:
            conditions.append(Person.job == job)
        
        # 应用所有条件
        if conditions:
            query = query.filter(and_(*conditions))
        
        # 分页查询
        pagination = query.order_by(Person.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 获取所有不重复的职业用于筛选器
        jobs_query = db.session.query(distinct(Person.job)).filter(
            Person.deleted_at.is_(None), 
            Person.job.isnot(None)
        ).order_by(Person.job)
        available_jobs = [j[0] for j in jobs_query.all() if j[0]]
        
        # 构建返回数据
        persons = []
        for person in pagination.items:
            persons.append({
                'id': person.id,
                'name': person.name,
                'god': person.god,
                'union_name': person.union_name,
                'job': person.job,
                'level': person.level,
                'created_at': person.created_at.strftime('%Y-%m-%d %H:%M:%S') if person.created_at else None,
                'updated_at': person.updated_at.strftime('%Y-%m-%d %H:%M:%S') if person.updated_at else None,
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'persons': persons,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages,
                'available_jobs': available_jobs
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取人员列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取人员列表失败: {str(e)}'
        }), 500


@api_person_bp.route('/add', methods=['POST'])
@token_required
def api_person_add():
    """添加人员"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': '未接收到数据'
            }), 400
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({
                'status': 'error',
                'message': '游戏ID不能为空'
            }), 400
            
        if not data.get('god'):
            return jsonify({
                'status': 'error',
                'message': '主神不能为空'
            }), 400
        
        # 确保level是字符串
        level = str(data.get('level', ''))
        
        person = Person(
            name=data['name'],
            god=data['god'],
            union_name=data.get('union_name', ''),
            job=data.get('job', ''),
            level=level,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            create_by=1  # 这里应该是当前登录用户的ID
        )
        
        db.session.add(person)
        db.session.commit()
        
        logger.info(f"添加人员成功: {person.name}")
        
        return jsonify({
            'status': 'success',
            'message': '添加成功',
            'data': {
                'id': person.id,
                'name': person.name
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"添加人员失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'添加失败: {str(e)}'
        }), 500


@api_person_bp.route('/edit/<int:id>', methods=['PUT'])
@token_required
def api_person_edit(id):
    """编辑人员"""
    try:
        person = Person.query.get(id)
        
        if not person or person.deleted_at:
            return jsonify({
                'status': 'error',
                'message': '人员不存在'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': '未接收到数据'
            }), 400
        
        # 更新字段
        if 'name' in data:
            person.name = data['name']
        if 'god' in data:
            person.god = data['god']
        if 'union_name' in data:
            person.union_name = data['union_name']
        if 'job' in data:
            person.job = data['job']
        if 'level' in data:
            person.level = str(data['level'])
        
        person.updated_at = datetime.now()
        person.update_by = 1  # 这里应该是当前登录用户的ID
        
        db.session.commit()
        
        logger.info(f"更新人员成功: {person.name}")
        
        return jsonify({
            'status': 'success',
            'message': '更新成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新人员失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'更新失败: {str(e)}'
        }), 500


@api_person_bp.route('/delete/<int:id>', methods=['DELETE'])
@token_required
def api_person_delete(id):
    """删除人员（软删除）"""
    try:
        person = Person.query.get(id)
        
        if not person or person.deleted_at:
            return jsonify({
                'status': 'error',
                'message': '人员不存在'
            }), 404
        
        person.deleted_at = datetime.now()
        db.session.commit()
        
        logger.info(f"删除人员成功: {person.name}")
        
        return jsonify({
            'status': 'success',
            'message': '删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除人员失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'删除失败: {str(e)}'
        }), 500


@api_person_bp.route('/detail/<int:id>', methods=['GET'])
@token_required
def api_person_detail(id):
    """获取人员详情"""
    try:
        person = Person.query.get(id)
        
        if not person or person.deleted_at:
            return jsonify({
                'status': 'error',
                'message': '人员不存在'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'id': person.id,
                'name': person.name,
                'god': person.god,
                'union_name': person.union_name,
                'job': person.job,
                'level': person.level,
                'created_at': person.created_at.strftime('%Y-%m-%d %H:%M:%S') if person.created_at else None,
                'updated_at': person.updated_at.strftime('%Y-%m-%d %H:%M:%S') if person.updated_at else None,
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取人员详情失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'获取人员详情失败: {str(e)}'
        }), 500
