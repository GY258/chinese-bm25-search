FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/documents /app/chinese_index /app/logs

# 设置权限
RUN chmod +x start_server.sh

# 暴露端口
EXPOSE 5002

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--workers", "4", "--timeout", "30", "api_server:app"]
