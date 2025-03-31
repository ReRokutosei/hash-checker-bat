import unittest
import os
import tempfile
import shutil
import yaml
from pathlib import Path
from hash import HashCalculator
import logging
from datetime import datetime
import time

class TestHashCalculator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 创建测试目录
        cls.test_dir = tempfile.mkdtemp()
        cls.test_files = cls._create_test_files()
        cls.test_config = cls._create_test_config()
        cls.error_log = []
        
    @classmethod
    def tearDownClass(cls):
        # 关闭所有日志处理器
        for handler in logging.getLogger().handlers[:]:
            handler.close()
            logging.getLogger().removeHandler(handler)
        
        # 等待一小段时间确保文件被释放
        time.sleep(0.1)
        
        try:
            # 清理测试目录
            shutil.rmtree(cls.test_dir)
        except Exception as e:
            print(f"警告：清理测试目录时出错: {e}")
        
        # 保存错误日志
        if cls.error_log:
            try:
                with open('test_errors.log', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(cls.error_log))
            except Exception as e:
                print(f"警告：无法保存错误日志: {e}")
    
    @classmethod
    def _create_test_files(cls):
        files = {
            'normal.txt': b'Hello, World!',
            'empty.txt': b'',
            'binary.dat': os.urandom(1024),
            'large.dat': os.urandom(1024 * 1024 * 10),  # 10MB
            'chinese.txt': '你好，世界'.encode('utf-8')
        }
        
        created_files = {}
        for name, content in files.items():
            path = os.path.join(cls.test_dir, name)
            with open(path, 'wb') as f:
                f.write(content)
            created_files[name] = path
        return created_files

    @classmethod
    def _create_test_config(cls):
        config_path = os.path.join(cls.test_dir, 'test_config.yaml')
        config = {
            'performance': {
                'async_mode': True,
                'buffer_size': 8388608,
                'use_mmap': True,
                'thread_count': 4
            },
            'algorithms': ['MD5', 'SHA1', 'SHA256'],
            'output': {
                'color': False,
                'progress_bar': False,
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
                'level': 'DEBUG',
                'file': os.path.join(cls.test_dir, 'test.log')
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        return config_path

    def _log_error(self, test_name, error_msg):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_log = f"[{timestamp}] {test_name}: {error_msg}"
        self.__class__.error_log.append(error_log)
        
    def test_basic_file_hash(self):
        try:
            calculator = HashCalculator(self.test_config)
            result = calculator.calculate_file_hash(self.test_files['normal.txt'], show_progress=False)
            self.assertIsInstance(result, dict)
            self.assertTrue(all(algo in result for algo in ['MD5', 'SHA1', 'SHA256']))
        except Exception as e:
            self._log_error('test_basic_file_hash', str(e))
            raise

    def test_empty_file(self):
        try:
            calculator = HashCalculator(self.test_config)
            result = calculator.calculate_file_hash(self.test_files['empty.txt'], show_progress=False)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self._log_error('test_empty_file', str(e))
            raise

    def test_large_file(self):
        try:
            calculator = HashCalculator(self.test_config)
            result = calculator.calculate_file_hash(self.test_files['large.dat'], show_progress=False)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self._log_error('test_large_file', str(e))
            raise

    def test_nonexistent_file(self):
        calculator = HashCalculator(self.test_config)
        with self.assertRaises(Exception):
            calculator.calculate_file_hash('nonexistent.txt')

    def test_invalid_config(self):
        invalid_config = os.path.join(self.test_dir, 'invalid.yaml')
        with open(invalid_config, 'w', encoding='utf-8') as f:
            f.write('invalid_key invalid_value')  # 使用有效但格式错误的YAML
        
        try:
            calculator = HashCalculator(invalid_config)
            # 验证是否使用了默认配置
            self.assertIsInstance(calculator.config, dict)
            self.assertTrue('algorithms' in calculator.config)
            self.assertTrue('performance' in calculator.config)
        except Exception as e:
            self._log_error('test_invalid_config', str(e))
            raise

    def test_multiple_files(self):
        try:
            calculator = HashCalculator(self.test_config)
            test_files = [self.test_files['normal.txt'], self.test_files['binary.dat']]
            calculator.process_files(test_files, mode="info", format="json")
        except Exception as e:
            self._log_error('test_multiple_files', str(e))
            raise

    def test_chinese_filename(self):
        try:
            calculator = HashCalculator(self.test_config)
            result = calculator.calculate_file_hash(self.test_files['chinese.txt'], show_progress=False)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self._log_error('test_chinese_filename', str(e))
            raise

def run_tests():
    # 配置测试运行器
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHashCalculator)
    runner = unittest.TextTestRunner(verbosity=2)
    
    # 运行测试并获取结果
    result = runner.run(suite)
    
    # 输出测试统计
    print("\n测试统计:")
    print(f"运行测试用例总数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    # 如果有测试错误日志，显示文件位置
    if TestHashCalculator.error_log:
        print("\n详细错误日志已保存到: test_errors.log")

if __name__ == '__main__':
    run_tests()
