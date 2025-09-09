FROM python:3.9-slim

# 更干净的 Python / pip 行为
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # 运行时可覆盖：gunicorn 参数
    API_HOST=0.0.0.0 \
    API_PORT=5002 \
    WORKERS=2 \
    TIMEOUT=120

WORKDIR /app

# 系统依赖（curl 用于健康检查；gcc/g++ 仅在编译依赖需要时）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc g++ \
 && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件以利用缓存
COPY requirements.txt ./

# 一次性安装所有依赖（若 requirements 已含 gunicorn，可删掉 "gunicorn"）
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 复制应用代码
COPY . .

# 目录准备
RUN mkdir -p /app/documents /app/chinese_index /app/logs \
 && chmod -R 755 /app

# 暴露端口
EXPOSE 5002

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -fsS http://localhost:${API_PORT}/health || exit 1

# 启动命令（WSGI 入口：api_server:app；如为 FastAPI/ASGI 可改用 uvicorn worker）
CMD exec gunicorn \
    --bind ${API_HOST}:${API_PORT} \
    --workers ${WORKERS} \
    --timeout ${TIMEOUT} \
    --graceful-timeout 30 \
    --keep-alive 30 \
    api_server:app
