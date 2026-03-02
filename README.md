# Script Executor MCP

一个基于 MCP (Model Context Protocol) 的脚本执行服务，支持在隔离环境中执行 Python 和 Node.js 代码。

## 功能特性

- **多运行时支持**: Python 和 Node.js
- **隔离执行环境**: 每次执行都在独立的 UUID 目录中运行
- **双传输模式**: stdio (IDE 集成) 和 HTTP (远程调用)
- **Docker 支持**: 提供完整的容器化部署方案

## 工具列表

| 工具 | 描述 |
|------|------|
| `execute_script` | 执行脚本代码，支持 `python` 和 `node` 运行时 |

### execute_script 参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `code` | string | 必填 | 要执行的脚本代码 |
| `runtime` | string | `"python"` | 运行时环境：`python` 或 `node` |
| `timeout` | int | `30` | 执行超时时间（秒） |

### 返回结果

执行结果为 JSON 格式：

```json
{
  "success": true,
  "execution_id": "uuid-string",
  "execution_dir": "/path/to/executions/uuid",
  "stdout": "输出内容",
  "stderr": null,
  "return_code": 0,
  "error": null,
  "files": [
    {"name": "script.py", "type": "file", "size": 123}
  ]
}
```

## 资源

| 资源 URI | 描述 |
|----------|------|
| `file://{path}` | 读取指定路径的文件内容 |

## 提示词模板

| 提示词 | 参数 | 描述 |
|--------|------|------|
| `python_script_template` | `task` | 生成 Python 脚本编写提示 |
| `node_script_template` | `task` | 生成 Node.js 脚本编写提示 |

## 安装

### 前置条件

- Python 3.10+
- Node.js 18+（可选，执行 Node.js 脚本时需要）

### 安装依赖

```bash
pip install -r requirements.txt
```

如需执行 Node.js 脚本并使用项目中的 npm 包：

```bash
npm install
```

## 启动服务

### stdio 模式（Cursor/IDE 集成）

```bash
python server.py
```

### HTTP 模式（远程调用）

```bash
# 默认配置 (127.0.0.1:8000/mcp)
python server.py --transport http

# 指定端口
python server.py --transport http --port 3000

# 监听所有接口（允许远程访问）
python server.py --transport http --host 0.0.0.0 --port 8000

# 自定义路径
python server.py --transport http --path /api/mcp
```

### 命令行参数

| 参数 | 简写 | 默认值 | 描述 |
|------|------|--------|------|
| `--transport` | `-t` | `stdio` | 传输方式：`stdio` 或 `http` |
| `--host` | | `127.0.0.1` | HTTP 服务监听地址 |
| `--port` | `-p` | `8000` | HTTP 服务端口 |
| `--path` | | `/mcp` | HTTP 服务路径 |

## Cursor 配置

在 Cursor 设置中添加 MCP 服务器（设置 > MCP）：

```json
{
  "mcpServers": {
    "script-executor": {
      "command": "python",
      "args": ["d:/go-project/exec-script-mcp/server.py"],
      "env": {}
    }
  }
}
```

使用 uv 运行：

```json
{
  "mcpServers": {
    "script-executor": {
      "command": "uv",
      "args": ["run", "d:/go-project/exec-script-mcp/server.py"],
      "env": {}
    }
  }
}
```

## 使用示例

### 执行 Python 代码

```python
execute_script(
    code="print('Hello, World!')",
    runtime="python"
)
```

### 执行 Node.js 代码

```python
execute_script(
    code="console.log('Hello from Node.js!')",
    runtime="node"
)
```

### 生成并保存文件

脚本可以在执行目录中创建文件，执行完成后可通过 `files` 字段查看生成的文件列表：

```python
execute_script(
    code="""
import json
data = {'name': 'test', 'value': 123}
with open('output.json', 'w') as f:
    json.dump(data, f, indent=2)
print('文件已保存')
""",
    runtime="python"
)
```

## Docker 部署

### 使用 Docker Compose

```bash
docker compose up -d
```

服务将在 `http://localhost:8000/mcp` 上启动。

### 手动构建运行

```bash
# 构建镜像
docker build -t mcp-script-executor .

# 运行容器
docker run -d -p 8000:8000 mcp-script-executor
```

### 持久化执行目录

docker-compose.yml 默认将 `./executions` 目录挂载到容器，用于保留执行历史和生成的文件。

## HTTP API 调用

### 列出可用工具

```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### 执行脚本

```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_script",
      "arguments": {"code": "print(1+1)", "runtime": "python"}
    },
    "id": 2
  }'
```

### Python 客户端

```python
import requests

response = requests.post("http://127.0.0.1:8000/mcp", json={
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "execute_script",
        "arguments": {
            "code": "console.log(2 + 2)",
            "runtime": "node"
        }
    },
    "id": 1
})
print(response.json())
```

## 项目结构

```
exec-script-mcp/
├── server.py           # MCP 服务主程序
├── requirements.txt    # Python 依赖
├── package.json        # Node.js 依赖
├── Dockerfile          # Docker 镜像定义
├── docker-compose.yml  # Docker Compose 配置
└── executions/         # 脚本执行目录（自动创建）
```

## 安全注意事项

- 此服务可执行任意代码，请在受信任的环境中运行
- HTTP 模式默认只监听 `127.0.0.1`，如需远程访问请配置防火墙和认证
- 每次执行都在独立的 UUID 目录中进行，提供基本的执行隔离

## 许可证

MIT License
