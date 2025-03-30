# Hash Calculator

一个简单的命令行工具，用于计算和比较文件的哈希值（MD5、SHA1、SHA256）。

## 功能特点

- 支持计算单个或多个文件的哈希值
- 支持比较多个文件的哈希值是否相同
- 支持通配符匹配文件
- 支持带空格的文件名
- 支持中文文件名
- 支持相对路径和绝对路径

## 安装配置

1. 下载 `hash.bat` 文件
2. 配置系统PATH环境变量
3. 打开命令提示符(cmd)，输入 `hash` 验证是否安装成功

## 使用方法

### 1. 计算哈希值

```batch
hash -i <文件名>              # 计算单个文件的哈希值
hash -i <文件名1> <文件名2>   # 计算多个文件的哈希值
hash -i *.txt                # 计算所有txt文件的哈希值
```

示例：
```batch
hash -i example.txt
hash -i "my file.txt"
hash -i file1.txt file2.txt file3.txt
hash -i *.txt *.pdf
```

### 2. 比较哈希值

```batch
hash -s <文件名1> <文件名2>   # 比较两个文件的哈希值
hash -s *.txt                # 比较所有txt文件的哈希值
```

示例：
```batch
hash -s original.txt copy.txt
hash -s "file 1.txt" "file 2.txt"
hash -s *.txt
```

## 使用说明

1. 命令格式
   - `-i` 模式：计算文件哈希值
   - `-s` 模式：比较文件哈希值（需要至少两个文件）

2. 支持的文件名格式
   - 普通文件名：`example.txt`
   - 带空格文件名：`"my document.txt"`
   - 中文文件名：`"测试文件.txt"`
   - 带路径的文件名：`"C:\Files\example.txt"` 或 `..\folder\file.txt`
   - 通配符：`*.txt`、`test*.dat`

3. 输出信息
   - MD5 哈希值
   - SHA1 哈希值
   - SHA256 哈希值
   - 文件比较结果（仅比较模式）

## 注意事项

1. 文件名包含空格时需要使用引号括起来
2. 比较模式（-s）必须提供至少两个文件
3. 不支持文件名带感叹号（!）的文件
4. 不支持递归扫描子目录
5. 不支持拖放文件到命令行窗口

## 依赖条件

- Windows 操作系统
- 需要系统内置的 certutil 工具（Windows 默认已安装）

## 版权和许可

[选择合适的开源许可证]

## 贡献

欢迎提交 Issue 和 Pull Request
