#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将HTTP图片地址转换为base64编码
"""

import base64
import requests
import sys
import argparse


def image_url_to_base64(url: str, timeout: int = 30) -> str:
    """
    从HTTP地址获取图片并转换为base64编码
    
    Args:
        url: 图片的HTTP地址
        timeout: 请求超时时间（秒）
    
    Returns:
        图片的base64编码字符串
    
    Raises:
        requests.RequestException: 请求失败时抛出
        ValueError: URL无效或响应不是图片时抛出
    """
    if not url or not url.startswith(('http://', 'https://')):
        raise ValueError("无效的URL，必须以http://或https://开头")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    
    content_type = response.headers.get('Content-Type', '')
    if not content_type.startswith('image/'):
        raise ValueError(f"响应不是图片类型，Content-Type: {content_type}")
    
    image_data = response.content
    base64_encoded = base64.b64encode(image_data).decode('utf-8')
    
    return base64_encoded


def image_url_to_base64_with_prefix(url: str, timeout: int = 30) -> str:
    """
    从HTTP地址获取图片并转换为带Data URI前缀的base64编码
    
    Args:
        url: 图片的HTTP地址
        timeout: 请求超时时间（秒）
    
    Returns:
        带Data URI前缀的base64编码字符串，如: data:image/png;base64,xxxxx
    """
    if not url or not url.startswith(('http://', 'https://')):
        raise ValueError("无效的URL，必须以http://或https://开头")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    
    content_type = response.headers.get('Content-Type', 'image/png')
    if not content_type.startswith('image/'):
        raise ValueError(f"响应不是图片类型，Content-Type: {content_type}")
    
    image_data = response.content
    base64_encoded = base64.b64encode(image_data).decode('utf-8')
    
    return f"data:{content_type};base64,{base64_encoded}"


def main():
    parser = argparse.ArgumentParser(description='将HTTP图片地址转换为base64编码')
    parser.add_argument('url', help='图片的HTTP地址')
    parser.add_argument('--prefix', '-p', action='store_true', 
                        help='是否添加Data URI前缀')
    parser.add_argument('--timeout', '-t', type=int, default=30,
                        help='请求超时时间（秒），默认30秒')
    
    args = parser.parse_args()
    
    try:
        if args.prefix:
            result = image_url_to_base64_with_prefix(args.url, args.timeout)
        else:
            result = image_url_to_base64(args.url, args.timeout)
        print(result)
    except requests.RequestException as e:
        print(f"请求失败: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
