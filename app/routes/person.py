from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.models.player import Person
from app.extensions import db
from sqlalchemy import or_, and_
from datetime import datetime

bp = Blueprint('person', __name__)

@bp.route('/person/list')
def person_list():
    """人员列表页面"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    god = request.args.get('god', '')
    
    per_page = 10
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
    
    # 应用所有条件
    if conditions:
        query = query.filter(and_(*conditions))
    
    pagination = query.order_by(Person.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('person/list.html', 
                         persons=pagination.items, 
                         pagination=pagination,
                         search=search,
                         god=god)

@bp.route('/person/add', methods=['GET', 'POST'])
def person_add():
    """添加人员"""
    if request.method == 'GET':
        return render_template('person/add.html')

    # POST请求处理
    try:
        x = request.data
        data = json.loads(x)

        print("Received data:", data)  # 打印接收到的数据
        
        if not data:
            return jsonify({'code': 1, 'message': '未接收到数据'})
        
        # 验证必填字段
        required_fields = ['name', 'god', 'union_name', 'job', 'level']
        if data.get('name') is None:
            return jsonify({'code': 1, 'message': '游戏id不能为空'})
        if data.get('god') is None:
            return jsonify({'code': 1, 'message': '主神不能为空'})
        
        # 确保level是整数
        try:
            level = int(data.get('level'))
        except (TypeError, ValueError):
            return jsonify({'code': 1, 'message': '主神等级必须是数字'})
            
        person = Person(
            name=data['name'],  # 使用直接访问而不是get
            god=data['god'],
            union_name=data['union_name'],
            job=data['job'],
            level=level,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            create_by=1
        )
        
        print("Creating person:", {  # 打印要创建的数据
            'name': person.name,
            'god': person.god,
            'union_name': person.union_name,
            'job': person.job,
            'level': person.level
        })
        
        db.session.add(person)
        db.session.commit()
        return jsonify({'code': 0, 'message': '添加成功'})
    except Exception as e:
        db.session.rollback()
        print("Error:", str(e))  # 打印错误信息
        return jsonify({'code': 1, 'message': f'添加失败：{str(e)}'})

@bp.route('/person/edit/<int:id>', methods=['GET', 'POST'])
def person_edit(id):
    """编辑人员"""
    person = Person.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            data = request.get_json()  # 改为获取JSON数据
            person.name = data.get('name')
            person.god = data.get('god')
            person.union_name = data.get('union_name')
            person.job = data.get('job')
            person.level = data.get('level')
            person.updated_at = datetime.now()
            person.update_by = 1  # 这里应该是当前登录用户的ID
            
            db.session.commit()
            return jsonify({'code': 0, 'message': '更新成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'code': 1, 'message': f'更新失败：{str(e)}'})
    
    return render_template('person/edit.html', person=person)

@bp.route('/person/delete/<int:id>', methods=['POST'])
def person_delete(id):
    """删除人员（软删除）"""
    person = Person.query.get_or_404(id)
    try:
        person.deleted_at = datetime.now()  # 软删除
        db.session.commit()
        return jsonify({'code': 0, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'message': f'删除失败：{str(e)}'}) 