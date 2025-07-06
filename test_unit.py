import logging
import os
import shutil
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path

import yaml

from hash import HashCalculator


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
                with open("test_errors.log", "w", encoding="utf-8") as f:
                    f.write("\n".join(cls.error_log))
            except Exception as e:
                print(f"警告：无法保存错误日志: {e}")

    @classmethod
    def _create_test_files(cls):
        """创建更全面的测试文件集"""
        files = {
            # 基础测试文件
            "normal.txt": b"Hello, World!",
            "empty.txt": b"",
            "binary.dat": os.urandom(1024),
            "large.dat": os.urandom(1024 * 1024 * 10),  # 10MB
            # 特殊文件名测试
            "chinese中文.txt": "你好，世界".encode("utf-8"),
            "space in name.txt": b"test",
            "special!@#$%^&().txt": b"test",
            "1234567890.txt": b"test",
            ".hidden": b"test",
            # 文件扩展名测试
            "test.gz": os.urandom(1024),
            "test.tar": os.urandom(1024),
            "test.zip": os.urandom(1024),
            "test.7z": os.urandom(1024),
            "test.rar": os.urandom(1024),
            # 相同扩展名文件
            "test1.png": os.urandom(1024),
            "test2.png": os.urandom(1024),
            "test3.png": os.urandom(1024),
        }

        # 创建目录结构
        dirs = {
            "subdir1": ["sub1.txt", "sub2.txt"],
            "subdir2/nested": ["deep1.txt", "deep2.txt"],
            "empty_dir": [],
            "space dir": ["test.txt"],
            "中文目录": ["test.txt"],
        }

        created_files = {}
        # 创建基础文件
        for name, content in files.items():
            path = os.path.join(cls.test_dir, name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(content)
            created_files[name] = path

        # 创建目录结构
        for dir_path, files in dirs.items():
            full_dir_path = os.path.join(cls.test_dir, dir_path)
            os.makedirs(full_dir_path, exist_ok=True)
            for file in files:
                file_path = os.path.join(full_dir_path, file)
                with open(file_path, "wb") as f:
                    f.write(b"test content")
                created_files[f"{dir_path}/{file}"] = file_path

        return created_files

    @classmethod
    def _create_test_config(cls):
        config_path = os.path.join(cls.test_dir, "test_config.yaml")
        config = {
            "performance": {
                "async_mode": True,
                "buffer_size": 8388608,
                "use_mmap": True,
                "thread_count": 4,
            },
            "algorithms": {
                "MD5": {"enabled": True},
                "SHA1": {"enabled": True},
                "SHA256": {"enabled": True},
            },
            "output": {
                "color": False,
                "progress_bar": False,
                "show_time": True,
                "format": "default",
                "generate_hash_file": False,
                "hash_file_format": "GNU",
                "hash_file_encoding": "utf-8",
            },
            "file_handling": {
                "recursive": False,
                "retry_count": 3,
                "ignore_errors": False,
            },
            "logging": {
                "enabled": True,
                "level": "DEBUG",
                "file": os.path.join(cls.test_dir, "test.log"),
            },
            "comparison": {
                "match_message": "******✅ 所有文件哈希值相同******",
                "mismatch_message": "******⚠️ 存在不一致的哈希值******",
                "detail_format": "{file1} 与 {file2} 的 {algo} 值不同",
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(config, f)
        return config_path

    def _log_error(self, test_name, error_msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_log = f"[{timestamp}] {test_name}: {error_msg}"
        self.__class__.error_log.append(error_log)

    def test_basic_file_hash(self):
        try:
            calculator = HashCalculator(self.test_config)
            result = calculator.calculate_file_hash(
                self.test_files["normal.txt"], show_progress=False
            )
            self.assertIsInstance(result, dict)
            self.assertTrue(all(algo in result for algo in ["MD5", "SHA1", "SHA256"]))
        except Exception as e:
            self._log_error("test_basic_file_hash", str(e))
            raise

    def test_empty_file(self):
        try:
            calculator = HashCalculator(self.test_config)
            result = calculator.calculate_file_hash(
                self.test_files["empty.txt"], show_progress=False
            )
            self.assertIsInstance(result, dict)
        except Exception as e:
            self._log_error("test_empty_file", str(e))
            raise

    def test_large_file(self):
        try:
            calculator = HashCalculator(self.test_config)
            result = calculator.calculate_file_hash(
                self.test_files["large.dat"], show_progress=False
            )
            self.assertIsInstance(result, dict)
        except Exception as e:
            self._log_error("test_large_file", str(e))
            raise

    def test_nonexistent_file(self):
        calculator = HashCalculator(self.test_config)
        with self.assertRaises(Exception):
            calculator.calculate_file_hash("nonexistent.txt")

    def test_invalid_config(self):
        invalid_config = os.path.join(self.test_dir, "invalid.yaml")
        with open(invalid_config, "w", encoding="utf-8") as f:
            f.write("invalid_key invalid_value")  # 使用有效但格式错误的YAML

        try:
            calculator = HashCalculator(invalid_config)
            # 验证是否使用了默认配置
            self.assertIsInstance(calculator.config, dict)
            self.assertTrue("algorithms" in calculator.config)
            self.assertTrue("performance" in calculator.config)
        except Exception as e:
            self._log_error("test_invalid_config", str(e))
            raise

    def test_multiple_files(self):
        try:
            calculator = HashCalculator(self.test_config)
            test_files = [self.test_files["normal.txt"], self.test_files["binary.dat"]]
            calculator.process_files(test_files, mode="info", format="json")
        except Exception as e:
            self._log_error("test_multiple_files", str(e))
            raise

    def test_chinese_filename(self):
        try:
            calculator = HashCalculator(self.test_config)
            result = calculator.calculate_file_hash(
                self.test_files["chinese中文.txt"], show_progress=False
            )
            self.assertIsInstance(result, dict)
        except Exception as e:
            self._log_error("test_chinese_filename", str(e))
            raise

    # 基础功能测试
    def test_basic_hash(self):
        calculator = HashCalculator(self.test_config)
        result = calculator.calculate_file_hash(self.test_files["normal.txt"])
        self.assertIsInstance(result, dict)
        self.assertTrue(all(algo in result for algo in ["MD5", "SHA1", "SHA256"]))

    # 通配符测试
    def test_wildcards(self):
        calculator = HashCalculator(self.test_config)
        patterns = [
            "*.txt",  # 基本通配符
            "test*.png",  # 前缀通配符
            "*dir*/*.txt",  # 目录通配符
            "**/*.txt",  # 递归通配符
            "subdir2/**/*.txt",  # 嵌套递归
            "[0-9]*.txt",  # 字符集通配符
        ]

        for pattern in patterns:
            pattern_path = os.path.join(self.test_dir, pattern)
            with self.subTest(pattern=pattern):
                try:
                    calculator.process_files([pattern_path], mode="info")
                except Exception as e:
                    self.fail(f"通配符 {pattern} 测试失败: {e}")

    # 特殊文件名测试
    def test_special_filenames(self):
        calculator = HashCalculator(self.test_config)
        special_files = [
            "chinese中文.txt",  # 中文文件名
            "space in name.txt",  # 空格
            "special!@#$%^&().txt",  # 特殊字符
            ".hidden",  # 隐藏文件
            "中文目录/test.txt",  # 中文路径
            "space dir/test.txt",  # 空格路径
        ]

        for filename in special_files:
            with self.subTest(filename=filename):
                file_path = self.test_files.get(filename)
                self.assertIsNotNone(file_path, f"测试文件 {filename} 未创建")
                result = calculator.calculate_file_hash(file_path)
                self.assertIsInstance(result, dict)

    # 边界情况测试
    def test_edge_cases(self):
        calculator = HashCalculator(self.test_config)
        tests = [
            ("empty.txt", "空文件"),
            ("large.dat", "大文件"),
            ("binary.dat", "二进制文件"),
            ("empty_dir", "空目录"),
        ]

        for filename, desc in tests:
            with self.subTest(desc=desc):
                if filename == "empty_dir":
                    dir_path = os.path.join(self.test_dir, filename)
                    with self.assertRaises(Exception):
                        calculator.calculate_file_hash(dir_path)
                else:
                    file_path = self.test_files[filename]
                    result = calculator.calculate_file_hash(file_path)
                    self.assertIsInstance(result, dict)

    # 路径测试
    def test_paths(self):
        calculator = HashCalculator(self.test_config)
        test_paths = [
            ("相对路径", "normal.txt"),
            ("绝对路径", os.path.abspath(self.test_files["normal.txt"])),
            ("嵌套路径", "subdir2/nested/deep1.txt"),
            ("父目录引用", "./subdir1/../subdir2/nested/deep1.txt"),
        ]

        for desc, path in test_paths:
            with self.subTest(desc=desc):
                try:
                    if not os.path.isabs(path):
                        path = os.path.join(self.test_dir, path)
                    result = calculator.calculate_file_hash(path)
                    self.assertIsInstance(result, dict)
                except Exception as e:
                    self.fail(f"{desc} 测试失败: {e}")

    # 错误情况测试
    def test_error_cases(self):
        calculator = HashCalculator(self.test_config)
        error_cases = [
            ("不存在的文件", "nonexistent.txt"),
            ("不存在的目录", "nonexistent/file.txt"),
            ("无权限目录", "/root/test.txt"),
            ("无效路径字符", "\0invalid.txt"),
        ]

        for desc, path in error_cases:
            with self.subTest(desc=desc):
                with self.assertRaises(Exception):
                    calculator.calculate_file_hash(path)

    def _create_comparison_files(self):
        """创建用于比较测试的文件"""
        test_content = b"test content"
        modified_content = b"modified content"

        files = {
            "original.txt": test_content,
            "identical.txt": test_content,
            "different.txt": modified_content,
            "empty.txt": b"",
        }

        paths = {}
        for name, content in files.items():
            path = os.path.join(self.test_dir, name)
            with open(path, "wb") as f:
                f.write(content)
            paths[name] = path

        return paths

    def test_compare_identical_files(self):
        """测试比较相同的文件"""
        try:
            comparison_files = self._create_comparison_files()
            calculator = HashCalculator(self.test_config)
            test_files = [
                comparison_files["original.txt"],
                comparison_files["identical.txt"],
            ]

            results = calculator.compare_files(test_files)

            self.assertIn("reference", results)
            self.assertIn("comparisons", results)
            self.assertEqual(len(results["comparisons"]), 1)

            # 验证所有哈希值都匹配
            comparison = results["comparisons"][0]
            self.assertTrue(all(comparison["matches"].values()))

        except Exception as e:
            self._log_error("test_compare_identical_files", str(e))
            raise

    def test_compare_different_files(self):
        """测试比较不同的文件"""
        try:
            comparison_files = self._create_comparison_files()
            calculator = HashCalculator(self.test_config)
            test_files = [
                comparison_files["original.txt"],
                comparison_files["different.txt"],
            ]

            results = calculator.compare_files(test_files)

            # 验证所有哈希值都不匹配
            comparison = results["comparisons"][0]
            self.assertTrue(not any(comparison["matches"].values()))

        except Exception as e:
            self._log_error("test_compare_different_files", str(e))
            raise

    def test_compare_output_formats(self):
        """测试比较结果的不同输出格式"""
        try:
            comparison_files = self._create_comparison_files()
            calculator = HashCalculator(self.test_config)
            test_files = [
                comparison_files["original.txt"],
                comparison_files["identical.txt"],
            ]

            for format in ["default", "json", "csv"]:
                with self.subTest(format=format):
                    results = calculator.compare_files(test_files)
                    calculator.format_comparison_output(results, format)

        except Exception as e:
            self._log_error("test_compare_output_formats", str(e))
            raise

    def test_compare_empty_files(self):
        """测试比较空文件"""
        try:
            comparison_files = self._create_comparison_files()
            calculator = HashCalculator(self.test_config)
            test_files = [comparison_files["empty.txt"], comparison_files["empty.txt"]]

            results = calculator.compare_files(test_files)
            comparison = results["comparisons"][0]
            self.assertTrue(all(comparison["matches"].values()))

        except Exception as e:
            self._log_error("test_compare_empty_files", str(e))
            raise

    def test_compare_error_handling(self):
        """测试比较模式的错误处理"""
        calculator = HashCalculator(self.test_config)

        # 测试文件数量不足
        with self.assertRaises(ValueError):
            calculator.compare_files(["single.txt"])

        # 测试文件不存在
        with self.assertRaises(Exception):
            calculator.compare_files(["nonexistent1.txt", "nonexistent2.txt"])

    def test_auto_verify_mode(self):
        """测试自动验证模式"""
        try:
            # 创建测试文件和对应的哈希文件
            test_data = b"test content"
            test_file = os.path.join(self.test_dir, "test.txt")
            with open(test_file, "wb") as f:
                f.write(test_data)

            # 创建各种哈希文件
            calculator = HashCalculator(self.test_config)
            hashes = calculator.calculate_file_hash(test_file, show_progress=False)

            for algo, value in hashes.items():
                hash_file = f"{test_file}.{algo.lower()}"
                with open(hash_file, "w") as f:
                    f.write(value)

            # 切换到测试目录并执行自动验证
            original_dir = os.getcwd()
            os.chdir(self.test_dir)
            try:
                calculator.auto_verify_files()
            finally:
                os.chdir(original_dir)

        except Exception as e:
            self._log_error("test_auto_verify_mode", str(e))
            raise

    def test_compare_with_wildcards(self):
        """测试带通配符的文件比较"""
        try:
            # 创建测试文件
            test_files = {
                "test1.png": b"content1",
                "test2.png": b"content1",  # 相同内容
                "test3.png": b"content2",  # 不同内容
            }

            for name, content in test_files.items():
                path = os.path.join(self.test_dir, name)
                with open(path, "wb") as f:
                    f.write(content)

            calculator = HashCalculator(self.test_config)

            # 测试通配符比较
            pattern = os.path.join(self.test_dir, "*.png")
            results = calculator.compare_files([pattern])

            self.assertFalse(results["all_match"])  # 应该有不匹配的文件
            self.assertEqual(len(results["comparisons"]), 2)  # 应该有两个比较结果

        except Exception as e:
            self._log_error("test_compare_with_wildcards", str(e))
            raise

    def test_compare_summary_messages(self):
        """测试比较结果的摘要消息"""
        try:
            # 创建相同的文件
            content = b"same content"
            files = ["file1.txt", "file2.txt"]
            for name in files:
                path = os.path.join(self.test_dir, name)
                with open(path, "wb") as f:
                    f.write(content)

            calculator = HashCalculator(self.test_config)

            # 测试匹配消息
            results = calculator.compare_files(
                [os.path.join(self.test_dir, f) for f in files]
            )
            self.assertTrue(results["all_match"])

            # 创建一个不同的文件
            with open(os.path.join(self.test_dir, "file3.txt"), "wb") as f:
                f.write(b"different content")

            # 测试不匹配消息
            results = calculator.compare_files(
                [
                    os.path.join(self.test_dir, "file1.txt"),
                    os.path.join(self.test_dir, "file3.txt"),
                ]
            )
            self.assertFalse(results["all_match"])

        except Exception as e:
            self._log_error("test_compare_summary_messages", str(e))
            raise

    def test_parse_hash_file_formats(self):
        """测试不同格式的哈希校验文件解析"""
        test_cases = {
            "gnu_single.md5": "d41d8cd98f00b204e9800998ecf8427e *test.txt",
            "gnu_multi.sha256": """
                e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 *file1.txt
                6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b *file2.txt
            """,
            "bsd_format.md5": "MD5 (test.txt) = d41d8cd98f00b204e9800998ecf8427e",
            "hash_only.md5": "d41d8cd98f00b204e9800998ecf8427e",
            "space_in_name.sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709 file with spaces.txt",
        }

        for filename, content in test_cases.items():
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, "w") as f:
                f.write(content.strip())

            try:
                calculator = HashCalculator(self.test_config)
                entries = calculator.parse_hash_file(filepath)
                self.assertTrue(len(entries) > 0)
                for entry in entries:
                    self.assertIn("filename", entry)
                    self.assertIn("hash", entry)
                    self.assertIn("binary", entry)
            except Exception as e:
                self._log_error(f"test_parse_hash_file_formats ({filename})", str(e))
                raise

    def test_hash_file_generation(self):
        """测试哈希文件生成功能"""
        try:
            # 修改工作目录到测试目录
            original_dir = os.getcwd()
            os.chdir(self.test_dir)

            try:
                # 创建自定义配置
                test_config = os.path.join(self.test_dir, "custom_config.yaml")
                config = {
                    "performance": {
                        "async_mode": True,
                        "buffer_size": 8388608,
                        "use_mmap": True,
                        "thread_count": 4,
                    },
                    "algorithms": {
                        "MD5": {"enabled": True},
                        "SHA1": {"enabled": True},
                        "SHA256": {"enabled": True},
                    },
                    "output": {
                        "color": False,
                        "progress_bar": False,
                        "show_time": True,
                        "format": "default",
                        "generate_hash_file": True,
                        "hash_file_format": "GNU",
                        "hash_file_encoding": "utf-8",
                    },
                    "file_handling": {
                        "recursive": False,
                        "retry_count": 3,
                        "ignore_errors": False,
                    },
                    "logging": {
                        "enabled": True,
                        "level": "DEBUG",
                        "file": os.path.join(self.test_dir, "test.log"),
                    },
                    "comparison": {
                        "match_message": "******✅ 所有文件哈希值相同******",
                        "mismatch_message": "******⚠️ 存在不一致的哈希值******",
                        "detail_format": "{file1} 与 {file2} 的 {algo} 值不同",
                    },
                }
                with open(test_config, "w") as f:
                    yaml.dump(config, f)

                calculator = HashCalculator(test_config)
                test_file = os.path.join(self.test_dir, "test_hash_gen.txt")

                # 创建测试文件
                with open(test_file, "wb") as f:
                    f.write(b"test content")

                # 计算哈希并生成校验文件
                calculator.calculate_file_hash(test_file)

                # 检查生成的文件
                self.assertTrue(os.path.exists("MD5SUMS"))
                self.assertTrue(os.path.exists("SHA1SUMS"))

                # 验证生成的哈希文件内容
                with open("MD5SUMS", "r") as f:
                    content = f.read()
                    self.assertIn("test_hash_gen.txt", content)

            finally:
                # 恢复原工作目录
                os.chdir(original_dir)

        except Exception as e:
            self._log_error("test_hash_file_generation", str(e))
            raise

    def test_auto_detect_hash_type(self):
        """测试哈希类型自动检测"""
        test_cases = {
            "MD5": "d41d8cd98f00b204e9800998ecf8427e",
            "SHA1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
            "SHA256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }

        calculator = HashCalculator(self.test_config)

        for expected_type, hash_value in test_cases.items():
            filename = f"test.{expected_type.lower()}"
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, "w") as f:
                f.write(hash_value)

            _, detected_type = calculator.is_hash_file(filepath)
            self.assertEqual(detected_type, expected_type)


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


if __name__ == "__main__":
    run_tests()
