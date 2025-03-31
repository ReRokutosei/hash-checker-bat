# 文件哈希计算工具

一个高性能的文件哈希计算工具，支持多种哈希算法、异步处理和灵活的配置选项。

## 功能特点

- 支持多种哈希算法 (MD5, SHA1, SHA256, SHA3_256, BLAKE2b)
- 异步处理和多线程支持
- 内存映射技术处理大文件
- 可自定义的缓冲区大小
- 支持多种输出格式 (默认/JSON/CSV)
- 进度条显示
- 彩色输出支持
- 详细的日志记录
- 可配置的文件处理选项

## 安装要求

- Python 3.8 +
- 依赖包：
  ```bash
  pip install pyyaml tqdm colorama
  ```

## 快速开始

1. 克隆仓库：
   ```bash
   git clone https://github.com/ReRokutosei/hash-checker-bat.git
   cd hash
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 运行工具：
   ```bash
   python hash.py -i file.txt          # 计算单个文件哈希值
   python hash.py -i *.txt             # 计算多个文件哈希值
   python hash.py -s file1.txt file2.txt  # 比较两个文件
   ```

## 配置说明

配置文件 (config.yaml) 包含以下主要部分：

### 性能配置
```yaml
performance:
  async_mode: true          # 是否启用异步模式
  buffer_size: 8388608      # 读取缓冲区大小(8MB)
  use_mmap: true           # 是否使用mmap处理大文件
  thread_count: 4          # 线程池大小
```

### 算法选择
```yaml
algorithms:
  - MD5
  - SHA1
  - SHA256
  - SHA3_256
  - BLAKE2b
```

### 输出设置
```yaml
output:
  color: true              # 启用彩色输出
  progress_bar: true       # 显示进度条
  show_time: true         # 显示处理时间
  format: "default"        # 输出格式(default/json/csv)
```

### 文件处理
```yaml
file_handling:
  recursive: false         # 是否递归扫描子目录
  retry_count: 3          # 文件读取失败重试次数
  ignore_errors: false    # 是否忽略错误继续执行
```

## 性能优化建议

1. 大文件处理
   - 启用 `use_mmap: true`
   - 设置合适的 `buffer_size`（建议 8MB）
   - 开启异步模式 `async_mode: true`

2. 批量小文件处理
   - 增加 `thread_count`
   - 启用异步模式
   - 根据CPU核心数调整线程数

3. 内存受限环境
   - 减小 `buffer_size`
   - 禁用 `use_mmap`
   - 减少同时处理的线程数

## 输出格式示例

### 默认格式
```
文件: example.txt
--------------------------------------
MD5:    d41d8cd98f00b204e9800998ecf8427e
SHA1:   da39a3ee5e6b4b0d3255bfef95601890afd80709
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
--------------------------------------
```

### JSON格式
```json
{
  "file": "example.txt",
  "hashes": {
    "MD5": "d41d8cd98f00b204e9800998ecf8427e",
    "SHA1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
    "SHA256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  }
}
```

### CSV格式
```
file,md5,sha1,sha256
example.txt,d41d8cd98f00b204e9800998ecf8427e,da39a3ee5e6b4b0d3255bfef95601890afd80709,e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## 开发者工具

项目包含两个测试工具：

1. `test_hash.py`: 基础功能测试
   ```bash
   python test_hash.py
   ```

2. `test_config.py`: 配置性能测试
   ```bash
   python test_config.py
   ```

## 许可证

本项目采用 MIT 许可证。查看 [LICENSE](LICENSE) 文件了解更多详细信息。
