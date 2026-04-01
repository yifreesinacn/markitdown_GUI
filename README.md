<<<<<<< HEAD

# AnyToMarkdown （AnyToMD) 文档转换工具

=======

## 项目简介

AnyToMarkdown（AnyToMD）是一个基于Python和Tkinter开发的图形界面工具，它封装了微软的MarkItDown命令行工具以及其他一些工具库，提供了友好的用户界面，使得文档转换变得简单易用。

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
  - HTML文件 (.html, MHTML, HTM)
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
- Python 3.10或更高版本
  <<<<<<< HEAD
- 4GB以上内存
- 500MB可用磁盘空间

### 安装使用

1. 下载发布版本
   
  从Release页面下载最新的exe文件(或压缩包)
  
3. （如果是压缩包）解压到任意目录

4. 运行 *.exe 可执行文件

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

- 等等
  
  ## 文件下载地址

- 本站：[ AnyToMD_v0.1.6 ](https://github.com/yihufree/AnyToMarkdown/releases/download/v0.1.6_260330/AnyToMD_v0.1.6_260330.exe)

  目前V0.1.6版本的源码还没有完全整理好，先下载EXE程序试用，暂时不要下载源码。
  
  ## 更新

-2026年3月31日：
抽空对程序进行了一些调整。
  - 一是更多了解了前期体积增大的原因（微软 MarkItDown 0.1.0 后的版本中引入了 magika ，而 magika 依赖了 onnxruntime 库，包含非常大的 C++ 动态链接库（约 150MB+）。另外打包时可能 涉及到了torch 、 scipy 、 sklearn 、 cv2 (OpenCV)、 PyQt5 等。）近期进行了调整。
  - 二是增加了对MHTML/HTM支持。
  - 三是转换质量有提升，尤其是PDF、HTML文档中的图片保留能力有了提升。
  - 四是提供了一些转换选项，满足更加灵活的需求。
  - 现在的程序速度更快、支持的文档转换质量更高。

2025年6月16日：
- 近期发现使用原来的脚本和主程序打包后文件为361M，发现是markitdown及相关依赖中加入了大量额外的依赖模块，主要是：
  (1)深度学习框架 ：包含了torch、transformers、huggingface_hub等大型机器学习库
  (2)科学计算库 ：包含了更完整的numpy、scipy、pandas、matplotlib等科学计算生态
  (3)图像处理库 ：包含了更多的PIL、opencv相关模块
  (4)云服务依赖 ：包含了azure、google.auth等云服务相关库
  因对以上内容不熟悉，请大家自行处理。（20250616）
  
- 上传了打包脚本文件AnyToMD_build.py，有兴趣的朋友可以放在同一目录，使用“ python AnyToMD_build.py "测试。我也只是学着玩，所以没有建立专门的依赖文件，直接使用打包文件打包，里面有具体的依赖名称。使用前先把微软的markitdown项目运行一下（https://github.com/microsoft/markitdown  可以下载到本地，使用pip install 'markitdown[all]'，不行的使用pip install markitdown[all），然后再打包。
- 如果本应用基于的一些库没有大的变动，转换工具涉及的图片的插入问题没有得到彻底解决，这个程序近期可能也不会做大的更新
  
- v0.1.1_250325 1.修正了一些小问题；2.有图片的doc、pdf文档，在目录内新建images文件夹，导出并链接原文档中图片，请勿删除；3.修改了一些细节。

- v0.1.0_250323 1.修正了以前没有发现的问题，如doc文档不能转换等。2.对于有图片的doc文档，能在目录文件夹内建立图片目录，将原文档中图片导出。3.在配置框内对支持的文件类型进行说明。4.修改了一些细节

- v0.1.0a1    2025年3月11日根据微软发布的新版本进行修改，微软版本为发0.1.0a1。其他无大的变动。目前存在的问题：一是部分大文件转换会失败；二是部分图形图像方面还存在问题，打包时有提示；三是后续考虑增加英文界面，方便更多的人使用。

- v1.0    2025年3月5日第一次发布第一个版本，版本号为1.0 （当时微软在github.com发布的markitdown版本为v0.0.2a1，在pypi发布的版本好像是v0.0.1a5）
  
  > > > > > > > 240727e928bd969ba73331fb428c70d7d074906a
