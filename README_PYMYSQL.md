# PyMySQL数据库配置说明

本应用使用PyMySQL连接MySQL数据库，以下是相关配置和使用说明。

## 数据库配置

数据库连接配置在以下文件中：

1. `app/config.py` - 主要配置文件
2. `.env` - 环境变量配置

### 配置详情

默认配置使用标准PyMySQL连接字符串：

```python
# app/config.py
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://cheetah:cheetah@192.168.123.144/oneapi?charset=utf8mb4'
```

环境变量配置示例：

```
# .env
DATABASE_URL=mysql+pymysql://username:password@hostname/database?charset=utf8mb4
```

## 依赖项

使用PyMySQL需要安装以下依赖：

```
pymysql==1.0.3
cryptography==40.0.2  # 如果使用SHA2密码认证则需要
```

这些依赖已添加到`requirements.txt`文件中。

## 认证方式说明

MySQL 8.0默认使用`caching_sha2_password`认证插件，需要`cryptography`包支持。如果您遇到认证问题，可以使用以下方法：

在MySQL服务器上更改用户认证方式：
```sql
ALTER USER 'username'@'hostname' IDENTIFIED WITH mysql_native_password BY 'password';
FLUSH PRIVILEGES;
```

## 数据库初始化

首次使用时，请确保MySQL服务器已启动，并且已创建相应的数据库：

```sql
CREATE DATABASE oneapi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后可以运行初始化脚本：

```
python init_db.py
```

## 常见问题

1. **连接错误**：如果出现连接错误，请检查MySQL服务器是否运行，以及用户名、密码和主机名是否正确。

2. **认证错误**：如果出现`caching_sha2_password`相关错误，请安装`cryptography`包或使用上述认证方法切换到`mysql_native_password`。

3. **编码问题**：确保使用`charset=utf8mb4`参数以支持完整的Unicode字符集。 