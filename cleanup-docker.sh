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
