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
    
    # 按日期分割文本，支持"号"和"日"两种格式
    date_blocks = re.split(r'\n(?=\d+月\d+(?:日|号))', text)
    results = []
    
    for block in date_blocks:
        if not block.strip():
            continue
            
        # 提取日期，支持"号"和"日"两种格式
        date_match = re.search(r'(\d+)月(\d+)(?:日|号)', block)
        if not date_match:
            continue
            
        month, day = map(int, date_match.groups())
        date = datetime(2024, month, day).date()
        
        # 提取出灯信息
        light_info = re.search(r'出灯：(.+?)(?=\n|$)', block)
        light_people = []
        light_counts = {}  # 存储每个人的出灯数量
        
        if light_info:
            light_text = light_info.group(1)
            light_entries = [entry.strip() for entry in re.split(r'[，,]', light_text)]
            
            for entry in light_entries:
                if not entry:
                    continue
                    
                # 提取名字和数量
                count_match = re.search(r'(.+?)(\d+)$', entry)
                if count_match:
                    name = count_match.group(1).strip()
                    name = name.split('（')[0].strip()  # 移除括号内容
                    name = re.sub(r'\s+', '', name)     # 移除空白字符
                    count = int(count_match.group(2))
                    light_people.append(name)
                    light_counts[name] = count
                else:
                    name = entry.split('（')[0].strip()  # 移除括号内容
                    name = re.sub(r'\s+', '', name)     # 移除空白字符
                    light_people.append(name)
                    # 如果名字已经在light_counts中，累加次数
                    if name in light_counts:
                        light_counts[name] += 1
                    else:
                        light_counts[name] = 1
        
        # 提取悬赏信息
        bounty_info = re.search(r'悬赏：(.+?)(?=\n|$)', block)
        bounty_people = []
        bounty_counts = {}  # 存储每个人的悬赏数量
        
        if bounty_info:
            bounty_text = bounty_info.group(1)
            bounty_entries = [entry.strip() for entry in re.split(r'[，,]', bounty_text)]
            
            for entry in bounty_entries:
                if not entry:
                    continue
                    
                # 提取名字和数量
                count_match = re.search(r'(.+?)(\d+)$', entry)
                if count_match:
                    name = count_match.group(1).strip()
                    name = name.split('（')[0].strip()  # 移除括号内容
                    name = re.sub(r'\s+', '', name)     # 移除空白字符
                    count = int(count_match.group(2))
                    bounty_people.append(name)
                    bounty_counts[name] = count
                else:
                    name = entry.split('（')[0].strip()  # 移除括号内容
                    name = re.sub(r'\s+', '', name)     # 移除空白字符
                    bounty_people.append(name)
                    # 如果名字已经在bounty_counts中，累加次数
                    if name in bounty_counts:
                        bounty_counts[name] += 1
                    else:
                        bounty_counts[name] = 1
        
        # 提取参与人员，支持"主神："和"主神人员："两种格式
        people_text = re.search(r'主神(?:人员)?[：:](.+?)(?=出灯|悬赏|\n|$)', block)
        if not people_text:
            continue
            
        people = []
        for person in re.split(r'[，,]', people_text.group(1)):
            person = person.strip()
            if not person:  # 跳过空名字
                continue
            is_healer = '活' in person
            # 更严格的名字提取逻辑
            name = re.sub(r'（.*?）', '', person).strip()  # 移除括号内容
            name = re.sub(r'\s+', '', name)  # 移除所有空白字符
            if not name:  # 跳过处理后的空名字
                continue
                
            base_reward = 1000000000  # 10亿
            healer_bonus = 1000000000 if is_healer else 0
            
            # 考虑出灯数量
            light_bonus = 0
            if name in light_people:
                light_count = light_counts.get(name, 1)  # 默认为1个
                light_bonus = 1000000000 * light_count
                
            # 考虑悬赏数量
            bounty_bonus = 0
            if name in bounty_people:
                bounty_count = bounty_counts.get(name, 1)  # 默认为1个
                bounty_bonus = 1000000000 * bounty_count
                
            total_reward = base_reward + healer_bonus + light_bonus + bounty_bonus
            
            people.append({
                'name': name,
                'is_healer': is_healer,
                'has_light': name in light_people,
                'light_count': light_counts.get(name, 0),
                'has_bounty': name in bounty_people,
                'bounty_count': bounty_counts.get(name, 0),
                'base_reward': base_reward,
                'healer_bonus': healer_bonus,
                'light_bonus': light_bonus,
                'bounty_bonus': bounty_bonus,
                'total_reward': total_reward
            })
        
        results.append({
            'date': date.strftime('%Y-%m-%d'),
            'people': people
        })
    
    return jsonify({'success': True, 'results': results}) 