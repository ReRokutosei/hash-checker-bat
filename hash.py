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
            'algorithms': {
                'MD5': {'enabled': True},
                'SHA1': {'enabled': True},
                'SHA256': {'enabled': True}
            },
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
            },
            'comparison': {
                'match_message': "所有文件的哈希值均匹配",
                'mismatch_message': "存在哈希值不匹配的文件",
                'detail_format': "文件 {file1} 和 {file2} 的 {algo} 哈希值不匹配"
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
        """设置哈希算法"""
        self.hash_funcs = {}
        for algo, config in self.config['algorithms'].items():
            if config.get('enabled', True) and hasattr(hashlib, algo.lower()):
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

    def compare_files(self, files: List[str]) -> Dict[str, Any]:
        """比较多个文件的哈希值"""
        # 展开通配符
        expanded_files = []
        for pattern in files:
            matched = glob.glob(pattern)
            if matched:
                expanded_files.extend(matched)
        
        if len(expanded_files) < 2:
            raise ValueError("比较模式需要至少两个文件")
            
        results = {
            'reference': None,
            'comparisons': [],
            'all_match': True
        }
        
        # 计算所有文件的哈希值
        hashes = {}
        for file in expanded_files:
            try:
                hashes[file] = self.calculate_file_hash(file)
            except Exception as e:
                logging.error(f"处理文件 {file} 失败: {e}")
                if not self.config['file_handling']['ignore_errors']:
                    raise
                continue
        
        # 设置参考文件和比较结果
        ref_file = expanded_files[0]
        results['reference'] = {'file': ref_file, 'hashes': hashes[ref_file]}
        
        # 比较其他文件
        for file in expanded_files[1:]:
            if file not in hashes:
                continue
            
            comparison = {
                'file': file,
                'hashes': hashes[file],
                'matches': {},
                'mismatches': []
            }
            
            for algo in self.hash_funcs.keys():
                matches = (hashes[ref_file][algo] == hashes[file][algo])
                comparison['matches'][algo] = matches
                if not matches:
                    results['all_match'] = False
                    mismatch = self.config['comparison']['detail_format'].format(
                        file1=os.path.basename(ref_file),
                        file2=os.path.basename(file),
                        algo=algo
                    )
                    comparison['mismatches'].append(mismatch)
            
            results['comparisons'].append(comparison)
        
        return results

    def format_comparison_output(self, results: Dict[str, Any], output_format: str = "default") -> None:
        """格式化比较结果输出"""
        if output_format == "json":
            import json
            print(json.dumps(results, ensure_ascii=False, indent=2))
            
        elif output_format == "csv":
            ref_file = results['reference']['file']
            print(f"file,algorithm,reference({ref_file}),value,matches")
            for comp in results['comparisons']:
                for algo in self.hash_funcs.keys():
                    print(f"{comp['file']},{algo},{results['reference']['hashes'][algo]},"
                          f"{comp['hashes'][algo]},{comp['matches'][algo]}")
        else:
            ref = results['reference']
            print(f"\n参考文件: {Fore.CYAN}{os.path.basename(ref['file'])}{Style.RESET_ALL}")
            print("--------------------------------------")
            for algo, value in ref['hashes'].items():
                print(f"{algo}:    {Fore.GREEN}{value}{Style.RESET_ALL}")
            print("--------------------------------------")
            
            for comp in results['comparisons']:
                print(f"\n比较文件: {Fore.CYAN}{os.path.basename(comp['file'])}{Style.RESET_ALL}")
                print("--------------------------------------")
                for algo, value in comp['hashes'].items():
                    color = Fore.GREEN if comp['matches'][algo] else Fore.RED
                    print(f"{algo}:    {color}{value}{Style.RESET_ALL}")
                print("--------------------------------------")
        
        # 添加总结信息
        if results['all_match']:
            print(f"\n{self.config['comparison']['match_message']}")
        else:
            print(f"\n{self.config['comparison']['mismatch_message']}")
            for comp in results['comparisons']:
                if comp['mismatches']:
                    for mismatch in comp['mismatches']:
                        print(mismatch)

    def parse_hash_file(self, hash_file: str) -> List[Dict[str, str]]:
        """解析哈希校验文件
        返回格式: [{'filename': str, 'hash': str, 'binary': bool}, ...]
        """
        results = []
        target_file = os.path.splitext(hash_file)[0]
        
        try:
            with open(hash_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                
            # 处理单行情况
            if len(lines) == 1:
                line = lines[0]
                # 情况1: 仅包含哈希值
                if ' ' not in line:
                    results.append({
                        'filename': target_file,
                        'hash': line.lower(),
                        'binary': False
                    })
                else:
                    # 情况2: "[hash] *filename" 或 "[hash] filename"
                    hash_value, *name_parts = line.split()
                    filename = ' '.join(name_parts)
                    if filename.startswith('*'):
                        filename = filename[1:]  # 去除星号
                        binary = True
                    else:
                        binary = False
                    
                    results.append({
                        'filename': filename,
                        'hash': hash_value.lower(),
                        'binary': binary
                    })
            # 处理多行情况
            else:
                for line in lines:
                    if ' ' in line:
                        hash_value, *name_parts = line.split()
                        filename = ' '.join(name_parts)
                        binary = filename.startswith('*')
                        if binary:
                            filename = filename[1:]
                        
                        results.append({
                            'filename': filename,
                            'hash': hash_value.lower(),
                            'binary': binary
                        })
        
        except Exception as e:
            logging.error(f"解析哈希文件 {hash_file} 时出错: {e}")
            raise
            
        return results

    def auto_verify_files(self) -> None:
        """自动验证模式"""
        # 获取所有可用的哈希算法
        all_algorithms = {name.upper() for name in hashlib.algorithms_available}
        temp_hash_funcs = {}
        
        # 获取当前目录下所有哈希文件
        hash_files = []
        for algo in all_algorithms:
            hash_files.extend(glob.glob(f"*.{algo.lower()}"))
        
        if not hash_files:
            print("未找到任何哈希校验文件")
            return
            
        success_count = 0
        fail_count = 0
        
        for hash_file in hash_files:
            algo = os.path.splitext(hash_file)[1][1:].upper()
            
            # 如果算法被禁用，临时启用它
            if algo not in self.hash_funcs:
                if hasattr(hashlib, algo.lower()):
                    temp_hash_funcs[algo] = getattr(hashlib, algo.lower())
                else:
                    print(f"⚠️ 不支持的哈希算法: {algo}")
                    continue
            
            try:
                # 解析哈希文件
                hash_entries = self.parse_hash_file(hash_file)
                
                for entry in hash_entries:
                    if not os.path.exists(entry['filename']):
                        print(f"⚠️ 未找到文件: {entry['filename']}")
                        fail_count += 1
                        continue
                    
                    # 计算实际哈希值
                    hash_func = self.hash_funcs.get(algo) or temp_hash_funcs.get(algo)
                    actual_hash = hash_func()
                    
                    with open(entry['filename'], 'rb') as f:
                        while chunk := f.read(self.config['performance']['buffer_size']):
                            actual_hash.update(chunk)
                    
                    actual_value = actual_hash.hexdigest().lower()
                    
                    if actual_value == entry['hash']:
                        print(f"✅ {entry['filename']} ({algo}) 验证通过")
                        success_count += 1
                    else:
                        print(f"❌ {entry['filename']} ({algo}) 验证失败")
                        print(f"预期: {entry['hash']}")
                        print(f"实际: {actual_value}")
                        fail_count += 1
                        
            except Exception as e:
                print(f"处理 {hash_file} 时出错: {e}")
                fail_count += 1
        
        # 清理临时哈希函数
        temp_hash_funcs.clear()
        print(f"\n验证完成: 成功 {success_count}, 失败 {fail_count}")

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
        
        try:
            if mode == "auto_verify":
                self.auto_verify_files()
            elif mode == "compare":
                results = self.compare_files(files)
                self.format_comparison_output(results, kwargs.get('format', 'default'))
            else:  # info mode
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
        
        finally:
            if self.config['output']['show_time']:
                elapsed = time.time() - start_time
                print(f"\n处理完成，耗时: {elapsed:.2f} 秒")

def main():
    if len(sys.argv) < 2:
        print("用法：")
        print("hash -i file           计算单个或多个文件的哈希值")
        print("hash -s file1 file2    比较两个或多个文件的哈希值")
        print("hash -a         无参数，自动验证当前目录下的哈希文件")
        return
    
    try:
        calculator = HashCalculator()
        mode = sys.argv[1]
        
        if mode == "-i":
            calculator.process_files(sys.argv[2:], mode="info")
        elif mode == "-s":
            calculator.process_files(sys.argv[2:], mode="compare")
        elif mode == "-a":
            calculator.process_files([], mode="auto_verify")
        else:
            print("错误：无效的操作模式，请使用 -i, -s 或 -a")
            
    except Exception as e:
        print(f"执行过程中出错：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
