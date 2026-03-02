# Script Executor MCP 服务

一个基于 Python 的 MCP (Model Context Protocol) 服务，提供多语言脚本执行和文件操作功能。

## 功能特性

### 支持的传输方式

| 传输方式 | 描述 | 适用场景 |
|---------|------|---------|
| `stdio` | 标准输入输出 | Cursor/IDE 集成（默认） |
| `streamable-http` | HTTP 服务 | 远程调用、Web 集成、多客户端 |

### 支持的运行时

- **Python** - 使用系统 Python 解释器
- **Node.js** - 使用系统 Node.js 运行时

### 工具 (Tools)

| 工具名称 | 描述 |
|---------|------|
| `execute_script` | 统一脚本执行接口（支持选择 python/node） |
| `execute_python` | 执行 Python 代码 |
| `execute_node` | 执行 Node.js 代码 |
| `execute_shell` | 执行 Shell/PowerShell 命令 |
| `read_file` | 读取文件内容 |
| `write_file` | 写入文件内容 |
| `list_directory` | 列出目录内容 |
| `get_system_info` | 获取系统信息（含 Python/Node.js 版本） |
| `get_available_runtimes` | 获取可用的运行时环境列表 |

### 资源 (Resources)

- `file://{path}` - 获取指定文件的内容

### 提示词 (Prompts)

- `python_script_template` - 生成 Python 脚本模板
- `node_script_template` - 生成 Node.js 脚本模板
- `script_template` - 统一脚本模板（支持选择运行时）

## 安装

### 前置条件

- **Python 3.10+** - 必需
- **Node.js 18+** - 可选，如需执行 Node.js 脚本

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或者使用 uv：

```bash
uv pip install -r requirements.txt
```

### 2. 验证安装

```bash
python server.py --help
```

### 3. 验证运行时

启动服务后，调用 `get_available_runtimes` 工具查看可用的运行时环境。

## 启动服务

### 方式一：stdio 模式（用于 Cursor 集成）

```bash
python server.py
```

### 方式二：HTTP 服务模式

```bash
# 默认配置 (127.0.0.1:8000/mcp)
python server.py --transport http

# 指定端口
python server.py --transport http --port 3000

# 监听所有网络接口（允许远程访问）
python server.py --transport http --host 0.0.0.0 --port 8000

# 自定义路径
python server.py --transport http --path /api/mcp
```

### 命令行参数

| 参数 | 简写 | 默认值 | 描述 |
|-----|------|--------|------|
| `--transport` | `-t` | `stdio` | 传输方式: `stdio` 或 `http` |
| `--host` | | `127.0.0.1` | HTTP 服务监听地址 |
| `--port` | `-p` | `8000` | HTTP 服务端口 |
| `--path` | | `/mcp` | HTTP 服务路径 |

## 配置 Cursor

在 Cursor 设置中添加 MCP 服务器配置。打开 `设置 > MCP`，添加以下配置：

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

或者使用 `uv` 运行：

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

### 使用统一接口执行脚本

```python
# 执行 Python 代码
execute_script(code="print('Hello from Python!')", runtime="python")

# 执行 Node.js 代码
execute_script(code="console.log('Hello from Node.js!')", runtime="node")
```

### 执行 Python 代码

```python
execute_python(code="print('Hello, World!')")
```

### 执行 Node.js 代码

```python
execute_node(code="console.log('Hello, Node.js!')")
```

### 执行 Shell 命令

```python
execute_shell(command="dir", working_dir="C:/")
```

### 读取文件

```python
read_file(file_path="config.json")
```

### 查看可用运行时

```python
get_available_runtimes()
# 输出示例:
# ✅ Python: 3.11.0 (C:\Python311\python.exe)
# ✅ Node.js: v20.10.0 (C:\Program Files\nodejs\node.exe)
```

## 开发

### 添加新工具

使用 `@mcp.tool()` 装饰器添加新工具：

```python
@mcp.tool()
def my_new_tool(param1: str, param2: int = 10) -> str:
    """
    工具描述

    Args:
        param1: 参数1描述
        param2: 参数2描述，默认值 10

    Returns:
        返回值描述
    """
    # 实现逻辑
    return "结果"
```

### 添加新资源

使用 `@mcp.resource()` 装饰器添加新资源：

```python
@mcp.resource("my-resource://{id}")
def get_my_resource(id: str) -> str:
    """获取资源"""
    return f"资源内容 {id}"
```

## HTTP 客户端调用示例

当使用 HTTP 模式启动服务后，可以通过 HTTP 请求调用工具。

### 使用 curl

```bash
# 列出可用工具
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'

# 调用工具
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_python",
      "arguments": {"code": "print(1+1)"}
    },
    "id": 2
  }'
```

### 使用 Python

```python
import requests

url = "http://127.0.0.1:8000/mcp"

# 调用 execute_script 工具
response = requests.post(url, json={
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "execute_script",
        "arguments": {
            "code": "console.log('Hello from Node.js')",
            "runtime": "node"
        }
    },
    "id": 1
})
print(response.json())
```

## 安全注意事项

- `execute_python`、`execute_node` 和 `execute_shell` 工具可以执行任意代码，请谨慎使用
- 建议在受信任的环境中运行此服务
- HTTP 模式下，默认只监听 `127.0.0.1`，如需远程访问请配置防火墙和认证
- 可以根据需要添加命令白名单或沙箱机制

## 许可证

MIT License
