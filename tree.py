#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tree_dirs_only.py
仅显示目录树，不打印任何文件
用法:
    python tree_dirs_only.py /your/path  [-L max_depth]
"""
import argparse
from pathlib import Path

PREFIX_MIDDLE = "├── "
PREFIX_LAST   = "└── "
PREFIX_PIPE   = "│   "
PREFIX_BLANK  = "    "

def build_tree(dir_path: Path, max_depth: int = None, curr_depth: int = 0, prefix: str = ""):
    if max_depth is not None and curr_depth >= max_depth:
        return
    try:
        entries = sorted([e for e in dir_path.iterdir() if e.is_dir()])
    except PermissionError:
        return
    for idx, entry in enumerate(entries):
        is_last = idx == len(entries) - 1
        print(prefix + (PREFIX_LAST if is_last else PREFIX_MIDDLE) + entry.name)
        next_prefix = prefix + (PREFIX_BLANK if is_last else PREFIX_PIPE)
        build_tree(entry, max_depth, curr_depth + 1, next_prefix)

def main():
    parser = argparse.ArgumentParser(description="仅显示目录树")
    parser.add_argument("root", type=Path, help="要扫描的根目录")
    parser.add_argument("-L", "--max-depth", type=int, default=None,
                        help="最大深度（无限制则留空）")
    args = parser.parse_args()
    if not args.root.is_dir():
        print("错误：根目录不存在或非目录")
        return
    print(args.root.resolve())   # 打印根目录本身
    build_tree(args.root, args.max_depth)

if __name__ == "__main__":
    main()  