# MySQL 到 SQLite 迁移指南

为了解决MySQL连接问题，我们将数据库从MySQL切换到了SQLite。SQLite是一个轻量级的数据库，不需要单独的服务器，数据直接存储在一个文件中，非常适合小型应用。

## 迁移步骤

1. **导出MySQL数据到CSV**

```bash
python export_mysql_data.py
```

这将从MySQL导出person表数据到`person_data.csv`文件。

2. **导入数据到SQLite**

```bash
python mysql_to_sqlite.py
```

这将创建一个SQLite数据库文件`app.db`，并将CSV文件中的数据导入到SQLite的person表中。

3. **验证数据导入**

```bash
sqlite3 app.db
sqlite> SELECT COUNT(*) FROM person;
sqlite> .exit
```

## 配置说明

以下文件已经更新为使用SQLite：

1. `app/config.py` - 修改了数据库连接字符串
2. `.env` - 更新了环境变量配置
3. `requirements.txt` - 更新了依赖列表

SQLite数据库文件`app.db`会自动创建在项目根目录下。

## 优缺点比较

**SQLite优点**:
- 无需安装数据库服务器
- 无需配置用户名和密码
- 没有依赖问题
- 部署简单，文件即数据库

**SQLite缺点**:
- 不适合高并发
- 不适合大型数据
- 不支持复杂的事务和存储过程

## 常见问题

1. **数据库文件权限问题**

确保应用有足够的权限读写数据库文件。

```bash
chmod 666 app.db
```

2. **数据库锁定问题**

SQLite在写入时会锁定整个数据库文件，如果出现"database is locked"错误，可以：
- 确保所有连接在操作完成后都被关闭
- 增加连接超时时间
- 减少并发访问

3. **性能问题**

如果应用规模增长导致SQLite性能下降，可考虑：
- 启用SQLite的WAL模式
- 优化查询
- 或考虑迁回到MySQL等服务器型数据库

## 迁回MySQL

如果将来需要迁回MySQL，可以使用SQLite的`.dump`命令导出SQL语句，然后进行适当修改后导入MySQL。 