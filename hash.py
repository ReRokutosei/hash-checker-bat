#!/usr/bin/env python3
import sys
import os
import hashlib
import glob
import time
import mmap
import yaml
import logging
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from tqdm import tqdm
from colorama import init, Fore, Style

# 初始化彩色输出
init()

class HashCalculator:
    def __init__(self, config_path: str = "config.yaml"):
        # 处理配置文件路径
        self.config_path = self._resolve_config_path(config_path)
        if not os.path.exists(self.config_path):
            self.create_default_config(self.config_path)
        self.config = self.load_config(self.config_path)
        if not self.validate_config(self.config):
            logging.warning("配置验证失败，使用默认配置")
            self.config = self.get_default_config()
        self.setup_logging()
        self.setup_algorithms()
        
    def _resolve_config_path(self, config_path: str) -> str:
        """解析配置文件路径"""
        if os.path.isabs(config_path):
            return config_path
        
        # 首先检查当前目录
        if os.path.exists(config_path):
            return os.path.abspath(config_path)
            
        # 然后检查用户目录
        user_config = os.path.join(os.path.expanduser("~"), ".config", "hash", "config.yaml")
        if os.path.exists(user_config):
            return user_config
            
        # 最后检查程序所在目录
        prog_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
        if os.path.exists(prog_config):
            return prog_config
            
        # 如果都不存在，使用用户目录
        return user_config

    def validate_config(self, config: Any) -> bool:
        """验证配置是否有效"""
        if not isinstance(config, dict):
            return False
            
        required_sections = ['performance', 'algorithms', 'output', 'file_handling', 'logging']
        return all(section in config for section in required_sections)

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config is None:
                    raise ValueError("配置文件为空")
                return config
        except Exception as e:
            logging.warning(f"无法加载配置文件: {e}，使用默认配置")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """返回默认配置"""
        return {
            'performance': {
                'async_mode': True,
                'buffer_size': 8388608,
                'use_mmap': True,
                'thread_count': 4
            },
            'algorithms': ['MD5', 'SHA1', 'SHA256'],
            'output': {
                'color': True,
                'progress_bar': True,
                'show_time': True,
                'format': 'default'
            },
            'file_handling': {
                'recursive': False,
                'retry_count': 3,
                'ignore_errors': False
            },
            'logging': {
                'enabled': True,
                'level': 'INFO',
                'file': 'hash_calculator.log'
            }
        }

    def create_default_config(self, config_path: str) -> None:
        """创建默认配置文件"""
        try:
            config = self.get_default_config()
            # 确保配置目录存在
            config_dir = os.path.dirname(config_path)
            if config_dir:  # 如果不是当前目录
                os.makedirs(config_dir, exist_ok=True)
                
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            logging.info(f"已创建默认配置文件: {config_path}")
        except Exception as e:
            logging.error(f"创建配置文件失败: {e}")
            raise

    def setup_logging(self) -> None:
        """设置日志处理"""
        log_config = self.config.get('logging', {})
        if log_config.get('enabled', True):
            handlers = []
            # 添加文件处理器
            if log_config.get('file'):
                try:
                    file_handler = logging.FileHandler(
                        log_config['file'],
                        mode='w',  # 使用 'w' 模式而不是 'a' 模式
                        encoding='utf-8'
                    )
                    file_handler.setFormatter(
                        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                    )
                    handlers.append(file_handler)
                except Exception as e:
                    print(f"警告：无法创建日志文件：{e}")
            
            # 添加控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter('%(levelname)s: %(message)s')
            )
            handlers.append(console_handler)

            # 配置根日志记录器
            logging.basicConfig(
                level=getattr(logging, log_config.get('level', 'INFO')),
                handlers=handlers
            )

    def setup_algorithms(self) -> None:
        self.hash_funcs = {}
        for algo in self.config['algorithms']:
            if hasattr(hashlib, algo.lower()):
                self.hash_funcs[algo] = getattr(hashlib, algo.lower())

    def calculate_file_hash(self, filepath: str, show_progress: bool = True) -> Dict[str, str]:
        file_size = os.path.getsize(filepath)
        hashes = {name: func() for name, func in self.hash_funcs.items()}
        
        try:
            with open(filepath, 'rb') as f:
                if self.config['performance']['use_mmap'] and file_size > 0:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        if show_progress:
                            with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"处理 {os.path.basename(filepath)}") as pbar:
                                for chunk in iter(lambda: mm.read(self.config['performance']['buffer_size']), b''):
                                    for h in hashes.values():
                                        h.update(chunk)
                                    pbar.update(len(chunk))
                        else:
                            for chunk in iter(lambda: mm.read(self.config['performance']['buffer_size']), b''):
                                for h in hashes.values():
                                    h.update(chunk)
                else:
                    if show_progress:
                        with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"处理 {os.path.basename(filepath)}") as pbar:
                            while chunk := f.read(self.config['performance']['buffer_size']):
                                for h in hashes.values():
                                    h.update(chunk)
                                pbar.update(len(chunk))
                    else:
                        while chunk := f.read(self.config['performance']['buffer_size']):
                            for h in hashes.values():
                                h.update(chunk)
        
        except Exception as e:
            logging.error(f"处理文件 {filepath} 时出错: {e}")
            raise
        
        return {name: h.hexdigest() for name, h in hashes.items()}

    def format_output(self, filepath: str, hashes: Dict[str, str], output_format: str = "default") -> None:
        if output_format == "json":
            import json
            print(json.dumps({"file": filepath, "hashes": hashes}, ensure_ascii=False))
        elif output_format == "csv":
            print(f"{filepath},{','.join(hashes.values())}")
        else:
            print(f"\n文件: {Fore.CYAN}{os.path.basename(filepath)}{Style.RESET_ALL}")
            print("--------------------------------------")
            for name, value in hashes.items():
                print(f"{name}:    {Fore.GREEN}{value}{Style.RESET_ALL}")
            print("--------------------------------------")

    def process_files(self, files: List[str], mode: str, **kwargs) -> None:
        start_time = time.time()
        
        if self.config['performance']['async_mode']:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.config['performance']['thread_count']
            ) as executor:
                futures = []
                for pattern in files:
                    if self.config['file_handling']['recursive']:
                        pattern = str(Path(pattern).absolute())
                        for filepath in Path(os.path.dirname(pattern)).rglob(os.path.basename(pattern)):
                            if filepath.is_file():
                                futures.append(executor.submit(self.calculate_file_hash, str(filepath)))
                    else:
                        for filepath in glob.glob(pattern):
                            if os.path.isfile(filepath):
                                futures.append(executor.submit(self.calculate_file_hash, filepath))
                
                for future, filepath in zip(concurrent.futures.as_completed(futures), files):
                    try:
                        hashes = future.result()
                        self.format_output(filepath, hashes, kwargs.get('format', 'default'))
                    except Exception as e:
                        logging.error(f"处理文件 {filepath} 失败: {e}")
                        if not self.config['file_handling']['ignore_errors']:
                            raise
        
        if self.config['output']['show_time']:
            elapsed = time.time() - start_time
            print(f"\n处理完成，耗时: {elapsed:.2f} 秒")

def main():
    if len(sys.argv) < 3:
        print("用法：")
        print("hash -i file           计算单个或多个文件的哈希值")
        print("hash -s file1 file2    比较两个或多个文件的哈希值")
        return
    
    try:
        calculator = HashCalculator()
        mode = sys.argv[1]
        files = sys.argv[2:]
        
        if mode == "-i":
            calculator.process_files(files, mode="info")
        elif mode == "-s":
            calculator.process_files(files, mode="compare")
        else:
            print("错误：无效的操作模式，请使用 -i 或 -s")
    except Exception as e:
        print(f"执行过程中出错：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
