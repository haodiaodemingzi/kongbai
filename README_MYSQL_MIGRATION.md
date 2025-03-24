# SQLite 到 MySQL 迁移指南

本文档介绍如何将应用从SQLite数据库迁回MySQL数据库。

## 已完成的配置更改

以下文件已经更新为使用MySQL (PyMySQL):

1. **app/config.py**
   - 更新了数据库连接字符串为MySQL连接
   - 配置使用了标准的PyMySQL连接格式

2. **.env**
   - 更新环境变量，使用MySQL连接字符串

3. **requirements.txt**
   - 添加了pymysql和cryptography依赖

4. **init_db.py**
   - 更新为使用MySQL初始化数据库

## 迁移步骤

如果您有SQLite中的数据需要迁移到MySQL，请按照以下步骤操作：

### 前提条件

1. 已安装MySQL服务器并创建数据库
   ```sql
   CREATE DATABASE oneapi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. 已安装所需的依赖
   ```bash
   pip install -r requirements.txt
   ```

### 使用mysqldump导出SQLite数据到MySQL

1. **导出SQLite数据到SQL文件**:
   ```bash
   sqlite3 app.db .dump > dump.sql
   ```

2. **修改SQL文件使其兼容MySQL格式**:
   将SQLite特有的语法转换为MySQL语法，特别需要修改：
   - 数据类型（例如，将BLOB改为LONGBLOB）
   - 自增语法（将AUTOINCREMENT改为AUTO_INCREMENT）
   - 约束语法差异

3. **导入到MySQL**:
   ```bash
   mysql -u用户名 -p密码 oneapi < modified_dump.sql
   ```

### 使用Python脚本迁移

如果数据量不大，使用Python脚本可能更简单：

1. 安装所需工具
   ```bash
   pip install sqlite3 pymysql pandas
   ```

2. 创建迁移脚本`sqlite_to_mysql.py`:
   ```python
   import sqlite3
   import pymysql
   import pandas as pd
   
   # 连接SQLite
   sqlite_conn = sqlite3.connect('app.db')
   
   # 连接MySQL
   mysql_conn = pymysql.connect(
       host='localhost',
       user='用户名',
       password='密码',
       database='oneapi',
       charset='utf8mb4'
   )
   
   # 获取SQLite表列表
   tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", sqlite_conn)
   
   # 迁移每个表的数据
   for table_name in tables['name']:
       try:
           # 读取SQLite表数据
           df = pd.read_sql(f"SELECT * FROM {table_name}", sqlite_conn)
           
           if len(df) > 0:
               # 将数据写入MySQL表
               cursor = mysql_conn.cursor()
               
               # 先清空表
               cursor.execute(f"TRUNCATE TABLE {table_name}")
               
               # 向MySQL写入数据
               placeholders = ', '.join(['%s'] * len(df.columns))
               columns = ', '.join(df.columns)
               
               for _, row in df.iterrows():
                   values = tuple(row)
                   cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
               
               mysql_conn.commit()
               print(f"表 {table_name} 迁移成功: {len(df)} 条记录")
       except Exception as e:
           print(f"迁移表 {table_name} 时出错: {e}")
   
   # 关闭连接
   sqlite_conn.close()
   mysql_conn.close()
   ```

3. 运行迁移脚本
   ```bash
   python sqlite_to_mysql.py
   ```

## 验证迁移

迁移完成后，执行以下步骤验证：

1. 检查MySQL中的表和记录数
   ```sql
   SHOW TABLES;
   SELECT COUNT(*) FROM person;
   SELECT COUNT(*) FROM battle_record;
   SELECT COUNT(*) FROM battle_detail;
   SELECT COUNT(*) FROM blessing;
   ```

2. 启动应用，确保所有功能正常工作

## 故障排除

1. **连接错误**: 检查MySQL服务器是否运行，以及连接参数是否正确

2. **认证错误**: 
   - 检查MySQL用户认证插件
   - 如果遇到caching_sha2_password错误，请安装cryptography包
   - 或者在MySQL中将用户认证改为mysql_native_password

3. **数据类型错误**:
   - SQLite和MySQL的数据类型存在差异，可能需要手动修正某些列的数据类型

4. **字符编码问题**:
   - 确保使用utf8mb4字符集，支持完整的Unicode字符

## 回滚方案

如果需要从MySQL回到SQLite，只需：

1. 将配置文件改回SQLite设置
2. 使用类似的方法导出MySQL数据并导入到SQLite

## 参考资料

- [PyMySQL文档](https://pymysql.readthedocs.io/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/en/14/dialects/mysql.html)
- [MySQL 8.0认证插件文档](https://dev.mysql.com/doc/refman/8.0/en/upgrading-from-previous-series.html#upgrade-caching-sha2-password) 