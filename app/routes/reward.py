from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
import re

bp = Blueprint('reward', __name__)

@bp.route('/rewards')
def rewards():
    """显示奖励记录页面"""
    return render_template('rewards.html')

@bp.route('/api/rewards/parse', methods=['POST'])
def parse_rewards():
    """解析奖励文本"""
    text = request.json.get('text', '')
    if not text:
        return jsonify({'error': '请提供文本内容'}), 400
    
    # 按日期分割文本
    date_blocks = re.split(r'\n(?=\d+月\d+日)', text)
    results = []
    
    for block in date_blocks:
        if not block.strip():
            continue
            
        # 提取日期
        date_match = re.search(r'(\d+)月(\d+)日', block)
        if not date_match:
            continue
            
        month, day = map(int, date_match.groups())
        date = datetime(2024, month, day).date()
        
        # 提取出灯信息
        light_info = re.search(r'出灯：(.+?)(?=\n|$)', block)
        light_people = []
        if light_info:
            light_text = light_info.group(1)
            light_people = [name.strip() for name in re.split(r'[，,]', light_text)]
            light_people = [name.split('（')[0] for name in light_people]  # 移除括号内容
        
        # 提取参与人员
        people_text = re.search(r'主神[：:](.+?)(?=出灯|\n|$)', block)
        if not people_text:
            continue
            
        people = []
        for person in re.split(r'[，,]', people_text.group(1)):
            person = person.strip()
            is_healer = '活' in person
            name = person.split('（')[0] if '（' in person else person
            base_reward = 1000000000  # 10亿
            healer_bonus = 1000000000 if is_healer else 0
            light_bonus = 1000000000 if name in light_people else 0
            total_reward = base_reward + healer_bonus + light_bonus
            
            people.append({
                'name': name,
                'is_healer': is_healer,
                'has_light': name in light_people,
                'base_reward': base_reward,
                'healer_bonus': healer_bonus,
                'light_bonus': light_bonus,
                'total_reward': total_reward
            })
        
        results.append({
            'date': date.strftime('%Y-%m-%d'),
            'people': people
        })
    
    return jsonify({'success': True, 'results': results}) 