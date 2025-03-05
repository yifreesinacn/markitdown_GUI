# MarkItDown GUI 安装说明

## 系统要求

### 硬件要求

- CPU: 1.6GHz及以上
- 内存: 4GB及以上
- 硬盘: 500MB可用空间

### 软件要求

- 操作系统: Windows 10或更高版本
- Python环境: Python 3.8或更高版本（如果从源码运行）
- 依赖组件: Visual C++ Redistributable 2015-2019

## 安装方式

### 1. 使用发布版本（推荐）

1. 下载最新版本的MarkItDown_GUI.zip
2. 解压到任意目录
3. 运行MarkItDown_GUI.exe

注意：首次运行时Windows可能会显示安全警告，选择"仍要运行"即可。

### 2. 从源码安装

1. 确保已安装Python 3.8或更高版本

2. 安装所需依赖：
   
   ```bash
   pip install markitdown
   pip install python-docx
   pip install pdfminer.six
   pip install Pillow
   pip install pywin32
   ```

3. 运行程序：
   
   ```bash
   python MarkItDown_GUI_1.0.py
   ```

## 依赖项说明

### 核心依赖

- markitdown: 微软文档转换工具
- python-docx: Word文档处理
- pdfminer.six: PDF文档处理
- Pillow: 图像处理
- pywin32: Windows系统接口

### 可选依赖

- pyinstaller: 用于打包（仅开发时需要）

## 配置说明

### 程序配置文件

位置：`%USERPROFILE%\.markitdown_gui_settings.json`

包含以下设置：

- 默认输出目录
- 界面选项
- 转换选项

### 环境变量

程序不需要特殊的环境变量配置。

## 升级说明

### 从旧版本升级

1. 备份个人设置：
   
   - 复制 `.markitdown_gui_settings.json`

2. 卸载旧版本：
   
   - 删除程序目录
   - 保留设置文件

3. 安装新版本：
   
   - 解压新版本
   - 恢复设置文件

### 版本兼容性

- 配置文件向后兼容
- 转换结果格式保持一致
- 不同版本可并存运行

## 故障排除

### 常见安装问题

1. 程序无法启动
   
   - 检查是否安装Visual C++ Redistributable
   - 确认Windows版本是否满足要求
   - 检查是否有管理员权限

2. 依赖安装失败
   
   ```bash
   # 尝试使用清华源
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

3. 配置文件问题
   
   - 删除配置文件重新生成
   - 检查文件权限

### 日志位置

- 程序运行日志：`程序目录/logs/`
- 转换日志：`输出目录/convert_log.txt`

## 卸载说明

1. 删除程序文件：
   
   - 删除程序目录
   - 删除桌面快捷方式

2. 删除配置文件：
   
   ```
   %USERPROFILE%\.markitdown_gui_settings.json
   ```

3. 删除日志文件（可选）：
   
   - 删除logs目录

4. 清理注册表（可选）：
   -