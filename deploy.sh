#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 配置变量
DOMAIN="bigmang.xyz"  # 替换为你的域名
EMAIL="haodiaodemingzi@gmail.com"  # 替换为你的邮箱
MYSQL_ROOT_PASSWORD="admin123"  # 替换为你的MySQL root密码
MYSQL_DATABASE="oneapi"
MYSQL_USER="oneapi"
MYSQL_PASSWORD="oneapi123"

# 配置 Docker 日志清理
echo -e "${GREEN}Configuring Docker log rotation...${NC}"
cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# 重启 Docker 服务以应用日志配置
echo -e "${GREEN}Restarting Docker service...${NC}"
systemctl restart docker

# 创建日志清理脚本
echo -e "${GREEN}Creating log cleanup script...${NC}"
cat > cleanup-docker.sh << 'EOF'
#!/bin/bash

# 清理退出的容器
docker container prune -f

# 清理未使用的镜像
docker image prune -f

# 清理未使用的卷
docker volume prune -f

# 清理构建缓存
docker builder prune -f

# 查找并删除大于 100MB 的容器日志文件
find /var/lib/docker/containers/ -type f -name "*.log" -size +100M -exec truncate -s 0 {} \;
EOF

# 设置清理脚本权限
chmod +x cleanup-docker.sh

# 添加定时任务，每天凌晨 3 点执行清理
echo -e "${GREEN}Setting up daily cleanup cron job...${NC}"
(crontab -l 2>/dev/null; echo "0 3 * * * $(pwd)/cleanup-docker.sh >> /var/log/docker-cleanup.log 2>&1") | crontab -

# 创建必要的目录
echo -e "${GREEN}Creating directories...${NC}"
mkdir -p ./data/mysql
mkdir -p ./data/certbot/conf
mkdir -p ./data/certbot/www
mkdir -p ./nginx/conf.d

# 创建 docker-compose.yml
echo -e "${GREEN}Creating docker-compose.yml...${NC}"
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    container_name: battle_stats_web
    restart: always
    environment:
      - FLASK_APP=app
      - FLASK_ENV=production
      - SQLALCHEMY_DATABASE_URI=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@db:3306/${MYSQL_DATABASE}
    ports:
      - "5000:5000"
    depends_on:
      db:
        condition: service_healthy
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  db:
    image: mysql:8.0
    container_name: battle_stats_mysql
    restart: always
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DATABASE}
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - ./data/mysql:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u$$MYSQL_USER", "-p$$MYSQL_PASSWORD"]
      interval: 10s
      timeout: 5s
      retries: 5
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

EOF

# 创建 nginx 配置文件
echo -e "${GREEN}Creating Nginx configuration...${NC}"
cat > ./nginx/conf.d/app.conf << EOF
server {
    listen 80;
    server_name ${DOMAIN};
    server_tokens off;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name ${DOMAIN};
    server_tokens off;

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 20M;

    location / {
        proxy_pass http://web:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 创建 .env 文件
echo -e "${GREEN}Creating .env file...${NC}"
cat > .env << EOF
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
MYSQL_DATABASE=${MYSQL_DATABASE}
MYSQL_USER=${MYSQL_USER}
MYSQL_PASSWORD=${MYSQL_PASSWORD}
DOMAIN=${DOMAIN}
EMAIL=${EMAIL}
EOF

# 初始化 SSL 证书
echo -e "${GREEN}Initializing SSL certificates...${NC}"
docker-compose up -d nginx
docker-compose run --rm certbot certonly --webroot -w /var/www/certbot \
    --email ${EMAIL} --agree-tos --no-eff-email \
    -d ${DOMAIN}

# 重启所有服务
echo -e "${GREEN}Restarting all services...${NC}"
docker-compose down
docker-compose up -d

echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${GREEN}Please make sure to:${NC}"
echo -e "1. Place your SQL dump file in ./data/mysql"
echo -e "2. Update the domain name and email in the script"
echo -e "3. Configure your DNS settings to point to this server"
echo -e "4. Update your firewall rules to allow ports 80 and 443"

# 显示部署状态
echo -e "${GREEN}Checking deployment status...${NC}"
docker-compose ps 
