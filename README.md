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
| 计算模式 `-i`(input) | 计算单个/多个文件的哈希值                                            | `hash -i file.txt *.zip`          |
| 比较模式 `-s`(same ) | 比较多个文件的哈希值是否一致                                          | `hash -s file1 file2`             |
| 验证模式 `-a`(auto ) | 自动匹配验证当前目录下的哈希文件（如`file.md5`与`file.txt`）          | `hash -a`                         |


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
  # 支持的算法(hashlib)：MD5, SHA1, SHA256, BLAKE2b等
  # 更多信息，请查看 Python 文档：https://docs.python.org/3/library/hashlib.html
  # `hash -a`自动校验模式不受此处配置影响，程序会临时启用被禁用的算法进行校验
```
#### 查询可使用的算法
```python
print(hashlib.algorithms_available)  # 当前环境中可用的所有算法
print(hashlib.algorithms_guaranteed)  # Python 内置保证支持的算法
```

### 3. 比较模式配置 (comparison)
```yaml
comparison:
  match_message: "******✅ 所有文件哈希值相同******"    # 可自定义匹配成功消息
  mismatch_message: "******⚠️ 存在不一致的哈希值******" # 可自定义匹配失败消息
  detail_format: "{file1} 与 {file2} 的 {algo} 值不同"  # 可自定义差异详情格式
```
### 4. 自动校验模式说明
- 支持的哈希校验文件格式：
   - | 格式类型               | 描述                                                                 | 示例                                                |
   |------------------------|----------------------------------------------------------------------|-----------------------------------------------------|
   | **标准格式**           | `[哈希值] [文件名]`，最常见和基础的格式。                              | `d41d8cd98f00b204e9800998ecf8427e example_file.txt` |
   | **带星号标记二进制模式** | 二进制模式读取的文件，文件名前有一个星号 (`*`)。                | `da39a3ee5e6b4b0d3255bfef95601890afd80709 *example_file.bin` |
   | **无文件名**            | 仅包含哈希值。                         | `d41d8cd98f00b204e9800998ecf8427e`                 |
   | **多文件校验文件**      | 每行代表一个文件及其对应的哈希值。           | <pre><code>hash1 file1.txt<br>hash2 file2.jpg<br>hash3 file3.pdf</code></pre> |

- 自动校验模式会自动搜索当前目录下的哈希文件，并自动进行哈希值校验
   - 如果哈希校验文件中包含文件名（如 `[哈希值] [文件名]`），程序会优先使用该文件名进行匹配。
     - 示例：如果 `example.md5` 文件中存储的内容是 `d41d8cd98f00b204e9800998ecf8427e xxx.txt`，程序会优先查找并匹配 `xxx.txt`。
   - 如果哈希校验文件中未包含文件名（如 `[哈希值]`），程序会尝试将哈希文件的文件名作为目标文件名进行匹配。
     - 示例：如果 `example.md5` 文件中只包含 `d41d8cd98f00b204e9800998ecf8427e`，程序会优先查找名为 `example.*` 的文件。
- 如果存在不一致的哈希值，程序会自动进行差异比较，并输出详细的比较结果。

### 5. 输出配置 (output)
```yaml
output:
  color: true        # 启用彩色输出
  progress_bar: true # 显示进度条
  show_time: true    # 显示处理时间
  format: "default"  # 输出格式 (default/json/csv)
```

### 6. 文件处理配置 (file_handling)
```yaml
file_handling:
  recursive: false   # 是否递归处理子目录
  retry_count: 3    # 读取失败重试次数
  ignore_errors: false # 是否忽略错误继续执行
```

### 7. 排除规则 (exclude_patterns)
```yaml
exclude_patterns:
  - "*.tmp"         # 排除临时文件
  - "*.temp"
  - "~*"
```

### 8. 日志配置 (logging)
```yaml
logging:
  enabled: false     # 启用日志
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
