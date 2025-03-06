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
import time
import json
import re

class MarkItDownApp:
    def __init__(self, root):
        self.root = root
        self.root.title('MarkItDown 文档转换工具 1.0版 【飞歌制作 2025年3月5日】')
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
            ('所有支持的文件', '*.pdf;*.pptx;*.docx;*.xlsx;*.png;*.jpg;*.jpeg;*.mp3;*.wav;*.html;*.csv;*.json;*.xml;*.zip'),
            ('PDF 文档', '*.pdf'),
            ('PowerPoint 文档', '*.pptx'),
            ('Word 文档', '*.docx'),
            ('Excel 文档', '*.xlsx'),
            ('图片文件', '*.png;*.jpg;*.jpeg'),
            ('音频文件', '*.mp3;*.wav'),
            ('HTML 文件', '*.html'),
            ('文本文件', '*.csv;*.json;*.xml'),
            ('压缩文件', '*.zip')
        ]
        
        # 检查 markitdown 是否已安装
        self.check_markitdown_installed()

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
        
        # 标题
        title_label = ttk.Label(header_frame, text='MarkItDown 文档转换工具 1.0', style='Header.TLabel')
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
            text='MarkItDown 文档转换工具', 
            font=('微软雅黑', 18, 'bold')
        )
        app_title.pack(pady=(0, 10))
        
        # 版本信息
        version_label = ttk.Label(
            about_content, 
            text='版本 1.0.0', 
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
            text='PyPI',
            foreground='blue', 
            cursor='hand2'
        )
        pypi_link.pack(side=tk.LEFT, padx=5)
        pypi_link.bind('<Button-1>', lambda e: webbrowser.open_new('https://pypi.org/project/markitdown/'))
        
        ttk.Label(links_frame, text='|').pack(side=tk.LEFT, padx=5)
        
        # GitHub 链接
        github_link = ttk.Label(
            links_frame, 
            text='GitHub',
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
        
        version_label = ttk.Label(self.statusbar, text='v1.0.0')
        version_label.pack(side=tk.RIGHT)

    def check_markitdown_installed(self):
        """检查 markitdown 是否可用"""
        try:
            import markitdown
            self.markitdown_status_var.set(f'已集成 MarkItDown v{markitdown.__version__}')  # 添加版本号显示
            self.install_btn.config(state=tk.DISABLED)  # 禁用安装按钮
        except ImportError:
            self.markitdown_status_var.set('MarkItDown 未正确集成')
            self.install_btn.config(state=tk.DISABLED)  # 禁用安装按钮
            messagebox.showerror(
                "集成错误",
                "MarkItDown 组件未正确集成。\n"
                "请联系软件开发者获取完整版本。"
            )
        except Exception as e:
            self.markitdown_status_var.set(f'检查失败: {str(e)}')
            self.install_btn.config(state=tk.DISABLED)  # 禁用安装按钮

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
                        self.files_listbox.insert(tk.END, os.path.basename(file_path))
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

    def convert_file(self):
        """转换单个文件"""
        try:
            self.conversion_in_progress = True
            self.convert_btn.config(state=tk.DISABLED)
            self.progress['value'] = 0
            self.status_var.set('正在转换...')
            
            input_file = self.input_path_var.get()
            output_folder = self.output_path_var.get()
            
            # 生成输出路径（确保为字符串）
            os.makedirs(output_folder, exist_ok=True)
            output_filename = os.path.splitext(os.path.basename(input_file))[0] + '.md'
            output_path = os.path.join(output_folder, output_filename)  # 正确生成字符串路径
                
            # 修正命令行调用
            cmd = [
                "markitdown",  # 直接调用 markitdown 命令
                input_file,
                "-o", output_path
            ]
            
            # 执行转换
            self.progress['value'] = 10
            self.root.update_idletasks()
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # 读取输出并更新进度
            for line in process.stdout:
                if 'progress' in line.lower():
                    try:
                        progress_value = int(line.split(':')[1].strip().rstrip('%'))
                        self.progress['value'] = 10 + progress_value * 0.8  # 10% - 90%
                        self.root.update_idletasks()
                    except:
                        pass
            
            # 等待进程完成
            process.wait()
            
            # 检查是否成功
            if process.returncode == 0:
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
                stderr_output = process.stderr.read()
                self.status_var.set('转换失败')
                messagebox.showerror('转换失败', f'转换过程中出错:\n{stderr_output}')
        except Exception as e:
            self.status_var.set(f"转换出错: {str(e)}")
            messagebox.showerror('错误', f'转换过程中出错:\n{str(e)}')
        finally:
            self.conversion_in_progress = False
            self.convert_btn.config(state=tk.NORMAL)
            self.preview_btn.config(state=tk.NORMAL)

    def start_batch_conversion(self):
        """开始批量转换"""
        if self.conversion_in_progress:
            messagebox.showinfo('提示', '转换正在进行中，请等待完成')
            return
        
        if not self.batch_files:
            messagebox.showwarning('警告', '请先添加要转换的文件')
            return
        
        output_folder = self.batch_output_var.get()
        
        if not output_folder:
            messagebox.showwarning('警告', '请选择输出文件夹')
            return
        
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
            except Exception as e:
                messagebox.showerror('错误', f'创建输出文件夹失败: {str(e)}')
                return
        
        # 在新线程中启动批量转换
        threading.Thread(target=self.convert_batch_files, daemon=True).start()

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
                    
                    # 构建输出文件路径
                    output_filename = os.path.splitext(file_name)[0] + '.md'
                    output_path = os.path.join(output_folder, output_filename)
                    
                    # 构建命令行参数 - 修复这里的问题，使用 file_path 而不是 input_file
                    cmd = [
                        "markitdown",  # 直接调用 markitdown 命令
                        file_path,     # 正确使用 file_path 而非 input_file
                        "-o", output_path
                    ]
                    
                    # 执行转换
                    process = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    # 检查是否成功
                    if process.returncode == 0:
                        successful += 1
                    else:
                        failed += 1
                        print(f"转换失败 {file_name}: {process.stderr}")
                except Exception as e:
                    failed += 1
                    print(f"转换出错 {file_name}: {str(e)}")
                
                # 更新进度
                progress_value = (i + 1) * 100 // total_files
                self.batch_progress['value'] = progress_value
                self.root.update_idletasks()
            
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

    def preview_markdown(self):
        """预览 Markdown 内容"""
        input_file = self.input_path_var.get()
        
        if not input_file:
            messagebox.showwarning('警告', '请先选择要转换的文件')
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror('错误', '输入文件不存在')
            return
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # 构建命令行参数
            cmd = [
                "markitdown",
                input_file,
                '-o', temp_path
            ]
            
            # 执行转换
            self.status_var.set('正在生成预览...')
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # 检查是否成功
            if process.returncode == 0:
                # 读取转换后的文件内容
                with open(temp_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                
                # 更新预览
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(tk.END, markdown_content)
                
                self.status_var.set('预览已生成')
            else:
                self.status_var.set('预览生成失败')
                messagebox.showerror('预览失败', f'生成预览时出错:\n{process.stderr}')
        except Exception as e:
            self.status_var.set('预览生成出错')
            messagebox.showerror('错误', f'生成预览时出错:\n{str(e)}')
        finally:
            # 删除临时文件
            try:
                os.unlink(temp_path)
            except:
                pass

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

def main():
    root = tk.Tk()
    app = MarkItDownApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()

