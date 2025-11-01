-- 为 battle_record 表添加性能优化索引
-- 这些索引将大幅提升战绩查询的速度
-- 注意: 如果索引已存在，执行会报错，这是正常的，脚本会自动跳过

-- 1. 为 win 列添加索引（用于查询击杀记录）
CREATE INDEX idx_battle_record_win ON battle_record(win);

-- 2. 为 lost 列添加索引（用于查询死亡记录）
CREATE INDEX idx_battle_record_lost ON battle_record(lost);

-- 3. 为 publish_at 添加索引（用于时间范围过滤）
CREATE INDEX idx_battle_record_publish_at ON battle_record(publish_at);

-- 4. 组合索引：win + publish_at + deleted_at（优化查询击杀记录时的性能）
CREATE INDEX idx_battle_record_win_date ON battle_record(win, publish_at, deleted_at);

-- 5. 组合索引：lost + publish_at + deleted_at（优化查询死亡记录时的性能）
CREATE INDEX idx_battle_record_lost_date ON battle_record(lost, publish_at, deleted_at);

