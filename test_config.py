import unittest
import os
import tempfile
import itertools
import time
import yaml
from hash import HashCalculator
from typing import Dict, Any, List, Generator
import shutil

class ConfigTester:
    def __init__(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = self._create_test_file()
        self.results = []

    def _create_test_file(self, size: int = 1024 * 1024 * 10) -> str:
        """创建测试文件（默认10MB）"""
        filepath = os.path.join(self.test_dir, 'test.dat')
        with open(filepath, 'wb') as f:
            f.write(os.urandom(size))
        return filepath

    def _generate_config_variants(self) -> Generator[Dict[str, Any], None, None]:
        """生成不同的配置组合"""
        base_config = {
            'performance': {
                'async_mode': [True, False],
                'buffer_size': [1024*1024, 8*1024*1024],
                'use_mmap': [True, False],
                'thread_count': [1, 4]
            },
            'algorithms': {
                'MD5': {'enabled': [True, False]},
                'SHA1': {'enabled': [True]},
                'SHA256': {'enabled': [True, False]}
            },
            'comparison': {
                'match_message': ["******✅ 所有文件哈希值相同******"],
                'mismatch_message': ["******⚠️ 存在不一致的哈希值******"]
            },
            'output': {
                'color': [False],
                'progress_bar': [False],
                'show_time': [True],
                'format': ['default'],
                'generate_hash_file': [True, False],
                'hash_file_format': ['GNU', 'BSD'],
                'hash_file_encoding': ['utf-8', 'gbk']
            },
            'file_handling': {
                'recursive': False,
                'retry_count': 1,
                'ignore_errors': False
            },
            'logging': {
                'enabled': False
            }
        }

        # 生成配置组合
        for perf_mode in [True, False]:
            for buffer_size in [1024*1024, 8*1024*1024]:
                for mmap in [True, False]:
                    for threads in [1, 4]:
                        # 生成算法组合
                        for md5 in [True, False]:
                            for sha256 in [True, False]:
                                if not (md5 or sha256):
                                    continue  # 跳过没有启用任何算法的情况
                                
                                config = {
                                    'performance': {
                                        'async_mode': perf_mode,
                                        'buffer_size': buffer_size,
                                        'use_mmap': mmap,
                                        'thread_count': threads
                                    },
                                    'algorithms': {
                                        'MD5': {'enabled': md5},
                                        'SHA1': {'enabled': True},
                                        'SHA256': {'enabled': sha256}
                                    },
                                    'comparison': {
                                        'match_message': "******✅ 所有文件哈希值相同******",
                                        'mismatch_message': "******⚠️ 存在不一致的哈希值******",
                                        'detail_format': "{file1} 与 {file2} 的 {algo} 值不同"
                                    },
                                    'output': {
                                        'color': False,
                                        'progress_bar': False,
                                        'show_time': True,
                                        'format': 'default',
                                        'generate_hash_file': True,
                                        'hash_file_format': 'GNU',
                                        'hash_file_encoding': 'utf-8'
                                    },
                                    'file_handling': {
                                        'recursive': False,
                                        'retry_count': 1,
                                        'ignore_errors': False
                                    },
                                    'logging': {
                                        'enabled': False
                                    }
                                }
                                yield config

    def test_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """测试单个配置"""
        config_file = os.path.join(self.test_dir, 'test_config.yaml')
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        start_time = time.time()
        try:
            calculator = HashCalculator(config_file)
            result = calculator.calculate_file_hash(self.test_file, show_progress=False)
            success = True
        except Exception as e:
            success = False
            result = str(e)

        duration = time.time() - start_time
        return {
            'config': config,
            'success': success,
            'duration': duration,
            'result': result
        }

    def run_tests(self) -> None:
        """运行所有配置测试"""
        print("开始配置测试...")
        total_configs = 0
        success_configs = 0

        for config in self._generate_config_variants():
            total_configs += 1
            result = self.test_config(config)
            if result['success']:
                success_configs += 1
                self.results.append(result)
                print(f"\n配置 {total_configs} 测试成功:")
                print(f"算法: {config['algorithms']}")
                print(f"异步模式: {config['performance']['async_mode']}")
                print(f"内存映射: {config['performance']['use_mmap']}")
                print(f"缓冲区: {config['performance']['buffer_size']//1024}KB")
                print(f"耗时: {result['duration']:.3f}秒")
            else:
                print(f"\n配置 {total_configs} 测试失败:")
                print(f"错误: {result['result']}")

        print(f"\n测试完成:")
        print(f"总配置数: {total_configs}")
        print(f"成功: {success_configs}")
        print(f"失败: {total_configs - success_configs}")

        if self.results:
            # 找出最快的配置
            fastest = min(self.results, key=lambda x: x['duration'])
            print("\n最佳性能配置:")
            print(f"算法: {fastest['config']['algorithms']}")
            print(f"异步模式: {fastest['config']['performance']['async_mode']}")
            print(f"内存映射: {fastest['config']['performance']['use_mmap']}")
            print(f"缓冲区: {fastest['config']['performance']['buffer_size']//1024}KB")
            print(f"耗时: {fastest['duration']:.3f}秒")

    def cleanup(self) -> None:
        """清理测试文件"""
        try:
            shutil.rmtree(self.test_dir)
        except Exception as e:
            print(f"清理测试目录时出错: {e}")

def main():
    tester = ConfigTester()
    try:
        tester.run_tests()
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
