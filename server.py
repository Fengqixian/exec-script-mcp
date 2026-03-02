"""
MCP 脚本执行服务

提供脚本执行工具，支持 Python 和 Node.js 代码执行。

支持的传输方式：
- stdio: 标准输入输出（默认，用于 Cursor 等 IDE 集成）
- streamable-http: HTTP 服务（用于远程调用和 Web 集成）
"""

import subprocess
import sys
import os
import shutil
import tempfile
import argparse
import uuid
import json
from typing import Optional, Literal
from enum import Enum
from mcp.server.fastmcp import FastMCP


class Runtime(str, Enum):
    PYTHON = "python"
    NODE = "node"


def get_runtime_executable(runtime: Runtime) -> tuple[str, str]:
    """获取运行时的可执行文件路径和文件扩展名"""
    if runtime == Runtime.PYTHON:
        return sys.executable, ".py"
    elif runtime == Runtime.NODE:
        node_path = shutil.which("node")
        if not node_path:
            raise RuntimeError("Node.js 未安装或不在 PATH 中")
        return node_path, ".js"
    else:
        raise ValueError(f"不支持的运行时: {runtime}")


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXECUTIONS_DIR = os.path.join(SCRIPT_DIR, "executions")


def _get_execution_dir() -> tuple[str, str]:
    """创建并返回一个基于 UUID 的隔离执行目录
    
    Returns:
        tuple: (执行目录的完整路径, UUID 目录名)
    """
    os.makedirs(EXECUTIONS_DIR, exist_ok=True)
    exec_id = str(uuid.uuid4())
    exec_dir = os.path.join(EXECUTIONS_DIR, exec_id)
    os.makedirs(exec_dir, exist_ok=True)
    return exec_dir, exec_id


def _list_directory_files(directory: str) -> list[dict]:
    """列出目录下的所有文件和子目录
    
    Args:
        directory: 目录路径
        
    Returns:
        文件信息列表，每项包含 name, type, size
    """
    files = []
    try:
        for entry in os.scandir(directory):
            file_info = {
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file",
            }
            if entry.is_file():
                file_info["size"] = entry.stat().st_size
            files.append(file_info)
    except Exception:
        pass
    return files


def _execute_code(code: str, runtime: Runtime, timeout: int) -> str:
    """内部函数：执行代码（在 UUID 隔离目录中）"""
    result_data = {
        "success": False,
        "execution_id": None,
        "execution_dir": None,
        "stdout": None,
        "stderr": None,
        "return_code": None,
        "error": None,
        "files": []
    }
    
    try:
        executable, suffix = get_runtime_executable(runtime)
    except RuntimeError as e:
        result_data["error"] = str(e)
        return json.dumps(result_data, ensure_ascii=False, indent=2)

    # 创建隔离的执行目录
    exec_dir, exec_id = _get_execution_dir()
    result_data["execution_id"] = exec_id
    result_data["execution_dir"] = exec_dir
    
    # 脚本文件名
    script_name = f"script{suffix}"
    script_path = os.path.join(exec_dir, script_name)
    
    # 写入脚本文件
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(code)

    # 对于 Node.js，需要确保能访问 node_modules
    # 设置环境变量 NODE_PATH 指向脚本目录的 node_modules
    env = os.environ.copy()
    if runtime == Runtime.NODE:
        node_modules_path = os.path.join(SCRIPT_DIR, "node_modules")
        if os.path.exists(node_modules_path):
            env["NODE_PATH"] = node_modules_path

    try:
        result = subprocess.run(
            [executable, script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=exec_dir,
            env=env
        )

        result_data["success"] = result.returncode == 0
        result_data["stdout"] = result.stdout if result.stdout else None
        result_data["stderr"] = result.stderr if result.stderr else None
        result_data["return_code"] = result.returncode

    except subprocess.TimeoutExpired:
        result_data["error"] = f"执行超时（超过 {timeout} 秒）"
    except Exception as e:
        result_data["error"] = str(e)

    # 列出执行目录下的文件
    result_data["files"] = _list_directory_files(exec_dir)
    
    return json.dumps(result_data, ensure_ascii=False, indent=2)


def register_tools(mcp: FastMCP):
    """注册所有工具到 MCP 服务"""

    @mcp.tool()
    def execute_script(
        code: str,
        runtime: Literal["python", "node"] = "python",
        timeout: int = 30
    ) -> str:
        """
        执行脚本代码（支持多种运行时环境）

        Args:
            code: 要执行的脚本代码
            runtime: 运行时环境，可选 "python" 或 "node"，默认 "python"
            timeout: 执行超时时间（秒），默认 30 秒

        Returns:
            执行结果或错误信息
        """
        rt = Runtime(runtime)
        return _execute_code(code, rt, timeout)



def register_resources(mcp: FastMCP):
    """注册所有资源到 MCP 服务"""

    @mcp.resource("file://{path}")
    def get_file_resource(path: str) -> str:
        """
        获取文件内容作为资源

        Args:
            path: 文件路径

        Returns:
            文件内容
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"错误: {str(e)}"


def register_prompts(mcp: FastMCP):
    """注册所有提示词到 MCP 服务"""

    @mcp.prompt()
    def python_script_template(task: str) -> str:
        """
        生成 Python 脚本模板

        Args:
            task: 脚本要完成的任务描述
        """
        return f"""请编写一个 Python 脚本来完成以下任务：

任务: {task}

要求:
1. 代码要清晰易读
2. 包含必要的错误处理
3. 添加适当的注释
4. 使用标准库（如果可能）
"""

    @mcp.prompt()
    def node_script_template(task: str) -> str:
        """
        生成 Node.js 脚本模板

        Args:
            task: 脚本要完成的任务描述
        """
        return f"""请编写一个 Node.js 脚本来完成以下任务：

任务: {task}

要求:
1. 代码要清晰易读
2. 包含必要的错误处理
3. 使用 ES6+ 语法
4. 优先使用内置模块（fs, path, http 等）
"""


def create_server(host: str = "127.0.0.1", port: int = 8000, path: str = "/mcp") -> FastMCP:
    """创建并配置 MCP 服务"""
    mcp = FastMCP(
        "Script Executor",
        host=host,
        port=port,
        streamable_http_path=path
    )

    register_tools(mcp)
    register_resources(mcp)
    register_prompts(mcp)

    return mcp


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="MCP 脚本执行服务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用 stdio 传输（默认，用于 Cursor 集成）
  python server.py

  # 使用 HTTP 服务
  python server.py --transport http --port 8000

  # 指定主机和端口
  python server.py --transport http --host 0.0.0.0 --port 3000
        """
    )
    parser.add_argument(
        "--transport", "-t",
        choices=["stdio", "http"],
        default="stdio",
        help="传输方式: stdio (默认) 或 http"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP 服务监听地址 (默认: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="HTTP 服务端口 (默认: 8000)"
    )
    parser.add_argument(
        "--path",
        default="/mcp",
        help="HTTP 服务路径 (默认: /mcp)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    mcp = create_server(
        host=args.host,
        port=args.port,
        path=args.path
    )

    if args.transport == "http":
        print(f"启动 HTTP 服务: http://{args.host}:{args.port}{args.path}")
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
