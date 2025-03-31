#!/usr/bin/env python3
import sys
import os
import hashlib
import glob
from typing import List, Dict, Tuple

def calculate_hash(filepath: str) -> Dict[str, str]:
    """计算单个文件的哈希值"""
    hashes = {
        'MD5': hashlib.md5(),
        'SHA1': hashlib.sha1(),
        'SHA256': hashlib.sha256()
    }
    
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            for h in hashes.values():
                h.update(chunk)
    
    return {name: h.hexdigest() for name, h in hashes.items()}

def print_hashes(filepath: str, hashes: Dict[str, str]) -> None:
    """打印文件的哈希值"""
    print(f"\n文件: {os.path.basename(filepath)}")
    print("--------------------------------------")
    for name, value in hashes.items():
        print(f"{name}:    {value}")
    print("--------------------------------------")

def info_mode(files: List[str]) -> None:
    """信息模式：计算文件哈希值"""
    found = False
    for pattern in files:
        matches = glob.glob(pattern)
        if not matches:
            continue
        
        for filepath in matches:
            if os.path.isfile(filepath):
                found = True
                try:
                    hashes = calculate_hash(filepath)
                    print_hashes(filepath, hashes)
                except Exception as e:
                    print(f"处理文件 {filepath} 时出错：{e}")
    
    if not found:
        print("未找到匹配的文件")

def compare_mode(files: List[str]) -> None:
    """比较模式：比较文件哈希值"""
    all_files = []
    for pattern in files:
        matches = glob.glob(pattern)
        all_files.extend([f for f in matches if os.path.isfile(f)])
    
    if len(all_files) < 2:
        print("错误：比较模式需要至少两个文件")
        return
    
    first_file = all_files[0]
    first_hashes = calculate_hash(first_file)
    print_hashes(first_file, first_hashes)
    
    all_same = True
    diff_files = []
    
    for filepath in all_files[1:]:
        current_hashes = calculate_hash(filepath)
        print_hashes(filepath, current_hashes)
        
        if any(first_hashes[k] != current_hashes[k] for k in first_hashes):
            all_same = False
            diff_files.append(os.path.basename(filepath))
    
    print()
    if all_same:
        print("******✅ 所有文件哈希值相同******")
    else:
        print("******⚠️ 存在不一致的哈希值******")
        print(f"以下文件与\"{os.path.basename(first_file)}\"的哈希值不同：{' '.join(diff_files)}")

def main():
    if len(sys.argv) < 3:
        print("用法：")
        print("hash -i file           计算单个或多个文件的哈希值")
        print("hash -s file1 file2    比较两个或多个文件的哈希值")
        return
    
    mode = sys.argv[1]
    files = sys.argv[2:]
    
    try:
        if mode == "-i":
            info_mode(files)
        elif mode == "-s":
            compare_mode(files)
        else:
            print("错误：无效的操作模式，请使用 -i 或 -s")
    except Exception as e:
        print(f"执行过程中出错：{e}")

if __name__ == "__main__":
    main()
