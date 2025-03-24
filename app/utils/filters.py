def chart_data(factions, values):
    """
    将数据转换为ECharts图表所需的格式
    
    Args:
        factions: 势力名称列表
        values: 对应的数值列表
        
    Returns:
        转换后的数据列表
    """
    return [{'value': val, 'name': faction} for faction, val in zip(factions, values)] 