FROM python:3.9-slim

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    python3-dev \
    default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
COPY . .

# 创建上传和日志目录
RUN mkdir -p uploads
RUN mkdir -p logs

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"] 