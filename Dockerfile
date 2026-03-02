# MCP Script Executor Docker Image
# 支持 Python 和 Node.js 脚本执行

FROM python:3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    NODE_VERSION=20

# 安装系统依赖和 Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_VERSION}.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt package.json ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Node.js 依赖
RUN npm install

# 复制应用代码
COPY server.py ./

# 创建执行目录
RUN mkdir -p /app/executions

# 暴露 HTTP 服务端口
EXPOSE 8000

# 默认以 HTTP 模式启动，监听所有网络接口
CMD ["python", "server.py", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
