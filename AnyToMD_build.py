import os
import subprocess
import sys
import importlib.util
import site

def check_dependencies():
    """检查依赖是否安装，如果没有安装则提示安装"""
    # 需要检查的库
    required_libraries = [
        'python-docx',  # 用于处理Word文档
        'pdf2image',    # 用于PDF转图片
        'python-pptx',  # 用于处理PPT
        'beautifulsoup4', # 用于解析HTML
        'requests',     # 用于下载网络图片
        'pillow',       # 图像处理
        'pdfplumber',   # PDF文本提取,20250324新增
        'PyPDF2',       # PDF处理，20250324新增
        'html2text',    # HTML转Markdown，20250324新增
        'pywin32',      # Windows COM接口，20250324新增    
        'pypdfium',   # 20250324自己添加
        'pypdfium2',   # 20250324自己添加
    ]
    # 20250324新增
    # 可选但推荐的库
    optional_libraries = [
        'pandoc',       # 强大的文档转换工具
        'textract',
    ]
    #20250324新增结束

    
    missing_libraries = []
    
    for lib in required_libraries:
        try:
            if lib == 'python-docx':
                import docx
                print(f"✓ docx 库已安装，版本: {getattr(docx, '__version__', '未知')}")
            elif lib == 'pdf2image':
                import pdf2image
                print(f"✓ pdf2image 库已安装，版本: {getattr(pdf2image, '__version__', '未知')}")
            elif lib == 'python-pptx':
                import pptx
                print(f"✓ pptx 库已安装，版本: {getattr(pptx, '__version__', '未知')}")
            elif lib == 'beautifulsoup4':
                import bs4
                print(f"✓ beautifulsoup4 库已安装，版本: {bs4.__version__}")
            elif lib == 'requests':
                import requests
                print(f"✓ requests 库已安装，版本: {requests.__version__}")
            elif lib == 'pillow':
                from PIL import Image
                import PIL
                print(f"✓ pillow 库已安装，版本: {PIL.__version__}")
        except ImportError:
            missing_libraries.append(lib)
            print(f"✗ {lib} 库未安装")
    
    # 检查poppler是否安装（pdf2image的依赖）
    try:
        from pdf2image.pdf2image import pdfinfo_from_path
        print("✓ pdf2image可用且poppler路径可能已正确配置")
    except:
        print("✗ poppler可能未安装或路径未正确配置。这是pdf2image的必需依赖。")
        print("  Windows用户：从https://github.com/oschwartz10612/poppler-windows/releases下载并配置")
        print("  Linux用户：使用包管理器安装，如：sudo apt-get install poppler-utils")
        print("  macOS用户：使用Homebrew安装，如：brew install poppler")
    
    # 检查是否存在图标文件
    if not os.path.exists('icon.ico'):
        print("✗ 警告：未找到icon.ico文件，将使用默认图标")
    else:
        print("✓ 图标文件已找到")
    
    # 如果有缺失的库，提示安装
    if missing_libraries:
        print("\n需要安装以下Python库:")
        for lib in missing_libraries:
            print(f"  pip install {lib}")
        
        # 询问是否自动安装
        choice = input("\n是否自动安装缺失的库? (y/n): ").strip().lower()
        if choice == 'y':
            for lib in missing_libraries:
                print(f"正在安装 {lib}...")
                os.system(f"pip install {lib}")
                print(f"{lib} 安装完成")
        else:
            print("请手动安装缺失的库后再运行")
            return False
    
    return True

def get_markitdown_path():
    """获取markitdown包的路径"""
    try:
        import markitdown
        markitdown_path = os.path.dirname(markitdown.__file__)
        print(f"找到markitdown路径: {markitdown_path}")
        return markitdown_path
    except ImportError:
        print("无法导入markitdown，请确保已正确安装")
        return None

def test_pdf2image():
    """测试pdf2image是否正常工作（无需实际调用poppler）"""
    try:
        import pdf2image
        print("pdf2image 模块已加载")
        
        # 仅检查模块是否存在必要的函数，不实际调用
        if hasattr(pdf2image, 'convert_from_path') and hasattr(pdf2image, 'convert_from_bytes'):
            print("pdf2image 基本功能正常")
        else:
            print("警告: pdf2image 似乎缺少某些功能")
        
        return True
    except Exception as e:
        print(f"pdf2image 测试失败: {str(e)}")
        return False

def build_executable():
    """执行打包命令"""
    # 获取markitdown路径
    markitdown_path = get_markitdown_path()
    
    # 构建基本命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--icon=icon.ico",
        "--add-data", "icon.ico;.",
        # markitdown 相关导入
        "--hidden-import", "markitdown",
    ]
    
    # 如果找到markitdown路径，添加其子模块
    if markitdown_path:
        # 添加markitdown的所有子模块
        for root, dirs, files in os.walk(markitdown_path):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    module_name = os.path.splitext(file)[0]
                    full_module = f"markitdown.{module_name}"
                    cmd.extend(["--hidden-import", full_module])
                    print(f"添加隐藏导入: {full_module}")
    
    # 添加其他必要的隐藏导入
    additional_imports = [
        # 文档处理相关导入
        "docx",
        "docx2python",
        "pdfminer",
        "PIL",
        "openpyxl",
        "pptx",
        "bs4",
        "lxml",
        "pytesseract",
        "pdf2image",  # 确保pdf2image被正确导入
        "pdf2image.pdf2image",  # pdf2image的主模块
        "pydub",
        "speech_recognition",
        # 系统相关导入
        "win32api",
        "win32con",
        # COM相关导入
        "win32com",
        "win32com.client",
        "pythoncom",
        # 图像处理相关
        "PIL.Image",
        "PIL.ExifTags",
        # PDF处理相关
        "pdfminer.high_level",
        "pdfminer.layout",
        # 音频处理相关
        "pydub.AudioSegment",
        # OCR相关
        "pytesseract.pytesseract",
    ]
    
    for imp in additional_imports:
        cmd.extend(["--hidden-import", imp])
    
    # 添加打包设置
    cmd.extend([
        # 打包设置
        "--clean",
        "--name=AnyToMD_v0.1.1_250409",
        "AnyToMD_v0.1.1_250409.py",
    ])
    
    # 收集完整的包
    collect_packages = [
        "markitdown",
        "docx",
        "docx2python",
        "pdfminer",
        "openpyxl",
        "pptx",
        "bs4",
        "lxml",
        "win32com",
        "PIL",
        "pytesseract",
        "pdf2image",  # 确保收集pdf2image包
        "pydub",
        "speech_recognition",
    ]
    
    for pkg in collect_packages:
        cmd.extend(["--collect-all", pkg])
    
    try:
        print("开始打包，这可能需要几分钟...")
        # 在打包前再次测试pdf2image功能
        if test_pdf2image():
            print("pdf2image功能验证通过，继续打包...")
        else:
            print("警告: pdf2image功能测试失败，打包可能不完整")
            response = input("是否继续打包? (y/n): ")
            if response.lower() != 'y':
                print("打包已取消")
                sys.exit(0)
                
        subprocess.run(cmd, check=True)
        print("\n打包成功！EXE文件位于 dist 目录")
        print(f"完整路径: {os.path.abspath('dist/AnyToMD_v0.1.1_250409.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    check_dependencies()
    build_executable()
    input("按回车键退出...")

