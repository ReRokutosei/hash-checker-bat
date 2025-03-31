# 文件哈希计算工具

CMD与PowerShell内置计算哈希值的工具虽然强大但不方便，因此使用python简化，提高效率。

## 主要功能

- 三种工作模式：
  - 计算模式 (-i): 计算一个或多个文件的哈希值
  - 比较模式 (-s): 比较多个文件的哈希值是否相同
  - 验证模式 (-a): 自动验证当前目录下的哈希校验文件

- 文件处理特性：
  - 支持通配符匹配文件
  - 支持递归目录处理
  - 支持大文件处理
  - 支持多文件并行处理

- 输出特性：
  - 彩色输出支持
  - 进度条显示
  - 多种输出格式 (默认/JSON/CSV)
  - 详细的比较结果

## 安装和使用

### 环境要求
- Python 3.8 或更高版本
- 依赖包：pyyaml, tqdm, colorama

### 配置项目
```bash
git clone https://github.com/ReRokutosei/hash-checker-bat.git
cd hash-checker-bat
pip install -r requirements.txt # 安装依赖
export PATH="$PATH:$(pwd)" # 将当前目录添加到环境变量
```

### 基本用法
| 模式       | 描述                                                                 | 命令示例                          |
|------------|----------------------------------------------------------------------|-----------------------------------|
| 计算模式 `-i` | 计算单个/多个文件的哈希值                                            | `hash -i file.txt *.zip`          |
| 比较模式 `-s` | 比较多个文件的哈希值是否一致                                          | `hash -s file1 file2`             |
| 验证模式 `-a` | 自动验证当前目录下所有哈希校验文件（如`.md5`, `.sha256`等）          | `hash -a`                         |


## 配置文件详解

配置文件（config.yaml）支持以下配置项：

### 1. 性能配置 (performance)
```yaml
performance:
  async_mode: true    # 启用异步处理模式
  buffer_size: 8388608 # 读取缓冲区大小(8MB)
  use_mmap: true     # 使用内存映射读取大文件
  thread_count: 4    # 并行处理线程数
```

### 2. 哈希算法配置 (algorithms)
```yaml
algorithms:
  MD5:               # 算法名称
    enabled: true    # 是否启用
    compare_format: "{filename}: {value}"  # 比较输出格式
  SHA1:
    enabled: true
    compare_format: "{filename}: {value}"
  # 支持的算法：MD5, SHA1, SHA256, SHA3_256, BLAKE2b, SHA384, SHA3_384, SHA512 等
```
#### 查询可使用的算法
```python
print(hashlib.algorithms_available)  # 当前环境中可用的所有算法
print(hashlib.algorithms_guaranteed)  # Python 内置保证支持的算法
```

### 3. 比较模式配置 (comparison)
```yaml
comparison:
  match_message: "******✅ 所有文件哈希值相同******"    # 自定义匹配成功消息
  mismatch_message: "******⚠️ 存在不一致的哈希值******" # 自定义匹配失败消息
  detail_format: "{file1} 与 {file2} 的 {algo} 值不同"  # 自定义差异详情格式
```

### 4. 输出配置 (output)
```yaml
output:
  color: true        # 启用彩色输出
  progress_bar: true # 显示进度条
  show_time: true    # 显示处理时间
  format: "default"  # 输出格式 (default/json/csv)
```

### 5. 文件处理配置 (file_handling)
```yaml
file_handling:
  recursive: false   # 是否递归处理子目录
  retry_count: 3    # 读取失败重试次数
  ignore_errors: false # 是否忽略错误继续执行
```

### 6. 排除规则 (exclude_patterns)
```yaml
exclude_patterns:
  - "*.tmp"         # 排除临时文件
  - "*.temp"
  - "~*"
```

### 7. 日志配置 (logging)
```yaml
logging:
  enabled: true     # 启用日志
  level: "INFO"     # 日志级别
  file: "hash_calculator.log" # 日志文件路径
```

## 配置优化建议

### 大文件处理优化
- 启用 mmap: `use_mmap: true`
- 设置合适的缓冲区: `buffer_size: 8388608`
- 禁用不必要的算法以减少计算量

### 批量小文件处理优化
- 启用异步模式: `async_mode: true`
- 增加线程数: `thread_count: 8`
- 启用递归处理: `recursive: true`

### 内存受限环境优化
- 禁用 mmap: `use_mmap: false`
- 减小缓冲区: `buffer_size: 1048576`
- 减少线程数: `thread_count: 2`

## 测试说明
### 运行测试

```bash
# 执行全部单元测试
python test_unit.py

# 运行配置压力测试
python test_config.py
```

###  测试覆盖
文件类型：文本、二进制、空文件、中文命名文件
边界情况：无效路径、权限问题、递归通配符
性能验证：不同配置组合的执行时长测试

## 许可证
本项目采用 MIT 许可证。查看 [LICENSE](LICENSE) 文件了解更多详细信息。
