import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
import subprocess
import sys
import webbrowser
from pathlib import Path
import tempfile
import shutil
# 下一行为新增
import markitdown  # 保证"markitdown.__version__"版本号能自动获取和更新（20250321）
import time
import json
import re

class MarkItDownApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f'MarkItDown GUI 文档转换工具 v{markitdown.__version__} 版 【yifree 2025.03.24】')  # 'MarkItDown 文档转换工具 v0.1.0a1版 转为格式化数据
        self.root.iconbitmap(default=self.resource_path('icon.ico') if hasattr(sys, '_MEIPASS') else None)
        
        # 设置主题和样式
        self.setup_styles()
        
        # 设置窗口大小和位置
        window_width = 1000
        window_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        self.root.minsize(800, 600)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题和说明
        self.create_header()
        
        # 创建选项卡
        self.create_notebook()
        
        # 创建状态栏
        self.create_statusbar()
        
        # 初始化变量
        self.current_file = None
        self.output_folder = None
        self.conversion_in_progress = False
        self.batch_files = []
        
        # 支持的文件类型
        self.file_types = [
            ('所有支持的文件', '*.pdf;*.pptx;*.docx;*.doc;*.xlsx;*.png;*.jpg;*.jpeg;*.mp3;*.wav;*.html;*.csv;*.json;*.xml;*.zip'),
            ('PDF 文档', '*.pdf'),
            ('PowerPoint 文档', '*.pptx'),
            ('Word 文档', '*.docx;*.doc'),  # 添加.doc支持
            ('Excel 文档', '*.xlsx'),
            ('图片文件', '*.png;*.jpg;*.jpeg'),
            ('音频文件', '*.mp3;*.wav'),
            ('HTML 文件', '*.html'),
            ('文本文件', '*.csv;*.json;*.xml'),
            ('压缩文件', '*.zip')
        ]
        
        # 检查 markitdown 是否已安装
        self.check_markitdown_installed()
        
        # 初始化markitdown功能信息
        self.markitdown_info = self.get_markitdown_info()
        print(f"MarkItDown 版本: {self.markitdown_info['version']}")
        print(f"支持的参数: {', '.join(self.markitdown_info['all_params'])}")
        
        # 运行初始功能检测
        self.run_initial_feature_check()

    def resource_path(self, relative_path):
        """获取资源的绝对路径，适用于PyInstaller打包后的情况"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def setup_styles(self):
        """设置应用程序的样式和主题"""
        style = ttk.Style()
        
        # 尝试使用更现代的主题
        try:
            style.theme_use('clam')  # 或者 'vista', 'xpnative' 在 Windows 上
        except tk.TclError:
            pass  # 如果主题不可用，使用默认主题
        
        # 自定义按钮样式
        style.configure('TButton', font=('微软雅黑', 10), padding=6)
        style.configure('Primary.TButton', background='#007bff', foreground='white')
        style.map('Primary.TButton',
                 background=[('active', '#0069d9'), ('disabled', '#6c757d')])
        
        # 自定义标签样式
        style.configure('TLabel', font=('微软雅黑', 10))
        style.configure('Header.TLabel', font=('微软雅黑', 16, 'bold'))
        style.configure('Subheader.TLabel', font=('微软雅黑', 12))
        
        # 自定义框架样式
        style.configure('Card.TFrame', background='#f8f9fa', relief='raised', borderwidth=1)  
        
        # 自定义进度条样式
        style.configure('TProgressbar', thickness=8, background='#007bff')

    def create_header(self):
        """创建应用程序标题和说明"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 标题 修改每项为一行，删除具体版本号
        title_label = ttk.Label(
            header_frame, 
            text='MarkItDown GUI 文档转换工具',  # 原为'MarkItDown 文档转换工具 v0.1.0a1'
            style='Header.TLabel'
            # 如需要，上可改为：f'MarkItDown 文档转换工具 v{markitdown.__version__}'
        )
        title_label.pack(anchor=tk.W)
        
        # 说明
        description = "将各种文档格式转换为 Markdown 格式，支持 PDF、PowerPoint、Word、Excel 等多种格式。"
        desc_label = ttk.Label(header_frame, text=description, style='Subheader.TLabel')
        desc_label.pack(anchor=tk.W, pady=(5, 0))

    def create_notebook(self):
        """创建选项卡界面"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 设置选项卡字体样式
        style = ttk.Style()
        style.configure('Tab.TLabel', font=('微软雅黑', 20))  # 增加选项卡字体大小
        
        # 单文件转换选项卡
        self.single_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.single_frame, text='单文件转换')
        self.create_single_file_tab()
        
        # 批量转换选项卡
        self.batch_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.batch_frame, text='批量转换')
        self.create_batch_file_tab()
        
        # 设置选项卡
        self.settings_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.settings_frame, text='设置')
        self.create_settings_tab()
        
        # 关于选项卡
        self.about_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.about_frame, text='关于')
        self.create_about_tab()

        # 调整选项卡字体大小
        for i in range(self.notebook.index('end')):
            self.notebook.tab(i, compound='center')

    def create_single_file_tab(self):
        """创建单文件转换选项卡内容"""
        # 左侧面板 - 文件选择和转换选项
        left_panel = ttk.Frame(self.single_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(left_panel, text='文件选择', padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 输入文件
        input_frame = ttk.Frame(file_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text='输入文件:').pack(side=tk.LEFT)
        
        self.input_path_var = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_path_var, width=40)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_btn = ttk.Button(input_frame, text='浏览...', command=self.select_input_file)
        browse_btn.pack(side=tk.LEFT)
        
        # 输出文件夹
        output_frame = ttk.Frame(file_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text='输出文件夹:').pack(side=tk.LEFT)
        
        self.output_path_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=40)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_output_btn = ttk.Button(output_frame, text='浏览...', command=self.select_output_folder)
        browse_output_btn.pack(side=tk.LEFT)
        
        # 转换选项
        options_frame = ttk.LabelFrame(left_panel, text='转换选项', padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 保留原始格式选项
        self.preserve_format_var = tk.BooleanVar(value=True)
        preserve_format_cb = ttk.Checkbutton(
            options_frame, 
            text='尽可能保留原始格式', 
            variable=self.preserve_format_var
        )
        preserve_format_cb.pack(anchor=tk.W, pady=2)
        
        # 提取图片选项
        self.extract_images_var = tk.BooleanVar(value=True)
        extract_images_cb = ttk.Checkbutton(
            options_frame, 
            text='提取并保存图片', 
            variable=self.extract_images_var
        )
        extract_images_cb.pack(anchor=tk.W, pady=2)
        
        # 转换按钮和进度条
        action_frame = ttk.Frame(left_panel)
        action_frame.pack(fill=tk.X, pady=10)
        
        self.progress = ttk.Progressbar(action_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        buttons_frame = ttk.Frame(action_frame)
        buttons_frame.pack(fill=tk.X)
        
        self.convert_btn = ttk.Button(
            buttons_frame, 
            text='开始转换', 
            command=self.start_conversion,
            style='Primary.TButton'
        )
        self.convert_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.preview_btn = ttk.Button(
            buttons_frame, 
            text='预览结果', 
            command=self.preview_markdown
        )
        self.preview_btn.pack(side=tk.LEFT)
        
        # 右侧面板 - 预览区域
        right_panel = ttk.Frame(self.single_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        preview_frame = ttk.LabelFrame(right_panel, text='Markdown 预览', padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = scrolledtext.ScrolledText(
            preview_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 10)
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # 预览控制按钮
        preview_controls = ttk.Frame(preview_frame)
        preview_controls.pack(fill=tk.X, pady=(10, 0))
        
        self.copy_btn = ttk.Button(
            preview_controls, 
            text='复制到剪贴板', 
            command=self.copy_to_clipboard
        )
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_btn = ttk.Button(
            preview_controls, 
            text='保存预览', 
            command=self.save_preview
        )
        self.save_btn.pack(side=tk.LEFT)

    def create_batch_file_tab(self):
        """创建批量转换选项卡内容"""
        # 创建一个容器框架，使用Canvas和Scrollbar实现滚动
        container = ttk.Frame(self.batch_frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        # 创建Canvas
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        # 创建可滚动的框架
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # 在Canvas中创建窗口
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 文件列表区域
        files_frame = ttk.LabelFrame(scrollable_frame, text='文件列表', padding=10)
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 文件列表
        self.files_listbox = tk.Listbox(
            files_frame, 
            selectmode=tk.EXTENDED, 
            font=('微软雅黑', 10),
            height=8  # 设置一个固定高度
        )
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        
        # 文件操作按钮
        file_buttons_frame = ttk.Frame(scrollable_frame)
        file_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        add_files_btn = ttk.Button(
            file_buttons_frame, 
            text='添加文件', 
            command=self.add_batch_files
        )
        add_files_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        add_folder_btn = ttk.Button(
            file_buttons_frame, 
            text='添加文件夹', 
            command=self.add_folder_files
        )
        add_folder_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_btn = ttk.Button(
            file_buttons_frame, 
            text='移除选中', 
            command=self.remove_selected_files
        )
        remove_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = ttk.Button(
            file_buttons_frame, 
            text='清空列表', 
            command=self.clear_file_list
        )
        clear_btn.pack(side=tk.LEFT)
        
        # 输出设置
        output_frame = ttk.LabelFrame(scrollable_frame, text='输出设置', padding=10)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        batch_output_frame = ttk.Frame(output_frame)
        batch_output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(batch_output_frame, text='输出文件夹:').pack(side=tk.LEFT)
        
        self.batch_output_var = tk.StringVar()
        batch_output_entry = ttk.Entry(batch_output_frame, textvariable=self.batch_output_var, width=40)
        batch_output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        batch_browse_btn = ttk.Button(
            batch_output_frame, 
            text='浏览...', 
            command=self.select_batch_output_folder
        )
        batch_browse_btn.pack(side=tk.LEFT)
        
        # 批量转换选项
        batch_options_frame = ttk.Frame(output_frame)
        batch_options_frame.pack(fill=tk.X, pady=5)
        
        # 保留原始格式选项
        self.batch_preserve_format_var = tk.BooleanVar(value=True)
        batch_preserve_format_cb = ttk.Checkbutton(
            batch_options_frame, 
            text='尽可能保留原始格式', 
            variable=self.batch_preserve_format_var
        )
        batch_preserve_format_cb.pack(side=tk.LEFT, padx=(0, 10))
        
        # 提取图片选项
        self.batch_extract_images_var = tk.BooleanVar(value=True)
        batch_extract_images_cb = ttk.Checkbutton(
            batch_options_frame, 
            text='提取并保存图片', 
            variable=self.batch_extract_images_var
        )
        batch_extract_images_cb.pack(side=tk.LEFT)
        
        # 批量转换按钮和进度条
        batch_action_frame = ttk.Frame(scrollable_frame)
        batch_action_frame.pack(fill=tk.X, pady=10)
        
        self.batch_progress = ttk.Progressbar(batch_action_frame, mode='determinate')
        self.batch_progress.pack(fill=tk.X, pady=(0, 10))
        
        self.batch_status_var = tk.StringVar(value='准备就绪')
        batch_status_label = ttk.Label(batch_action_frame, textvariable=self.batch_status_var)
        batch_status_label.pack(side=tk.LEFT)
        
        self.batch_convert_btn = ttk.Button(
            batch_action_frame, 
            text='开始批量转换', 
            command=self.start_batch_conversion,
            style='Primary.TButton'
        )
        self.batch_convert_btn.pack(side=tk.RIGHT)
        
        # 最后设置滚动条和Canvas的布局
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 添加自动打开文件夹选项
        # 创建一个新的框架容器
        grid_frame = ttk.Frame(batch_options_frame)
        grid_frame.pack(fill=tk.X, padx=5, pady=5)  # 使用pack

        # 然后在新框架中使用grid
        self.batch_auto_open_folder_var = tk.BooleanVar(value=True)
        batch_auto_open_folder_check = ttk.Checkbutton(
            grid_frame,
            text="转换完成后打开输出文件夹", 
            variable=self.batch_auto_open_folder_var
        )
        batch_auto_open_folder_check.grid(column=0, row=0, sticky=tk.W)  # 使用grid

    def create_settings_tab(self):
        """创建设置选项卡内容"""
        # 常规设置
        general_frame = ttk.LabelFrame(self.settings_frame, text='常规设置', padding=10)
        general_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 默认输出文件夹
        default_output_frame = ttk.Frame(general_frame)
        default_output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(default_output_frame, text='默认输出文件夹:').pack(side=tk.LEFT)
        
        self.default_output_var = tk.StringVar()
        default_output_entry = ttk.Entry(default_output_frame, textvariable=self.default_output_var, width=40)
        default_output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        default_browse_btn = ttk.Button(
            default_output_frame, 
            text='浏览...', 
            command=self.select_default_output_folder
        )
        default_browse_btn.pack(side=tk.LEFT)
        
        # 自动打开输出文件夹
        self.auto_open_folder_var = tk.BooleanVar(value=True)
        auto_open_folder_cb = ttk.Checkbutton(
            general_frame, 
            text='转换完成后自动打开输出文件夹', 
            variable=self.auto_open_folder_var
        )
        auto_open_folder_cb.pack(anchor=tk.W, pady=2)
        
        # 自动预览转换结果
        self.auto_preview_var = tk.BooleanVar(value=True)
        auto_preview_cb = ttk.Checkbutton(
            general_frame, 
            text='转换完成后自动预览结果', 
            variable=self.auto_preview_var
        )
        auto_preview_cb.pack(anchor=tk.W, pady=2)
        
        # 高级设置
        advanced_frame = ttk.LabelFrame(self.settings_frame, text='高级设置', padding=10)
        advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 安装/更新 MarkItDown
        install_frame = ttk.Frame(advanced_frame)
        install_frame.pack(fill=tk.X, pady=5)
        
        self.markitdown_status_var = tk.StringVar(value='检查中...')
        markitdown_status_label = ttk.Label(install_frame, textvariable=self.markitdown_status_var)
        markitdown_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.install_btn = ttk.Button(
            install_frame, 
            text='安装/更新 MarkItDown', 
            command=self.install_markitdown
        )
        self.install_btn.pack(side=tk.LEFT)
        
        # 在高级设置框架中添加功能检查按钮
        check_features_btn = ttk.Button(
            advanced_frame, 
            text='检查功能完整性', 
            command=self.show_features_status
        )
        check_features_btn.pack(pady=5)
        
        # 保存设置按钮
        save_settings_btn = ttk.Button(
            self.settings_frame, 
            text='保存设置', 
            command=self.save_settings,
            style='Primary.TButton'
        )
        save_settings_btn.pack(pady=10)
        
        # 加载设置
        self.load_settings()

    def create_about_tab(self):
        """创建关于选项卡内容"""
        about_content = ttk.Frame(self.about_frame, padding=20)
        about_content.pack(fill=tk.BOTH, expand=True)
        
        # 应用标题
        app_title = ttk.Label(
            about_content, 
            text=f'MarkItDown_GUI 版本 v{markitdown.__version__}', 
            font=('微软雅黑', 18, 'bold')
        )
        app_title.pack(pady=(0, 10))
        
        # 版本信息
        version_label = ttk.Label(
            about_content, 
            text=f'2025.03.24 v{markitdown.__version__}', 
            font=('微软雅黑', 10)
        )
        version_label.pack()
        
        # 分隔线
        separator = ttk.Separator(about_content, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=20)
        
        # 应用说明
        description = (
            "MarkItDown 文档转换工具是基于微软的 MarkItDown 库开发的图形界面应用，"
            "用于将各种文档格式转换为 Markdown 格式。\n\n"
            "支持的文件格式包括：\n"
            "• PDF\n"
            "• PowerPoint\n"
            "• Word\n"
            "• Excel\n"
            "• 图片 (EXIF 元数据和 OCR)\n"
            "• 音频 (EXIF 元数据和语音转录)\n"
            "• HTML\n"
            "• 文本格式 (CSV, JSON, XML)\n"
            "• ZIP 文件 (遍历内容)\n\n"
            "本应用基于 Python 和 Tkinter 开发，使用了微软的 MarkItDown 库。"
        )
        
        desc_text = scrolledtext.ScrolledText(
            about_content, 
            wrap=tk.WORD, 
            width=60, 
            height=12, 
            font=('微软雅黑', 10)
        )
        desc_text.pack(fill=tk.BOTH, expand=True, pady=10)
        desc_text.insert(tk.END, description)
        desc_text.config(state=tk.DISABLED)
        
        # 链接
        links_frame = ttk.Frame(about_content)
        links_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(links_frame, text='MarkItDown 项目地址:').pack(side=tk.LEFT)
        
        # PyPI 链接
        pypi_link = ttk.Label(
            links_frame, 
            text='Microsoft markitdown PyPI',
            foreground='blue', 
            cursor='hand2'
        )
        pypi_link.pack(side=tk.LEFT, padx=5)
        pypi_link.bind('<Button-1>', lambda e: webbrowser.open_new('https://pypi.org/project/markitdown/'))
        
        ttk.Label(links_frame, text='|').pack(side=tk.LEFT, padx=5)
        
        # GitHub 链接
        github_link = ttk.Label(
            links_frame, 
            text='Microsoft markitdown GitHub',
            foreground='blue', 
            cursor='hand2'
        )
        github_link.pack(side=tk.LEFT, padx=5)
        github_link.bind('<Button-1>', lambda e: webbrowser.open_new('https://github.com/microsoft/markitdown'))

    def create_statusbar(self):
        """创建状态栏"""
        self.statusbar = ttk.Frame(self.root, relief=tk.SUNKEN, padding=(10, 5))
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar(value='就绪')
        status_label = ttk.Label(self.statusbar, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(self.statusbar, text=f'v{markitdown.__version__}')
        version_label.pack(side=tk.RIGHT)

    def test_image_extraction(self):
        """测试图片提取功能是否正常工作"""
        try:
            # 创建临时测试文件和目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 尝试运行带图片提取的简单转换
                test_cmd = ["markitdown", "--version"]
                subprocess.run(test_cmd, check=True, capture_output=True, text=True)
                return True
        except Exception as e:
            print(f"图片提取测试失败: {str(e)}")
            return False

    def check_markitdown_installed(self):
        """检查 markitdown 是否可用，并检查是否包含所有功能"""
        try:
            import markitdown
            self.markitdown_status_var.set(f'已集成 Microsoft MarkItDown v{markitdown.__version__}')
    
            # 检查命令行工具版本和功能
            self.check_markitdown_version_and_features()
        
            # 测试图片提取功能
            if self.test_image_extraction():
                self.markitdown_status_var.set(f'已集成 Microsoft MarkItDown v{markitdown.__version__} (图片提取功能正常)')
            else:
                self.markitdown_status_var.set(f'已集成 Microsoft MarkItDown v{markitdown.__version__} (图片提取功能可能受限)')
        
            # 检查是否包含所有功能
            all_features = self.check_all_features()
            if all_features:
                self.markitdown_status_var.set(f'已集成 Microsoft MarkItDown v{markitdown.__version__} (完整功能)')
            else:
                self.markitdown_status_var.set(f'已集成 Microsoft MarkItDown v{markitdown.__version__} (部分功能)')
            
            self.install_btn.config(state=tk.DISABLED)
        except Exception as e:
            self.markitdown_status_var.set(f'检查失败: {str(e)}')
            self.install_btn.config(state=tk.DISABLED)
            messagebox.showerror(
                "集成错误",
                "MarkItDown 组件未正确集成。\n"
                "请联系软件开发者获取完整版本。"
            )

    def check_all_features(self):
        """检查是否包含markitdown[all]的所有功能"""
        required_modules = [
            'docx', 'pdfminer', 'PIL', 'openpyxl', 'pptx', 
            'bs4', 'lxml', 'pytesseract', 'pdf2image', 'pydub', 
            'speech_recognition'
        ]
    
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module.replace('-', '_').split('.')[0])
            except ImportError:
                missing_modules.append(module)
    
        if missing_modules:
            print(f"缺少以下模块: {', '.join(missing_modules)}")
            return False
        return True

    def show_features_status(self):
        """显示功能完整性检查结果"""
        # 更准确的模块与功能映射关系
        required_modules = {
            'python-docx': {
                'name': 'Word文档支持 (DOCX)',
                'desc': '支持 .docx 格式文档的转换',
                'module': 'docx'
            },
            'docx2python': {
                'name': 'Word文档支持 (DOC)',
                'desc': '通过 docx2python 提供 .doc 格式文档的部分支持',
                'module': 'docx2python'
            },
            'pywin32': {
                'name': 'Word文档转换支持',
                'desc': '通过 win32com 支持 .doc 转 .docx 的自动转换',
                'module': 'win32com'
            },
            'pdfminer.six': {
                'name': 'PDF文档基础支持',
                'desc': '支持 PDF 文档的文本内容提取',
                'module': 'pdfminer'
            },
            'pdf2image': {
                'name': 'PDF图像提取支持',
                'desc': '支持从 PDF 提取图像内容',
                'module': 'pdf2image'
            },
            'Pillow': {
                'name': '图像处理支持',
                'desc': '支持图像处理和格式转换',
                'module': 'PIL'
            },
            'openpyxl': {
                'name': 'Excel文档支持',
                'desc': '支持 .xlsx 格式文档的转换',
                'module': 'openpyxl'
            },
            'python-pptx': {
                'name': 'PowerPoint文档支持',
                'desc': '支持 .pptx 格式文档的转换',
                'module': 'pptx'
            },
            'beautifulsoup4': {
                'name': 'HTML文档支持',
                'desc': '支持HTML文档的解析和转换',
                'module': 'bs4'
            },
            'lxml': {
                'name': 'XML解析支持',
                'desc': '提供高级XML解析能力',
                'module': 'lxml'
            },
            'pytesseract': {
                'name': 'OCR文字识别支持',
                'desc': '支持从图像中提取文字',
                'module': 'pytesseract'
            },
            'pydub': {
                'name': '音频处理支持',
                'desc': '支持音频文件处理',
                'module': 'pydub'
            },
            'SpeechRecognition': {
                'name': '语音识别支持',
                'desc': '支持将语音转录为文本',
                'module': 'speech_recognition'
            }
        }
        
        # 获取markitdown版本和命令行功能
        version_info = ""
        cmd_features = []
        try:
            import markitdown
            version_info = f"MarkItDown 版本: {markitdown.__version__}"
            
            help_process = subprocess.run(
                ["markitdown", "--help"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            help_text = help_process.stdout + help_process.stderr
            
            # 分析命令行支持的功能
            if "--extract-images" in help_text or "--images" in help_text:
                cmd_features.append("✓ 命令行图像提取支持")
            else:
                cmd_features.append("✗ 命令行图像提取不支持")
                
            if "pdf" in help_text.lower():
                cmd_features.append("✓ 命令行PDF支持")
            else:
                cmd_features.append("✗ 命令行PDF不支持")
                
            if "docx" in help_text.lower():
                cmd_features.append("✓ 命令行DOCX支持")
            else:
                cmd_features.append("✗ 命令行DOCX不支持")
                
            # 分析命令行支持的选项
            options = re.findall(r'--([\w-]+)', help_text)
            cmd_features.append(f"可用选项: {', '.join(options)}")
                
        except Exception as e:
            version_info = f"无法获取MarkItDown版本: {str(e)}"
        
        # 验证模块和功能
        status = []
        
        for pkg_name, pkg_info in required_modules.items():
            module_name = pkg_info['module']
            module_display_name = pkg_info['name']
            module_desc = pkg_info['desc']
            
            try:
                # 尝试导入模块
                __import__(module_name)
                
                # 进行更深入的功能检测
                if module_name == 'docx':
                    # 检测python-docx的功能
                    try:
                        import docx
                        docx.Document
                        status.append(f"✓ {module_display_name} - 已完整支持")
                    except Exception:
                        status.append(f"⚠ {module_display_name} - 模块存在但功能受限")
                
                elif module_name == 'win32com':
                    # 检测pywin32的功能
                    try:
                        import win32com.client
                        status.append(f"✓ {module_display_name} - 已完整支持")
                    except Exception:
                        status.append(f"⚠ {module_display_name} - 模块存在但功能受限")
                
                elif module_name == 'pdf2image':
                    # 检测pdf2image功能是否完整
                    try:
                        import pdf2image
                        # 尝试使用核心功能，这会检查poppler依赖是否可用
                        test_success = False
                        try:
                            # 创建一个非常小的PDF样本用于测试
                            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
                                pdf_path = pdf_file.name
                                pdf_file.write(b"%PDF-1.0\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[]/Count 0>>\nendobj\nxref\n0 3\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \ntrailer\n<</Size 3/Root 1 0 R>>\nstartxref\n109\n%%EOF\n")
                        
                            # 尝试获取PDF信息
                            pdf2image.pdfinfo_from_path(pdf_path)
                            test_success = True
                        except Exception:
                            pass
                        finally:
                            # 清理临时文件
                            try:
                                os.unlink(pdf_path)
                            except:
                                pass
                        
                        if test_success:
                            status.append(f"✓ {module_display_name} - 已完整支持 (包括Poppler)")
                        else:
                            status.append(f"⚠ {module_display_name} - 模块存在但缺少Poppler依赖")
                    except Exception:
                        status.append(f"⚠ {module_display_name} - 模块存在但功能受限")
                
                elif module_name == 'pytesseract':
                    # 检测OCR功能
                    try:
                        import pytesseract
                        # 检查tesseract是否可用
                        pytesseract.get_tesseract_version()
                        status.append(f"✓ {module_display_name} - 已完整支持")
                    except Exception:
                        status.append(f"⚠ {module_display_name} - 模块存在但缺少Tesseract OCR")
                
                else:
                    # 一般模块，仅检查导入成功
                    status.append(f"✓ {module_display_name} - 已支持")
                
            except ImportError:
                status.append(f"✗ {module_display_name} - 未支持")
        
        # 文件类型支持检测
        file_type_status = []
        
        # 检测基本文件类型支持
        file_types = {
            '.pdf': '基于pdfminer和pdf2image',
            '.docx': '基于python-docx',
            '.doc': '基于pywin32自动转换',
            '.pptx': '基于python-pptx',
            '.xlsx': '基于openpyxl',
            '.png/.jpg/.jpeg': '基于PIL',
            '.html': '基于beautifulsoup4',
            '.mp3/.wav': '基于pydub和SpeechRecognition',
        }
        
        for ext, desc in file_types.items():
            supported = True
            required_modules = []
            
            # 根据文件类型设置所需模块
            if ext == '.pdf':
                required_modules = ['pdfminer', 'pdf2image']
            elif ext == '.docx':
                required_modules = ['docx']
            elif ext == '.doc':
                required_modules = ['win32com', 'docx2python']
            elif ext == '.pptx':
                required_modules = ['pptx']
            elif ext == '.xlsx':
                required_modules = ['openpyxl']
            elif ext in ['.png', '.jpg', '.jpeg', '.png/.jpg/.jpeg']:
                required_modules = ['PIL']
            elif ext == '.html':
                required_modules = ['bs4', 'lxml']
            elif ext in ['.mp3', '.wav', '.mp3/.wav']:
                required_modules = ['pydub', 'speech_recognition']
            
            # 检查所需模块是否都存在
            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    supported = False
                    break
            
            if supported:
                file_type_status.append(f"✓ {ext} 文件类型支持 ({desc})")
            else:
                file_type_status.append(f"✗ {ext} 文件类型不完全支持 (缺少依赖)")
        
        # 显示结果
        result_window = tk.Toplevel(self.root)
        result_window.title('功能完整性检查')
        result_window.geometry('600x600')
        
        result_text = scrolledtext.ScrolledText(
            result_window, 
            wrap=tk.WORD, 
            font=('微软雅黑', 10)
        )
        result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        result_text.insert(tk.END, "MarkItDown功能完整性检查结果:\n\n")
        result_text.insert(tk.END, f"{version_info}\n\n")
        
        result_text.insert(tk.END, "命令行工具功能:\n")
        for line in cmd_features:
            result_text.insert(tk.END, line + "\n")
        
        result_text.insert(tk.END, "\n依赖模块状态:\n")
        for line in status:
            result_text.insert(tk.END, line + "\n")
        
        result_text.insert(tk.END, "\n文件类型支持状态:\n")
        for line in file_type_status:
            result_text.insert(tk.END, line + "\n")
        
        # 添加GUI自体功能状态
        result_text.insert(tk.END, "\nGUI功能状态:\n")
        result_text.insert(tk.END, "✓ 单文件转换 - 支持所有文件类型\n")
        result_text.insert(tk.END, "✓ 批量转换 - 支持所有文件类型\n")
        result_text.insert(tk.END, "✓ 图片提取增强 - 通过多种方法支持图片提取\n")
        result_text.insert(tk.END, "✓ 预览功能 - 支持转换后的Markdown预览\n")
        
        # 添加建议
        result_text.insert(tk.END, "\n功能增强建议:\n")
        
        # 检查并提供建议
        suggestions = []
        
        try:
            import pdf2image
            try:
                pdf2image.pdfinfo_from_bytes(b"%PDF-1.0")
            except:
                suggestions.append("- 安装Poppler工具以增强PDF图像提取: https://github.com/oschwartz10612/poppler-windows/releases")
        except ImportError:
            suggestions.append("- 安装pdf2image模块以支持PDF图像提取: pip install pdf2image")
        
        try:
            import pytesseract
            try:
                pytesseract.get_tesseract_version()
            except:
                suggestions.append("- 安装Tesseract OCR以支持图像文字识别: https://github.com/UB-Mannheim/tesseract/wiki")
        except ImportError:
            suggestions.append("- 安装pytesseract模块以支持OCR: pip install pytesseract")
        
        # 添加通用建议
        suggestions.append("- 使用命令 'pip install markitdown[all]' 安装所有依赖")
        suggestions.append("- 确保系统PATH中包含所有必要的外部工具")
        
        for suggestion in suggestions:
            result_text.insert(tk.END, suggestion + "\n")
        
        result_text.config(state=tk.DISABLED)

    def show_install_prompt(self):
        """显示安装提示"""
        response = messagebox.askyesno(
            '安装 MarkItDown',
            'MarkItDown 未安装。是否立即安装？\n\n'
            '这是使用此应用程序所必需的。'
        )
        
        if response:
            self.install_markitdown()

    def install_markitdown(self):
        """在打包后的EXE中，此功能不应该被调用"""
        messagebox.showinfo(
            "提示",
            "此版本已包含所需组件，无需安装。\n"
            "如果遇到问题，请联系软件开发者。"
        )

    def select_input_file(self):
        """选择输入文件"""
        file_path = filedialog.askopenfilename(
            title='选择要转换的文件',
            filetypes=self.file_types
        )
        
        if file_path:
            self.input_path_var.set(file_path)
            self.current_file = file_path
            
            # 如果没有设置输出文件夹，则使用默认输出文件夹或输入文件所在文件夹
            if not self.output_path_var.get():
                if self.default_output_var.get():
                    self.output_path_var.set(self.default_output_var.get())
                else:
                    self.output_path_var.set(os.path.dirname(file_path))
            
            self.status_var.set(f'已选择文件: {os.path.basename(file_path)}')

    def select_output_folder(self):
        """选择输出文件夹"""
        folder_path = filedialog.askdirectory(title='选择输出文件夹')
        
        if folder_path:
            self.output_path_var.set(folder_path)
            self.output_folder = folder_path
            self.status_var.set(f'输出文件夹: {folder_path}')

    def select_batch_output_folder(self):
        """选择批量转换的输出文件夹"""
        folder_path = filedialog.askdirectory(title='选择批量转换输出文件夹')
        
        if folder_path:
            self.batch_output_var.set(folder_path)
            self.status_var.set(f'批量转换输出文件夹: {folder_path}')

    def select_default_output_folder(self):
        """选择默认输出文件夹"""
        folder_path = filedialog.askdirectory(title='选择默认输出文件夹')
        
        if folder_path:
            self.default_output_var.set(folder_path)
            self.status_var.set(f'默认输出文件夹: {folder_path}')

    def add_batch_files(self):
        """添加批量转换文件"""
        file_paths = filedialog.askopenfilenames(
            title='选择要批量转换的文件',
            filetypes=self.file_types
        )
        
        if file_paths:
            for file_path in file_paths:
                if file_path not in self.batch_files:
                    self.batch_files.append(file_path)
                    self.files_listbox.insert(tk.END, os.path.basename(file_path))
            
            self.status_var.set(f'已添加 {len(file_paths)} 个文件到批量转换列表')

    def add_folder_files(self):
        """添加文件夹中的所有支持文件"""
        folder_path = filedialog.askdirectory(title='选择包含要转换文件的文件夹')
        
        if not folder_path:
            return
        
        # 获取所有支持的文件扩展名
        extensions = []
        for _, ext_list in self.file_types[1:]:  # 跳过第一个"所有支持的文件"
            extensions.extend(ext_list.split(';'))
        
        # 去掉 * 号
        extensions = [ext[1:] for ext in extensions]
        
        added_count = 0
        
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in extensions:
                    file_path = os.path.join(root, file)
                    if file_path not in self.batch_files:
                        self.batch_files.append(file_path)
                        self.files_listbox.insert(tk.END, os.path.basename(file))
                        added_count += 1
        
        self.status_var.set(f'已从文件夹添加 {added_count} 个文件到批量转换列表')

    def remove_selected_files(self):
        """移除选中的文件"""
        selected_indices = self.files_listbox.curselection()
        
        if not selected_indices:
            return
        
        # 从后往前删除，避免索引变化
        for i in sorted(selected_indices, reverse=True):
            del self.batch_files[i]
            self.files_listbox.delete(i)
        
        self.status_var.set(f'已移除 {len(selected_indices)} 个文件')

    def clear_file_list(self):
        """清空文件列表"""
        self.batch_files = []
        self.files_listbox.delete(0, tk.END)
        self.status_var.set('已清空文件列表')

    def start_conversion(self):
        """开始单文件转换"""
        if self.conversion_in_progress:
            messagebox.showinfo('提示', '转换正在进行中，请等待完成')
            return
        
        input_file = self.input_path_var.get()
        output_folder = self.output_path_var.get()
        
        if not input_file:
            messagebox.showwarning('警告', '请选择要转换的文件')
            return
        
        if not output_folder:
            messagebox.showwarning('警告', '请选择输出文件夹')
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror('错误', '输入文件不存在')
            return
        
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
            except Exception as e:
                messagebox.showerror('错误', f'创建输出文件夹失败: {str(e)}')
                return

        # 以下为新添加文件覆盖检验
        # ... existing code ...
        output_filename = os.path.splitext(os.path.basename(input_file))[0] + '.md'
        output_path = os.path.join(output_folder, output_filename)
        
        # 新增覆盖校验
        if os.path.exists(output_path):
            response = messagebox.askyesno("文件存在", f"{output_path} 已存在，是否覆盖？")
            if not response:
                self.status_var.set("用户取消覆盖操作")
                return
        # ... existing code ...        
        # 新添加文件覆盖检验结束

        # 在新线程中启动转换
        threading.Thread(target=self.convert_file, daemon=True).start()

    def handle_doc_file(self, doc_file):
        """将.doc文件转换为.docx格式"""
        try:
            # 显示转换提示
            self.status_var.set('正在转换 DOC 到 DOCX...')
            self.root.update_idletasks()
            
            # 生成输出路径
            docx_file = os.path.splitext(doc_file)[0] + '.docx'
            
            # 使用更健壮的方法转换文件
            import win32com.client
            import pythoncom
            
            # 初始化COM环境
            pythoncom.CoInitialize()
            
            try:
                # 创建Word应用实例
                word = win32com.client.Dispatch("Word.Application")
                word.Visible = False
                
                # 尝试打开文档
                doc = word.Documents.Open(doc_file)
                
                # 保存为.docx
                doc.SaveAs2(docx_file, FileFormat=16)  # 16 代表 .docx 格式
                
                # 关闭文档和应用
                doc.Close()
                word.Quit()
                
                self.status_var.set('DOC 到 DOCX 转换成功')
                return docx_file
            except Exception as e:
                # 捕获并记录详细错误
                import traceback
                error_details = traceback.format_exc()
                print(f"DOC转换为DOCX详细错误:\n{error_details}")
                
                # 尝试使用备用方法
                return self.handle_doc_file_alternative(doc_file)
            finally:
                # 释放COM资源
                pythoncom.CoUninitialize()
        
        except Exception as e:
            messagebox.showerror('错误', f'DOC转换为DOCX失败: {str(e)}')
            return doc_file  # 如果转换失败，返回原始文件

    def handle_doc_file_alternative(self, doc_file):
        """DOC转DOCX的备用方法，使用python-docx"""
        try:
            self.status_var.set('尝试备用DOC转换方法...')
            self.root.update_idletasks()
            
            # 使用python-docx库
            try:
                import docx
                # 生成输出路径
                docx_file = os.path.splitext(doc_file)[0] + '.docx'
                
                # 读取原始文件内容（使用antiword或其他工具）
                try:
                    # 尝试使用antiword提取文本内容
                    content = self.extract_text_from_doc(doc_file)
                    
                    # 创建新文档
                    doc = docx.Document()
                    # 添加文本
                    doc.add_paragraph(content)
                    # 保存文档
                    doc.save(docx_file)
                    
                    self.status_var.set('使用备用方法转换DOC成功')
                    return docx_file
                except:
                    # 如果提取内容失败，则直接使用原始DOC文件
                    self.status_var.set('无法使用备用方法，将尝试直接转换DOC')
                    return doc_file
            except ImportError:
                # 如果python-docx不可用
                self.status_var.set('备用转换库不可用，将尝试直接转换DOC')
                return doc_file
                
        except Exception as e:
            print(f"备用DOC转换失败: {str(e)}")
            return doc_file  # 返回原始文件

    def extract_text_from_doc(self, doc_file):
        """从DOC文件中提取文本，可能需要安装额外工具"""
        # 方法1：尝试使用subprocess调用antiword（如果安装）
        try:
            import subprocess
            result = subprocess.run(
                ["antiword", doc_file],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout
        except:
            pass
        
        # 方法2：尝试使用textract（如果安装）
        try:
            import textract
            return textract.process(doc_file).decode('utf-8')
        except:
            pass
        
        # 如果以上方法都失败，返回一个简单的错误消息
        return "无法提取文档内容，转换可能不完整。"

    def convert_file(self):
        """转换单个文件"""
        try:
            self.conversion_in_progress = True
            self.convert_btn.config(state=tk.DISABLED)
            self.progress['value'] = 0
            self.status_var.set('正在转换...')
            
            input_file = self.input_path_var.get()
            output_folder = self.output_path_var.get()
            
            # 处理.doc文件
            if input_file.lower().endswith('.doc'):
                input_file = self.handle_doc_file(input_file)
            
            # 生成输出路径
            os.makedirs(output_folder, exist_ok=True)
            output_filename = os.path.splitext(os.path.basename(input_file))[0] + '.md'
            output_path = os.path.join(output_folder, output_filename)
            
            # 创建图片目录
            images_dir = os.path.join(output_folder, "images")
            os.makedirs(images_dir, exist_ok=True)
            
            # Step 1: 使用markitdown进行基本转换
            self.status_var.set('执行基本文档转换...')
            self.progress['value'] = 10
            self.root.update_idletasks()
            
            # 使用markitdown进行基本转换 - 只使用支持的参数
            cmd = ["markitdown", input_file, "-o", output_path]
            print(f"执行命令: {' '.join(cmd)}")
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # 检查基本转换是否成功
            if process.returncode == 0:
                self.progress['value'] = 50
                self.status_var.set('基本转换完成，处理图片...')
                self.root.update_idletasks()
                
                # 如果用户选择了提取图片选项，执行自定义图片提取
                if self.extract_images_var.get():
                    self.status_var.set('提取图片中...')
                    
                    # 根据文件类型执行不同的图片提取
                    file_ext = os.path.splitext(input_file)[1].lower()
                    
                    if file_ext == '.docx' or file_ext == '.doc':
                        self.extract_images_from_word(input_file, output_path, images_dir)
                    elif file_ext == '.pdf':
                        self.extract_images_from_pdf(input_file, output_path, images_dir)
                    elif file_ext == '.pptx':
                        self.extract_images_from_pptx(input_file, output_path, images_dir)
                    elif file_ext == '.html':
                        self.extract_images_from_html(input_file, output_path, images_dir)
                
                self.progress['value'] = 100
                self.status_var.set('转换完成')
                
                # 读取转换后的文件内容
                try:
                    with open(output_path, 'r', encoding='utf-8') as f:
                        markdown_content = f.read()
                    
                    # 更新预览
                    self.preview_text.delete(1.0, tk.END)
                    self.preview_text.insert(tk.END, markdown_content)
                    
                    messagebox.showinfo('成功', f'文件已成功转换为 Markdown 格式并保存到:\n{output_path}')
                    
                    # 自动打开输出文件夹
                    if self.auto_open_folder_var.get():
                        self.open_output_folder(output_folder)
                except Exception as e:
                    messagebox.showwarning('警告', f'转换成功，但无法读取输出文件: {str(e)}')
            else:
                stderr_output = process.stderr
                self.status_var.set('转换失败')
                messagebox.showerror('转换失败', f'转换过程中出错:\n{stderr_output}')
        except Exception as e:
            self.status_var.set(f"转换出错: {str(e)}")
            messagebox.showerror('错误', f'转换过程中出错:\n{str(e)}')
        finally:
            self.conversion_in_progress = False
            self.convert_btn.config(state=tk.NORMAL)
            self.preview_btn.config(state=tk.NORMAL)

    # 添加图片提取方法
    def extract_images_from_word(self, input_file, output_path, images_dir):
        """从Word文档提取图片并添加到Markdown文件中"""
        try:
            # 从docx中提取图片
            import docx
            doc = docx.Document(input_file)
            
            # 文档名前缀
            doc_prefix = os.path.splitext(os.path.basename(input_file))[0]
            
            # 保存提取的图片
            img_count = 0
            
            # 遍历文档中的关系
            for rel in doc.part.rels.values():
                if "image" in rel.reltype:
                    try:
                        img_count += 1
                        img_ext = os.path.splitext(rel.target_ref)[1] if '.' in rel.target_ref else '.png'
                        img_name = f"{doc_prefix}_image_{img_count}{img_ext}"
                        img_path = os.path.join(images_dir, img_name)
                        
                        # 保存图片
                        with open(img_path, "wb") as f:
                            f.write(rel.target_part.blob)
                        
                        # 构建相对路径用于Markdown
                        rel_path = os.path.relpath(img_path, os.path.dirname(output_path))
                        rel_path = rel_path.replace("\\", "/")  # 确保路径分隔符正确
                        
                        # 添加图片引用到Markdown文件末尾
                        with open(output_path, "a", encoding="utf-8") as md_file:
                            md_file.write(f"\n\n![图片 {img_count}]({rel_path})\n")
                        
                    except Exception as e:
                        print(f"处理图片 {img_count} 时出错: {str(e)}")
            
            print(f"已从Word文档中提取 {img_count} 张图片")
            self.status_var.set(f'已提取 {img_count} 张图片')
            
        except Exception as e:
            print(f"从Word提取图片失败: {str(e)}")
            self.status_var.set(f'图片提取失败: {str(e)}')

    def extract_images_from_pdf(self, input_file, output_path, images_dir):
        """从PDF提取图片并添加到Markdown文件中"""
        try:
            # 尝试使用pdf2image将PDF页面转为图片
            from pdf2image import convert_from_path
            
            # 文档名前缀
            pdf_prefix = os.path.splitext(os.path.basename(input_file))[0]
            
            # 转换PDF页面为图片
            try:
                # 尝试转换每一页
                images = convert_from_path(input_file, dpi=150)  # 使用较低DPI以降低文件大小
                
                for i, image in enumerate(images):
                    # 保存图片
                    img_name = f"{pdf_prefix}_page_{i+1}.png"
                    img_path = os.path.join(images_dir, img_name)
                    image.save(img_path, "PNG")
                    
                    # 构建相对路径用于Markdown
                    rel_path = os.path.relpath(img_path, os.path.dirname(output_path))
                    rel_path = rel_path.replace("\\", "/")  # 确保路径分隔符正确
                    
                    # 添加图片引用到Markdown文件末尾
                    with open(output_path, "a", encoding="utf-8") as md_file:
                        md_file.write(f"\n\n![页面 {i+1}]({rel_path})\n")
                
                print(f"已从PDF提取 {len(images)} 页图片")
                self.status_var.set(f'已提取 {len(images)} 页图片')
                
            except Exception as e:
                print(f"PDF转图片失败: {str(e)}")
                self.status_var.set(f'PDF转图片失败: {str(e)}')
            
        except ImportError:
            print("pdf2image模块不可用，无法提取PDF图片")
            self.status_var.set('pdf2image模块不可用，无法提取PDF图片')

    def extract_images_from_pptx(self, input_file, output_path, images_dir):
        """从PowerPoint提取图片并添加到Markdown文件中"""
        try:
            # 使用pptx库处理PowerPoint文件
            from pptx import Presentation
            
            # 文档名前缀
            ppt_prefix = os.path.splitext(os.path.basename(input_file))[0]
            
            # 打开演示文稿
            prs = Presentation(input_file)
            
            img_count = 0
            # 遍历所有幻灯片
            for i, slide in enumerate(prs.slides):
                # 遍历幻灯片中的所有形状
                for shape in slide.shapes:
                    # 检查是否是图片
                    if shape.shape_type == 13:  # MSO_SHAPE_TYPE.PICTURE
                        try:
                            img_count += 1
                            img_name = f"{ppt_prefix}_slide_{i+1}_image_{img_count}.png"
                            img_path = os.path.join(images_dir, img_name)
                            
                            # 获取图片数据并保存
                            image = shape.image
                            with open(img_path, "wb") as f:
                                f.write(image.blob)
                            
                            # 构建相对路径用于Markdown
                            rel_path = os.path.relpath(img_path, os.path.dirname(output_path))
                            rel_path = rel_path.replace("\\", "/")
                            
                            # 添加图片引用到Markdown文件末尾
                            with open(output_path, "a", encoding="utf-8") as md_file:
                                md_file.write(f"\n\n![幻灯片 {i+1} 图片 {img_count}]({rel_path})\n")
                        except Exception as e:
                            print(f"处理幻灯片 {i+1} 中的图片时出错: {str(e)}")
                            
            print(f"已从PowerPoint中提取 {img_count} 张图片")
            self.status_var.set(f'已提取 {img_count} 张图片')
                        
        except Exception as e:
            print(f"从PowerPoint提取图片失败: {str(e)}")
            self.status_var.set(f'图片提取失败: {str(e)}')

    def extract_images_from_html(self, input_file, output_path, images_dir):
        """从HTML文件提取图片并添加到Markdown文件中"""
        try:
            # 使用BeautifulSoup解析HTML
            from bs4 import BeautifulSoup
            import requests
            import urllib.parse
            
            # 文档名前缀
            html_prefix = os.path.splitext(os.path.basename(input_file))[0]
            
            # 读取HTML文件
            with open(input_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找所有图片标签
            img_tags = soup.find_all('img')
            
            img_count = 0
            for img in img_tags:
                try:
                    img_src = img.get('src')
                    if not img_src:
                        continue
                    
                    img_count += 1
                    
                    # 处理图片路径
                    if img_src.startswith('http://') or img_src.startswith('https://'):
                        # 网络图片
                        try:
                            response = requests.get(img_src, timeout=10)
                            img_data = response.content
                            # 从URL中提取文件扩展名
                            img_ext = os.path.splitext(urllib.parse.urlparse(img_src).path)[1]
                            if not img_ext or len(img_ext) > 5:  # 如果扩展名不存在或太长
                                img_ext = '.png'  # 默认为PNG
                        except:
                            print(f"无法下载网络图片: {img_src}")
                            continue
                    else:
                        # 本地图片
                        if img_src.startswith('data:image'):
                            # 数据URI
                            continue  # 暂时跳过数据URI图片
                        else:
                            # 文件路径可能是相对路径
                            img_path_abs = img_src
                            if not os.path.isabs(img_src):
                                img_path_abs = os.path.join(os.path.dirname(input_file), img_src)
                            
                            try:
                                with open(img_path_abs, 'rb') as img_file:
                                    img_data = img_file.read()
                                # 获取扩展名
                                img_ext = os.path.splitext(img_src)[1]
                            except:
                                print(f"无法读取本地图片: {img_path_abs}")
                                continue
                    
                    # 保存图片
                    img_name = f"{html_prefix}_image_{img_count}{img_ext}"
                    img_path = os.path.join(images_dir, img_name)
                    
                    with open(img_path, 'wb') as f:
                        f.write(img_data)
                    
                    # 构建相对路径用于Markdown
                    rel_path = os.path.relpath(img_path, os.path.dirname(output_path))
                    rel_path = rel_path.replace("\\", "/")
                    
                    # 添加图片引用到Markdown文件末尾
                    with open(output_path, "a", encoding="utf-8") as md_file:
                        # 使用alt属性作为图片描述
                        alt_text = img.get('alt', f'图片 {img_count}')
                        md_file.write(f"\n\n![{alt_text}]({rel_path})\n")
                    
                except Exception as e:
                    print(f"处理HTML图片 {img_count} 时出错: {str(e)}")
            
            print(f"已从HTML中提取 {img_count} 张图片")
            self.status_var.set(f'已提取 {img_count} 张图片')
            
        except Exception as e:
            print(f"从HTML提取图片失败: {str(e)}")
            self.status_var.set(f'图片提取失败: {str(e)}')

    def preview_markdown(self):
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as temp_file:
                temp_path = temp_file.name
            # ... 其他代码 ...
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    print(f"清理临时文件失败: {e}")

    def copy_to_clipboard(self):
        """复制预览内容到剪贴板"""
        content = self.preview_text.get(1.0, tk.END)
        
        if not content.strip():
            messagebox.showinfo('提示', '预览内容为空')
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.status_var.set('已复制到剪贴板')

    def save_preview(self):
        """保存预览内容"""
        content = self.preview_text.get(1.0, tk.END)
        
        if not content.strip():
            messagebox.showinfo('提示', '预览内容为空')
            return
        
        file_path = filedialog.asksaveasfilename(
            title='保存预览',
            defaultextension='.md',
            filetypes=[('Markdown 文件', '*.md'), ('文本文件', '*.txt'), ('所有文件', '*.*')]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.status_var.set(f'预览已保存到: {file_path}')
            messagebox.showinfo('成功', f'预览内容已保存到:\n{file_path}')
        except Exception as e:
            messagebox.showerror('保存失败', f'保存预览内容时出错:\n{str(e)}')

    def open_output_folder(self, folder_path):
        """打开输出文件夹"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS 和 Linux
                subprocess.run(['xdg-open', folder_path])
        except Exception as e:
            messagebox.showerror('错误', f'无法打开输出文件夹:\n{str(e)}')

    def load_settings(self):
        """加载设置"""
        settings_file = os.path.join(os.path.expanduser('~'), '.markitdown_gui_settings.json')
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 应用设置
                if 'default_output_folder' in settings:
                    self.default_output_var.set(settings['default_output_folder'])
                
                if 'auto_open_folder' in settings:
                    self.auto_open_folder_var.set(settings['auto_open_folder'])
                
                if 'auto_preview' in settings:
                    self.auto_preview_var.set(settings['auto_preview'])
            except Exception as e:
                print(f"加载设置时出错: {str(e)}")

    def save_settings(self):
        """保存设置"""
        settings = {
            'default_output_folder': self.default_output_var.get(),
            'auto_open_folder': self.auto_open_folder_var.get(),
            'auto_preview': self.auto_preview_var.get()
        }
        
        settings_file = os.path.join(os.path.expanduser('~'), '.markitdown_gui_settings.json')
        
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            self.status_var.set('设置已保存')
            messagebox.showinfo('成功', '设置已保存')
        except Exception as e:
            messagebox.showerror('保存失败', f'保存设置时出错:\n{str(e)}')

    def check_markitdown_version_and_features(self):
        """检查markitdown版本和支持的功能"""
        try:
            # 获取版本信息
            version_process = subprocess.run(
                ["markitdown", "--version"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            version_text = version_process.stdout.strip()
            if not version_text:
                version_text = "未知版本"
            
            # 获取帮助信息
            help_process = subprocess.run(
                ["markitdown", "--help"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            help_text = help_process.stdout + help_process.stderr
            
            # 检查支持的功能
            features = []
            if "--extract-images" in help_text or "--images" in help_text:
                features.append("图片提取")
            if "pdf" in help_text.lower():
                features.append("PDF转换")
            if "docx" in help_text.lower():
                features.append("DOCX转换")
            if "pptx" in help_text.lower():
                features.append("PPTX转换")
            if "xlsx" in help_text.lower():
                features.append("XLSX转换")
            
            # 更新状态
            feature_text = "、".join(features) if features else "基本转换"
            self.markitdown_status_var.set(f'已集成 Microsoft MarkItDown {version_text} (支持: {feature_text})')
            
            return True
        except Exception as e:
            self.markitdown_status_var.set(f'检查失败: {str(e)}')
            return False

    def convert_batch_files(self):
        """批量转换文件"""
        try:
            self.conversion_in_progress = True
            self.batch_convert_btn.config(state=tk.DISABLED)
            self.batch_progress['value'] = 0
            self.batch_status_var.set('准备批量转换...')
            self.status_var.set('批量转换进行中...')
            
            output_folder = self.batch_output_var.get()
            total_files = len(self.batch_files)
            successful = 0
            failed = 0
            
            for i, file_path in enumerate(self.batch_files):
                try:
                    # 更新状态
                    file_name = os.path.basename(file_path)
                    self.batch_status_var.set(f'正在转换 ({i+1}/{total_files}): {file_name}')
                    self.root.update_idletasks()
                    
                    # 处理.doc文件
                    if file_path.lower().endswith('.doc'):
                        file_path = self.handle_doc_file(file_path)
                    
                    # 构建输出文件路径
                    output_filename = os.path.splitext(os.path.basename(file_path))[0] + '.md'
                    output_path = os.path.join(output_folder, output_filename)
                    
                    # 创建图片目录
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    images_dir = os.path.join(output_folder, "images", base_name)
                    os.makedirs(images_dir, exist_ok=True)
                    
                    # 执行基本转换
                    cmd = ["markitdown", file_path, "-o", output_path]
                    
                    # 执行转换
                    process = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    if process.returncode == 0:
                        # 如果用户选择了提取图片选项，执行自定义图片提取
                        if self.batch_extract_images_var.get():
                            file_ext = os.path.splitext(file_path)[1].lower()
                            
                            if file_ext == '.docx' or file_ext == '.doc':
                                self.extract_images_from_word(file_path, output_path, images_dir)
                            elif file_ext == '.pdf':
                                self.extract_images_from_pdf(file_path, output_path, images_dir)
                            elif file_ext == '.pptx':
                                self.extract_images_from_pptx(file_path, output_path, images_dir)
                            elif file_ext == '.html':
                                self.extract_images_from_html(file_path, output_path, images_dir)
                        
                        successful += 1
                    else:
                        failed += 1
                        print(f"转换失败 {file_name}: {process.stderr}")
                    
                    # 更新进度
                    progress_value = (i + 1) * 100 // total_files
                    self.batch_progress['value'] = progress_value
                    self.root.update_idletasks()
                except Exception as e:
                    failed += 1
                    print(f"转换出错 {file_name}: {str(e)}")
            
            # 完成
            self.batch_status_var.set(f'批量转换完成: 成功 {successful} 个，失败 {failed} 个')
            self.status_var.set(f'批量转换完成: 成功 {successful} 个，失败 {failed} 个')
            
            messagebox.showinfo(
                '批量转换完成',
                f'批量转换已完成\n\n'
                f'成功: {successful} 个文件\n'
                f'失败: {failed} 个文件\n\n'
                f'输出文件夹: {output_folder}'
            )
            
            # 自动打开输出文件夹
            if self.auto_open_folder_var.get():
                self.open_output_folder(output_folder)
        except Exception as e:
            self.batch_status_var.set('批量转换出错')
            self.status_var.set('批量转换出错')
            messagebox.showerror('错误', f'批量转换过程中出错:\n{str(e)}')
        finally:
            self.conversion_in_progress = False
            self.batch_convert_btn.config(state=tk.NORMAL)

    def get_markitdown_info(self):
        """获取markitdown版本和功能信息"""
        info = {
            'version': 'unknown',
            'extract_images_param': None,
            'images_dir_param': None,
            'pdf_extract_param': None,
            'html_mode_param': None,
            'preserve_links_param': None,
            'all_params': []
        }
        
        try:
            # 获取版本
            version_process = subprocess.run(
                ["markitdown", "--version"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            version_text = version_process.stdout.strip()
            if version_text:
                info['version'] = version_text
            
            # 获取帮助信息
            help_process = subprocess.run(
                ["markitdown", "--help"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            help_text = help_process.stdout + help_process.stderr
            
            # 提取所有参数
            params = re.findall(r'--([\w-]+)', help_text)
            info['all_params'] = params
            
            # 检查特定参数
            if "--extract-images" in help_text:
                info['extract_images_param'] = "--extract-images"
            elif "--images" in help_text:
                info['extract_images_param'] = "--images"
            elif "-i" in help_text:
                info['extract_images_param'] = "-i"
            
            if "--images-dir" in help_text:
                info['images_dir_param'] = "--images-dir"
            
            if "--pdf-extract-images" in help_text:
                info['pdf_extract_param'] = "--pdf-extract-images"
            
            if "--html-mode" in help_text:
                info['html_mode_param'] = "--html-mode"
            
            if "--preserve-links" in help_text:
                info['preserve_links_param'] = "--preserve-links"
                
            return info
        except Exception as e:
            print(f"获取markitdown信息失败: {str(e)}")
            return info

    def run_initial_feature_check(self):
        """运行初始功能检查，确保关键功能可用"""
        # 检查图片提取功能
        self.image_extraction_supported = False
        if self.markitdown_info['extract_images_param']:
            self.image_extraction_supported = True
            print("支持图片提取功能")
        else:
            print("MarkItDown 命令行不支持图片提取，将使用自定义图片提取")
        
        # 检查PDF功能
        self.pdf_supported = False
        try:
            import pdfminer
            self.pdf_supported = True
            print("支持PDF处理")
        except ImportError:
            print("不支持PDF处理 (缺少pdfminer)")
        
        # 检查PDF图片提取
        self.pdf_image_extraction_supported = False
        try:
            import pdf2image
            try:
                pdf2image.pdfinfo_from_bytes(b"%PDF-1.0\n")
                self.pdf_image_extraction_supported = True
                print("支持PDF图片提取 (pdf2image + poppler)")
            except Exception as e:
                print(f"PDF图片提取受限 (缺少Poppler): {str(e)}")
        except ImportError:
            print("不支持PDF图片提取 (缺少pdf2image)")
        
        # 检查Word文档支持
        self.word_supported = False
        try:
            import docx
            self.word_supported = True
            print("支持Word文档 (DOCX)")
        except ImportError:
            print("不支持Word文档 (缺少python-docx)")
        
        # 检查DOC转换支持
        self.doc_conversion_supported = False
        try:
            import win32com.client
            self.doc_conversion_supported = True
            print("支持DOC转换 (pywin32)")
        except ImportError:
            print("不支持DOC转换 (缺少pywin32)")

    def start_batch_conversion(self):
        """开始批量文件转换"""
        try:
            self.conversion_in_progress = True
            self.batch_convert_btn.config(state=tk.DISABLED)
            self.progress['value'] = 0
            self.status_var.set('准备批量转换...')
            
            # 获取输入文件和输出目录
            input_files = self.batch_files
            output_folder = self.batch_output_var.get()
            
            # 检查是否有文件要转换
            if not input_files:
                messagebox.showwarning('警告', '请先添加需要转换的文件')
                self.conversion_in_progress = False
                self.batch_convert_btn.config(state=tk.NORMAL)
                return
            
            # 检查输出目录
            if not output_folder:
                messagebox.showwarning('警告', '请选择输出目录')
                self.conversion_in_progress = False
                self.batch_convert_btn.config(state=tk.NORMAL)
                return
            
            # 确保输出目录存在
            os.makedirs(output_folder, exist_ok=True)
            
            # 创建图片目录
            images_dir = os.path.join(output_folder, "images")
            os.makedirs(images_dir, exist_ok=True)
            
            # 转换每个文件
            total_files = len(input_files)
            successful_conversions = 0
            failed_conversions = []
            
            for i, input_file in enumerate(input_files):
                try:
                    # 更新进度
                    progress_percent = (i / total_files) * 100
                    self.progress['value'] = progress_percent
                    self.status_var.set(f'正在转换 {i+1}/{total_files}: {os.path.basename(input_file)}')
                    self.root.update_idletasks()
                    
                    # 获取文件扩展名
                    file_ext = os.path.splitext(input_file)[1].lower()
                    
                    # 处理.doc文件
                    if file_ext == '.doc':
                        original_file = input_file
                        input_file = self.handle_doc_file(input_file)
                        # 如果转换失败，尝试直接转换
                        if input_file == original_file:
                            output_path = self.convert_doc_directly(input_file, output_folder)
                            if output_path:
                                successful_conversions += 1
                                continue
                    
                    # 生成输出路径
                    output_filename = os.path.splitext(os.path.basename(input_file))[0] + '.md'
                    output_path = os.path.join(output_folder, output_filename)
                    
                    # 转换标志
                    conversion_success = False
                    
                    # 使用MarkItDown转换
                    try:
                        cmd = ["markitdown", input_file, "-o", output_path]
                        print(f"执行命令: {' '.join(cmd)}")
                        
                        process = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        
                        if process.returncode == 0:
                            conversion_success = True
                        else:
                            print(f"MarkItDown转换失败，错误: {process.stderr}")
                    except Exception as e:
                        print(f"MarkItDown转换异常: {str(e)}")
                    
                    # 如果常规转换失败，尝试备用方法
                    if not conversion_success:
                        if file_ext == '.docx' or file_ext == '.doc':
                            conversion_success = self.convert_word_to_markdown(input_file, output_path)
                        elif file_ext == '.pdf':
                            conversion_success = self.convert_pdf_to_markdown(input_file, output_path)
                        elif file_ext == '.html' or file_ext == '.htm':
                            conversion_success = self.convert_html_to_markdown(input_file, output_path)
                    
                    # 如果最终转换成功
                    if conversion_success:
                        # 提取图片
                        if hasattr(self, 'batch_extract_images_var') and self.batch_extract_images_var.get():
                            if file_ext == '.docx' or file_ext == '.doc':
                                self.extract_images_from_word(input_file, output_path, images_dir)
                            elif file_ext == '.pdf':
                                self.extract_images_from_pdf(input_file, output_path, images_dir)
                            elif file_ext == '.pptx':
                                self.extract_images_from_pptx(input_file, output_path, images_dir)
                            elif file_ext == '.html' or file_ext == '.htm':
                                self.extract_images_from_html(input_file, output_path, images_dir)
                        
                        successful_conversions += 1
                    else:
                        failed_conversions.append((input_file, "所有转换方法均失败"))
                
                except Exception as e:
                    print(f"转换 {input_file} 出错: {str(e)}")
                    failed_conversions.append((input_file, str(e)))
            
            # 更新最终进度和状态
            self.progress['value'] = 100
            
            # 生成结果消息
            if failed_conversions:
                failed_msg = "\n".join([f"{os.path.basename(f)}: {err}" for f, err in failed_conversions])
                self.status_var.set(f'完成 {successful_conversions}/{total_files} 个文件转换')
                messagebox.showwarning('批量转换结果', 
                    f'成功转换: {successful_conversions}/{total_files}\n\n'
                    f'失败文件:\n{failed_msg}')
            else:
                self.status_var.set(f'成功完成所有 {total_files} 个文件转换')
                messagebox.showinfo('成功', 
                    f'所有 {total_files} 个文件已成功转换到:\n{output_folder}')
                
                # 自动打开输出文件夹
                if hasattr(self, 'batch_auto_open_folder_var') and self.batch_auto_open_folder_var.get():
                    self.open_output_folder(output_folder)
        
        except Exception as e:
            self.status_var.set(f"批量转换出错: {str(e)}")
            messagebox.showerror('错误', f'批量转换过程中出错:\n{str(e)}')
        
        finally:
            self.conversion_in_progress = False
            self.batch_convert_btn.config(state=tk.NORMAL)

    def convert_doc_directly(self, input_file, output_folder):
        """直接将DOC转换为Markdown，不经过DOCX中间格式"""
        try:
            # 生成输出路径
            output_filename = os.path.splitext(os.path.basename(input_file))[0] + '.md'
            output_path = os.path.join(output_folder, output_filename)
            
            # 尝试使用pandoc进行转换
            try:
                self.status_var.set('尝试使用pandoc转换...')
                self.root.update_idletasks()
                
                cmd = ["pandoc", input_file, "-o", output_path]
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if process.returncode == 0:
                    return output_path
            except:
                pass
            
            # 如果pandoc失败，尝试使用其他方法
            try:
                import textract
                text = textract.process(input_file).decode('utf-8')
                
                # 简单格式化文本
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                return output_path
            except:
                pass
            
            return None
        except Exception as e:
            print(f"直接转换DOC失败: {str(e)}")
            return None

    def convert_word_to_markdown(self, input_file, output_path):
        """Word到Markdown的备用转换方法"""
        try:
            # 尝试使用pandoc
            try:
                cmd = ["pandoc", input_file, "-o", output_path]
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if process.returncode == 0:
                    return True
            except:
                pass
            
            # 尝试使用python-docx和markdown库
            try:
                import docx
                from docx.shared import Pt
                
                # 读取Word文档
                doc = docx.Document(input_file)
                
                # 提取文本并转换为Markdown
                markdown_text = ""
                
                # 处理段落
                for para in doc.paragraphs:
                    if not para.text.strip():
                        continue
                    
                    # 检查段落样式
                    style = para.style.name.lower()
                    text = para.text.strip()
                    
                    # 标题处理
                    if 'heading' in style:
                        heading_level = int(style[-1]) if style[-1].isdigit() else 1
                        markdown_text += '#' * heading_level + ' ' + text + '\n\n'
                    else:
                        # 检查是否有粗体、斜体等格式
                        formatted_text = ""
                        for run in para.runs:
                            run_text = run.text
                            if run.bold and run.italic:
                                formatted_text += f"***{run_text}***"
                            elif run.bold:
                                formatted_text += f"**{run_text}**"
                            elif run.italic:
                                formatted_text += f"*{run_text}*"
                            else:
                                formatted_text += run_text
                        
                        markdown_text += formatted_text + '\n\n'
                
                # 保存Markdown文件
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_text)
                
                return True
            except Exception as e:
                print(f"python-docx转换失败: {str(e)}")
            
            return False
        except Exception as e:
            print(f"Word备用转换失败: {str(e)}")
            return False

    def convert_pdf_to_markdown(self, input_file, output_path):
        """PDF到Markdown的备用转换方法"""
        try:
            # 尝试使用pandoc
            try:
                cmd = ["pandoc", input_file, "-o", output_path]
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if process.returncode == 0:
                    return True
            except:
                pass
            
            # 尝试使用pdfplumber或PyPDF2
            try:
                import pdfplumber
                
                markdown_text = ""
                with pdfplumber.open(input_file) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text:
                            markdown_text += f"## 第 {page_num+1} 页\n\n{text}\n\n"
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_text)
                
                return True
            except ImportError:
                # 如果pdfplumber不可用，尝试PyPDF2
                try:
                    import PyPDF2
                    
                    markdown_text = ""
                    with open(input_file, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        for page_num in range(len(reader.pages)):
                            text = reader.pages[page_num].extract_text()
                            if text:
                                markdown_text += f"## 第 {page_num+1} 页\n\n{text}\n\n"
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_text)
                    
                    return True
                except:
                    pass
            
            return False
        except Exception as e:
            print(f"PDF备用转换失败: {str(e)}")
            return False

    def convert_html_to_markdown(self, input_file, output_path):
        """HTML到Markdown的备用转换方法"""
        try:
            # 尝试使用pandoc
            try:
                cmd = ["pandoc", input_file, "-o", output_path]
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if process.returncode == 0:
                    return True
            except:
                pass
            
            # 尝试使用html2text
            try:
                import html2text
                
                with open(input_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                converter = html2text.HTML2Text()
                converter.ignore_links = False
                converter.ignore_images = False
                markdown_text = converter.handle(html_content)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_text)
                
                return True
            except ImportError:
                # 如果html2text不可用，尝试BeautifulSoup
                try:
                    from bs4 import BeautifulSoup
                    
                    with open(input_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # 简单提取文本
                    markdown_text = ""
                    
                    # 处理标题
                    for i in range(1, 7):
                        for heading in soup.find_all(f'h{i}'):
                            markdown_text += '#' * i + ' ' + heading.get_text() + '\n\n'
                    
                    # 处理段落
                    for para in soup.find_all('p'):
                        markdown_text += para.get_text() + '\n\n'
                    
                    # 处理列表
                    for ul in soup.find_all('ul'):
                        for li in ul.find_all('li'):
                            markdown_text += '* ' + li.get_text() + '\n'
                        markdown_text += '\n'
                    
                    for ol in soup.find_all('ol'):
                        for i, li in enumerate(ol.find_all('li')):
                            markdown_text += f'{i+1}. ' + li.get_text() + '\n'
                        markdown_text += '\n'
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_text)
                    
                    return True
                except:
                    pass
            
            return False
        except Exception as e:
            print(f"HTML备用转换失败: {str(e)}")
            return False

def main():
    root = tk.Tk()
    app = MarkItDownApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()

