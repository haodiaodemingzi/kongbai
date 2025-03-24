#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单的调试脚本，测试输出
"""

import sys
import os

def main():
    """主函数，测试简单输出"""
    # 直接打印到标准输出
    print("测试标准输出 - 这是一条普通的 print 消息")
    sys.stdout.write("这是 sys.stdout.write 的消息\n")
    sys.stdout.flush()
    
    # 打印到标准错误
    print("测试标准错误 - 这是一条错误消息", file=sys.stderr)
    sys.stderr.write("这是 sys.stderr.write 的消息\n")
    sys.stderr.flush()
    
    # 写入到文件
    with open("debug_output.txt", "w", encoding="utf-8") as f:
        f.write("这是写入到文件的消息\n")
    
    # 检查文件是否创建成功
    if os.path.exists("debug_output.txt"):
        print(f"文件创建成功: debug_output.txt")
        print(f"文件大小: {os.path.getsize('debug_output.txt')} 字节")
    
    return 0

if __name__ == "__main__":
    print("开始执行调试脚本")
    result = main()
    print(f"脚本执行完成，结果: {result}")
    sys.exit(result) 