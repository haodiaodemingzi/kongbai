# 数据库连接库切换指南

## 从PyMySQL切换到mysql-connector-python

我们已经将数据库连接库从PyMySQL切换到了mysql-connector-python，这么做的好处有：

1. 不再需要cryptography包来支持MySQL 8.0的SHA2认证
2. 官方支持的MySQL连接库，更好的兼容性
3. 更好的性能和稳定性

## 切换步骤

1. 安装新的依赖
```bash
pip install mysql-connector-python==8.0.32
```

2. 更新数据库连接字符串
在`.env`文件中，将连接字符串从：
```
DATABASE_URL=mysql+pymysql://用户名:密码@主机/数据库名?charset=utf8mb4&auth_plugin=mysql_native_password
```
更改为：
```
DATABASE_URL=mysql+mysqlconnector://用户名:密码@主机/数据库名?charset=utf8mb4
```

3. 移除不再需要的cryptography包（可选）
```bash
pip uninstall cryptography
```

## 配置文件变更

我们已经更新了以下文件：

1. `requirements.txt` - 更新了依赖列表
2. `app/config.py` - 修改了默认的数据库连接字符串
3. `.env` - 更新了数据库连接配置
4. `.env.example` - 更新了示例环境变量文件
5. `app/utils/file_parser.py` - 更新了数据库连接错误处理
6. `app/routes/battle.py` - 更新了错误处理

## 可能的问题

如果您在切换后遇到以下问题：

1. **找不到模块mysql.connector**
   这表示mysql-connector-python没有正确安装，请重新运行安装命令。

2. **连接失败**
   检查连接字符串是否正确，特别是用户名、密码、主机和数据库名。

3. **权限问题**
   确保数据库用户有足够的权限访问数据库。

4. **编码问题**
   可能需要在连接字符串中显式指定编码，例如添加`charset=utf8mb4`。

## 测试连接

您可以使用以下Python代码测试数据库连接：

```python
import mysql.connector

conn = mysql.connector.connect(
    host="你的主机地址",
    user="用户名",
    password="密码",
    database="数据库名"
)

cursor = conn.cursor()
cursor.execute("SELECT 1")
result = cursor.fetchone()
print(result)
cursor.close()
conn.close()
```

如果输出`(1,)`，则表示连接成功。 