# 战报分析系统

一个用于分析游戏战报的Web应用，使用Python和Flask开发。

## 功能特点

- 上传战报文件并解析
- 分析玩家参与度和表现
- 生成战斗数据统计和报表
- 追踪玩家历史表现

## 技术栈

- **后端**: Python, Flask
- **数据库**: MySQL (通过PyMySQL连接)
- **ORM**: SQLAlchemy
- **前端**: HTML, CSS, JavaScript
- **数据可视化**: Matplotlib

## 安装指南

### 前提条件

- Python 3.8+
- MySQL 8.0+

### 安装步骤

1. 克隆仓库:
   ```
   git clone <仓库地址>
   cd <项目文件夹>
   ```

2. 创建虚拟环境:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. 安装依赖:
   ```
   pip install -r requirements.txt
   ```

4. 配置数据库:
   - 在MySQL中创建数据库
   ```sql
   CREATE DATABASE oneapi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
   - 修改`.env`文件以配置数据库连接

5. 初始化数据库:
   ```
   python init_db.py
   ```

6. 启动应用:
   ```
   python run.py
   ```

## 环境变量配置

创建`.env`文件，包含以下配置:

```
# 应用配置
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# 服务器配置
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@hostname/database?charset=utf8mb4

# 日志配置
LOG_LEVEL=DEBUG
```

## 项目结构

```
├── app/                  # 应用程序代码
│   ├── __init__.py       # 应用程序初始化
│   ├── config.py         # 配置文件
│   ├── models/           # 数据模型
│   ├── routes/           # 路由处理
│   ├── static/           # 静态文件
│   ├── templates/        # HTML模板
│   └── utils/            # 工具函数
├── logs/                 # 日志文件
├── uploads/              # 上传文件目录
├── .env                  # 环境变量配置
├── init_db.py            # 数据库初始化脚本
├── requirements.txt      # 依赖项列表
└── run.py                # 应用程序入口
```

## 数据库说明

系统使用MySQL数据库，通过PyMySQL连接。更多详细信息，请参考[数据库配置说明](README_PYMYSQL.md)。

## 使用指南

1. 打开浏览器访问: `http://localhost:5000`
2. 上传战报文件（支持.txt, .log和.csv格式）
3. 查看生成的分析报告和战斗数据统计

## Docker支持

使用Docker运行应用:

```
docker-compose up -d
```

## 贡献指南

欢迎贡献代码或提交问题报告。请遵循项目的代码风格和贡献指南。

## 许可证

[MIT许可证](LICENSE) 