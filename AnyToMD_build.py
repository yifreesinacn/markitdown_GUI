import os
import subprocess
import sys
import importlib.util
import site
import glob
import datetime  # 2026-04-01 16:45:00 修改：用于“固定内容+日期”的输出文件名
import re  # 2026-04-01 16:45:00 修改：用于从主文件名解析版本号

def _parse_version_from_main_filename(main_filename: str) -> str:  # 2026-04-01 16:45:00 修改：从主文件名解析版本号用于打包输出名称
    basename = os.path.basename(str(main_filename or ""))
    match = re.search(r'_v(\d+(?:\.\d+)+)', basename)
    if not match:
        return "0.0.0"
    parts = match.group(1).split(".")
    normalized_parts = []
    for part in parts:
        try:
            normalized_parts.append(str(int(part)))
        except Exception:
            break
    while len(normalized_parts) < 3:
        normalized_parts.append("0")
    return ".".join(normalized_parts[:3])

def _get_app_version_from_source(main_script: str) -> str:  # 2026-09-02 修改：主文件改为固定名 AnyToMD_main.py 后，版本号从源码中的 APP_VERSION 常量读取
    """从主程序源码读取 APP_VERSION 常量作为打包版本号（主文件名不再包含版本号）"""
    try:
        with open(str(main_script), encoding="utf-8") as f:
            content = f.read()
        match = re.search(r'^APP_VERSION\s*=\s*["\'](\d+\.\d+(?:\.\d+)?)["\']', content, re.MULTILINE)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"警告: 无法从 {main_script} 读取 APP_VERSION: {e}")
    # 降级：回退到旧的文件名解析（对无版本文件名将返回 0.0.0）
    return _parse_version_from_main_filename(main_script)

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
        'pypdfium2',   # 2026-03-29 14:14:24 修改：与requirements对齐，统一使用pypdfium2
        'customtkinter',
        'markitdown',   # 2026-03-29 14:14:24 修改：构建/运行关键依赖检查补齐
        'pyinstaller',  # 2026-03-29 14:14:24 修改：构建关键依赖检查补齐
        'docx2python',  # 2026-09-01 新增：.doc 格式备用提取（此前缺失导致功能检查显示未支持）
        'pytesseract',  # 2026-09-01 新增：OCR 文字识别包装器（此前缺失导致功能检查显示未支持）
        'firecrawl-anydoc',  # 2026-09-01 新增：AnyDoc 兜底引擎
        'pdf-inspector',     # 2026-09-01 新增：pdf-inspector 引擎
        'magika',            # 2026-09-02 新增：MarkItDown 0.1.7 硬依赖（缺失会导致版本/引擎显示 unknown）
        'onnxruntime',       # 2026-09-02 新增：magika 的 ML 推理依赖，需随 magika 一起打包
    ]
    # 20250324新增
    # 可选但推荐的库
    optional_libraries = [
        'pandoc',       # 强大的文档转换工具
        'textract',
    ]
    #20250324新增结束

    
    missing_libraries = []
    import importlib  # 2026-03-29 14:14:24 修改：补齐通用依赖检查，避免列表中大量库未被实际校验
    module_name_map = {  # 2026-03-29 14:14:24 修改：包名与导入名映射
        'python-docx': 'docx',
        'python-pptx': 'pptx',
        'beautifulsoup4': 'bs4',
        'pillow': 'PIL',
        'pyinstaller': 'PyInstaller',
        'pywin32': 'win32api',
        'firecrawl-anydoc': 'anydoc',   # 2026-09-01 新增：PyPI 包名 firecrawl-anydoc，导入名 anydoc
        'pdf-inspector': 'pdf_inspector',  # 2026-09-01 新增：PyPI 包名 pdf-inspector，导入名 pdf_inspector
    }
    
    for lib in required_libraries:
        try:
            module_name = module_name_map.get(lib, lib)  # 2026-03-29 14:14:24 修改：统一按映射导入
            module = importlib.import_module(module_name)  # 2026-03-29 14:14:24 修改：通用导入检查
            if lib == 'python-docx':
                print(f"✓ docx 库已安装，版本: {getattr(module, '__version__', '未知')}")
            elif lib == 'pdf2image':
                print(f"✓ pdf2image 库已安装，版本: {getattr(module, '__version__', '未知')}")
            elif lib == 'python-pptx':
                print(f"✓ pptx 库已安装，版本: {getattr(module, '__version__', '未知')}")
            elif lib == 'beautifulsoup4':
                print(f"✓ beautifulsoup4 库已安装，版本: {getattr(module, '__version__', '未知')}")
            elif lib == 'requests':
                print(f"✓ requests 库已安装，版本: {getattr(module, '__version__', '未知')}")
            elif lib == 'pillow':
                print(f"✓ pillow 库已安装，版本: {getattr(module, '__version__', '未知')}")
            else:
                print(f"✓ {lib} 库已安装")
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
                subprocess.run([sys.executable, "-m", "pip", "install", lib], check=True)
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

def _collect_native_extension_binaries(cmd):  # 2026-09-02 新增：PyO3 单模块扩展（anydoc/pdf_inspector）原生二进制收集
    """将 anydoc/pdf_inspector 的原生 .pyd 按实际文件位置加入打包。
    这两个包是 PyO3 单模块分发（顶层模块即包，非目录结构），--collect-all 对其无效
    （日志提示 not a package 被跳过），导致 EXE 中缺失 .pyd、换机即报“未安装”。
    """
    for pkg in ("anydoc", "pdf_inspector"):
        try:
            mod = importlib.import_module(pkg)
            pkg_file = getattr(mod, "__file__", "") or ""
            base_dir = os.path.dirname(os.path.abspath(pkg_file))
            if not os.path.isdir(base_dir):
                continue
            added = False
            for fname in sorted(os.listdir(base_dir)):
                if fname.lower().endswith(".pyd"):
                    pyd_path = os.path.abspath(os.path.join(base_dir, fname))
                    cmd.extend(["--add-binary", f"{pyd_path};."])
                    added = True
            if added:
                print(f"已添加原生扩展二进制: {pkg} -> {base_dir}")
            else:
                print(f"警告: 未在 {base_dir} 找到 {pkg} 的 .pyd 文件")
        except Exception as e:
            print(f"警告: 收集 {pkg} 原生二进制失败: {e}")

def build_executable():
    """执行打包命令"""
    main_script = "AnyToMD_main.py"  # 2026-09-02 修改：主文件改为固定名（不再随版本号变化），确保项目稳定
    app_version = _get_app_version_from_source(main_script)  # 2026-09-02 修改：版本号从源码 APP_VERSION 常量读取（主文件名不再含版本号）
    build_date = datetime.datetime.now().strftime("%Y%m%d")  # 2026-04-01 16:45:00 修改：日期采用 YYYYMMDD
    exe_name = f"AnyToMD_v{app_version}_{build_date}"  # 2026-04-01 16:45:00 修改：输出文件名=固定内容+版本+日期

    # 获取markitdown路径
    markitdown_path = get_markitdown_path()
    
    # 构建基本命令
    # 2026-09-02 修改：统一用当前解释器运行 PyInstaller（sys.executable -m PyInstaller），
    # 根除“build.py 由 Python3.12 执行、PATH 中的 pyinstaller 却来自 Python3.13”导致的双环境混用
    # （此前日志：markitdown 路径命中 3.12，而 PyInstaller 运行于 3.13，出现大量 Hidden import not found）
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
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
        "pdfplumber",
        "PyPDF2",
        "html2text",
        "PIL",
        "openpyxl",
        "pptx",
        "bs4",
        "lxml",
        "pytesseract",
        "pdf2image",  # 确保pdf2image被正确导入
        "pdf2image.pdf2image",  # pdf2image的主模块
        "fitz",
        "pydub",
        "speech_recognition",
        "customtkinter",
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
        # 2026-09-01 新增：AnyDoc 兜底引擎（PyO3 原生扩展，需 hidden-import 收集 .pyd）
        "anydoc",
        "anydoc._anydoc",
        # 2026-09-01 新增：pdf-inspector 引擎（PyO3 原生扩展，需 hidden-import 收集 .pyd）
        "pdf_inspector",
        "pdf_inspector.pdf_inspector",
    ]
    
    for imp in additional_imports:
        cmd.extend(["--hidden-import", imp])
    
    # 添加打包设置
    cmd.extend([
        # 打包设置
        "--clean",
        f"--name={exe_name}",  # 2026-04-01 16:45:00 修改：动态输出名称
        main_script,  # 2026-04-01 16:45:00 修改：使用统一的主脚本变量
    ])
    
    # 收集完整的包（--collect-all 仅适用于目录式 package）
    collect_packages = [
        "markitdown",
        "docx",
        "docx2python",
        "pdfminer",
        "pdfplumber",
        "PyPDF2",
        "html2text",
        "openpyxl",
        "pptx",
        "bs4",
        "lxml",
        "win32com",
        "PIL",
        "pytesseract",
        "pdf2image",  # 确保收集pdf2image包
        "fitz",
        "pydub",
        "speech_recognition",
        "magika",        # 2026-09-02 新增：MarkItDown 0.1.7 硬依赖，需 collect-all 收集 .pyd 与模型数据
    ]

    for pkg in collect_packages:
        cmd.extend(["--collect-all", pkg])

    # 2026-09-02 修改：onnxruntime 不再 --collect-all，只收集原生二进制（核心 DLL/capi，配合 PyInstaller 官方 hook）。
    # 原因：--collect-all onnxruntime 会把 tools/transformers/datasets 等数百子模块全部打入，
    # 造成 EXE 体积暴增约 40+ MiB、构建时间翻倍（20→37 分钟），并间接触发 torch/transformers 依赖链扫描。
    cmd.extend(["--collect-binaries", "onnxruntime"])
    # 2026-09-02 修改：anydoc/pdf_inspector 是 PyO3 单模块扩展（非目录包），--collect-all 无效，
    # 改为按实际文件位置 --add-binary 收集原生 .pyd，避免 EXE 缺失扩展导致换机后“检查功能完整性”报未安装
    _collect_native_extension_binaries(cmd)
        
    # 排除不需要的庞大科学计算和机器学习包，以减小可执行文件体积
    excluded_modules = [
        "torch",
        "torchvision",
        "torchaudio",
        "tensorflow",
        "keras",
        "scipy",
        "sklearn",
        "matplotlib",
        "cv2",
        "PyQt5",
        "PySide6",
        "pandas",
        "sympy",
        "IPython",
        "jupyter",
        "notebook",
        "botocore",
        "boto3",
        "pydantic",
        "numba",
        "spacy",
        "xgboost",
        "tensorboard",
        "lightgbm",
        # 2026-09-02 修改：排除 onnxruntime 巨型子模块与 torch/transformers 链，
        # 体积瘦身，并避免 PyInstaller 分析时加载本机 torchvision._C.pyd 触发“无法定位程序输入点”弹窗
        "onnxruntime.transformers",
        "onnxruntime.tools",
        "onnxruntime.datasets",
        "onnxruntime.quantization",
        "transformers"
    ]
    
    for mod in excluded_modules:
        cmd.extend(["--exclude-module", mod])
        
    poppler_added = False
    for poppler_dir in sorted(glob.glob("poppler*")):
        if not os.path.isdir(poppler_dir):
            continue
        poppler_bin = os.path.join(poppler_dir, "Library", "bin")
        if os.path.exists(os.path.join(poppler_bin, "pdftoppm.exe")):
            cmd.extend(["--add-data", f"{poppler_dir};{poppler_dir}"])
            print(f"已将本地 Poppler 依赖包含在打包中: {poppler_dir}")
            poppler_added = True
            break
    
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
        print(f"完整路径: {os.path.abspath(os.path.join('dist', f'{exe_name}.exe'))}")  # 2026-04-01 16:45:00 修改：输出路径与动态名称一致
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)
    build_executable()
    input("按回车键退出...")
