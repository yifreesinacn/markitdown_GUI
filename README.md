<<<<<<< HEAD

# MarkItDown GUI 文档转换工具(图形界面程序)

=======

基于微软MarkItDown工具开发的图形界面应用程序，用于将各种文档格式转换为Markdown格式。

## 功能特点

> > > > > > > 240727e928bd969ba73331fb428c70d7d074906a

基于微软MarkItDown工具开发的图形界面应用程序，提供便捷的文档格式转换功能。

## 项目简介

MarkItDown GUI是一个基于Python和Tkinter开发的图形界面工具，它封装了微软的MarkItDown命令行工具，提供了友好的用户界面，使得文档转换变得简单易用。

## 主要功能

- **单文件转换**
  
  - 支持多种文档格式转换为Markdown
  - 实时预览转换结果
  - 可自定义输出目录
  - 支持保留原始格式

- **批量转换**
  
  - 支持多文件同时转换
  - 支持文件夹导入
  - 批量转换进度显示
  - 转换结果统计

- **格式支持**
  
  - PDF文档 (.pdf)
  - Word文档 (.docx)
  - Excel文档 (.xlsx)
  - PowerPoint文档 (.pptx)
  - 图片文件 (.png, .jpg, .jpeg)
  - 音频文件 (.mp3, .wav)
  - HTML文件 (.html)
  - 文本文件 (.csv, .json, .xml)
  - 压缩文件 (.zip)

## 技术特点

- 使用Python 3.13+开发
- 基于Tkinter构建GUI界面
- 集成微软MarkItDown工具
- 多线程处理保证界面响应
- 支持配置持久化

### 创建环境

- Windows 10版本
- Python 3.13版本
- 8GB内存
- 500MB可用磁盘空间

### 运行环境

- Windows 10或更高版本
- Python 3.8或更高版本
  <<<<<<< HEAD
- 4GB以上内存
- 500MB可用磁盘空间

### 安装使用

1. 下载发布版本
   
   (1)从Release页面下载最新的exe文件
   (2)从网盘下载

3. 解压到任意目录

4. 运行MarkItDown_GUI.exe

### 详细文档

- [安装说明](docs/installation.md)
- [使用教程](docs/usage.md)
- [开发指南](docs/development.md)

### 依赖库：

- markitdown

- python-docx

- pdfminer.six

- Pillow

- pywin32
  
  ## 文件下载地址

- 1.本站：[MarkItDown_GUI_v0.1.1](https://github.com/yihufree/markitdown_GUI/releases/download/v0.1.0_250325/MarkItDown_GUI_v0.1.1_250325.zip)

- 2.网盘：[百度网盘](https://pan.baidu.com/s/1WhnLy0MOH4nWss54G4OYAQ) 提取码: 1234 。
  
  ## 更新

- v0.1.1_250325 1.修正了一些小问题；2.有图片的doc、pdf文档，在目录内新建images文件夹，导出并链接原文档中图片，请勿删除；3.修改了一些细节。

- v0.1.0_250323 1.修正了以前没有发现的问题，如doc文档不能转换等。2.对于有图片的doc文档，能在目录文件夹内建立图片目录，将原文档中图片导出。3.在配置框内对支持的文件类型进行说明。4.修改了一些细节

- v0.1.0a1    2025年3月11日根据微软发布的新版本进行修改，微软版本为发0.1.0a1。其他无大的变动。目前存在的问题：一是部分大文件转换会失败；二是部分图形图像方面还存在问题，打包时有提示；三是后续考虑增加英文界面，方便更多的人使用。

- v1.0    2025年3月5日第一次发布第一个版本，版本号为1.0 （当时微软在github.com发布的markitdown版本为v0.0.2a1，在pypi发布的版本好像是v0.0.1a5）
  
  > > > > > > > 240727e928bd969ba73331fb428c70d7d074906a
