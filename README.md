# AnyToMD

Windows 平台下的多格式文档转 Markdown 图形工具，基于 Python、Tkinter、MarkItDown 以及 Firecrawl AnyDoc / pdf-inspector 构建，目标是让常见文档在图形界面中完成可控、可验证、可预览的 Markdown 转换。

## 项目目标

- 面向 Windows 用户提供可直接操作的桌面式转换工具
- 支持单文件与批量转换
- 支持多种转换策略，以兼顾内容提取、图文混排与版式保真
- 优先保证转换效果与稳定性，而不是为统一流程牺牲结果

## 当前定位

- 当前版本：v0.1.7（版本日期 20260902）
- 平台：Windows
- 语言：Python
- 图形框架：Tkinter / customtkinter / ttk
- 打包工具：PyInstaller（打包脚本统一以 `sys.executable -m PyInstaller` 执行，避免本机多套 Python 环境混用导致依赖清单错位）
- 主程序：`AnyToMD_main.py`（**文件名固定不变**；项目版本号统一由源码内 `APP_VERSION` / `APP_VERSION_DATE` 常量控制，不再随版本号改名）
- 打包脚本：`AnyToMD_build.py`（唯一打包入口；生成的 EXE 名为 `AnyToMD_v{APP_VERSION}_{打包当日YYYYMMDD}.exe`）
- 体积审计脚本：`build_size_audit.py`
- 回归脚本：`regression_smoke.py`

## 主要能力

- 支持 PDF、Word、Excel、PPT、HTML、HTM、MHTML 等多类文档转换（含旧版 Office 格式 .doc / .xls / .ppt；其中 .xls/.ppt 兜底依赖 AnyDoc 引擎）
- 支持单文件转换与批量转换
- 支持转换后 Markdown 预览
- 支持“文档输出模式”与“图片输出策略”组合控制
- 支持图片嵌入、图片落地、OCR 等扩展能力
- 支持五种文档输出模式：智能转换（图文并存）、保持版式（页面转图片）、保留图像、保留文字、保留文字（含 OCR）
- 浏览器导出的书签 HTML（Netscape 格式）走专用解析路径，保留文件夹层级、备注与链接

## 增强引擎（2026-09-01 新增）

- **AnyDoc 兜底引擎**（Firecrawl AnyDoc，纯 Rust）：对 Office 文档（DOC/DOCX/XLS/XLSX/PPT/PPTX）在其他转换方法均失败时自动启用，保留标题层级与表格结构
- **pdf-inspector 引擎**（Firecrawl pdf-inspector，纯 Rust）：纯文本型 PDF 的智能识别（detect_pdf）与高质量 Markdown 输出；设置页新增「PDF 引擎策略」下拉：自动(默认) / 图文混排优先 / pdf-inspector优先（仅作用于智能转换模式，保持版式与扫描件 OCR 路径不变）

## 当前稳定性结论

- PDF 当前已形成专用图文混排转换路径，优先保证图文混合与相对位置保留；pdf-inspector 作为纯文本型 PDF 的补充引擎（默认自动模式，仅 text_based 触发）
- Word 当前整体转换效果较稳定；AnyDoc 作为 Office 转换的最终兜底
- HTML / HTM / MHTML 已补充图文混排与书签导出专用处理；书签文件采用 HTMLParser 事件流 + DL 栈结构化解析（不依赖 DOM 树容错，完整还原全部文件夹与可点击链接，避免 markitdown 0.1.7 对深层 HTML 的纯文本回退），回归与真实 Chrome 导出文件验证通过
- 工程整体可编译、可运行，当前更应优先做验证补强而不是频繁改动主流程

## 快速开始

### 方式一：直接运行 Python 主程序

```bash
python .\AnyToMD_main.py
```

### 方式二：运行已打包程序

- 可执行文件位于 `dist/AnyToMD_v0.1.7_20260902.exe`（重新打包后按打包当日日期生成）

### 方式三：重新打包

```bash
python .\AnyToMD_build.py
```

> 打包注意：请在**与依赖安装完全相同的单一 Python 环境**中运行。脚本内部已统一以 `sys.executable -m PyInstaller` 执行打包，从机制上避免“依赖收集解释器与 PyInstaller 解释器不一致”的问题；若本机装有多个 Python 版本或无关的 torch/torchvision/pandas 等大库，建议使用干净的虚拟环境打包，以免分析阶段加载无关二进制。

## 使用说明

- 简要使用指南见 [docs/使用指南.md](docs/使用指南.md)
- 审核结论与注意事项见 [docs/审核报告与注意事项.md](docs/审核报告与注意事项.md)
- 项目结构图清单见 [docs/项目结构图清单.md](docs/项目结构图清单.md)

## 仓库建议文档

- 贡献规范：[CONTRIBUTING.md](CONTRIBUTING.md)
- 安全说明：[SECURITY.md](SECURITY.md)
- 变更记录：[CHANGELOG.md](CHANGELOG.md)

## 已知重点注意事项

- PDF 相关转换代码目前视为冻结区，未经明确批准不建议改动
- 书签处理模块（Chrome/Netscape 书签 HTML 解析与渲染）自 2026-09-02 起为逻辑锁定区，与 PDF 冻结区同等待遇：未经专门批准禁止修改（模块内已置根因与思路注释）
- Word / PPT 的部分“保持版式”能力依赖本机 Office 与 COM 环境
- HTML / HTM / MHTML 的“保持版式”能力依赖 Edge 或 Chrome 无头打印能力
- 浏览器导出的书签 HTML 已有专用转换分支（HTMLParser 事件流 + DL 栈，完整保留文件夹层级与可点击链接；解析失败自动以 HTML 内嵌形式兜底），仍建议用真实样本复核
- OCR 模式依赖 Tesseract 安装与对应语言包
- 文件选择框已包含旧版 .xls / .ppt 类型（其转换兜底依赖 AnyDoc 引擎；未安装 AnyDoc 时功能检查会提示“不完全支持”）
- 打包体积控制说明：onnxruntime 仅收集运行所需原生二进制（tools / transformers / datasets 等已排除）；AnyDoc / pdf-inspector 的原生 .pyd 由打包脚本按实际安装位置收集，避免换机后“未安装”误报
- “图片输出策略”并不是对所有格式、所有模式都完全等价生效
- AnyDoc / pdf-inspector 均为可选增强引擎：未安装时自动回退到原有转换链路，不影响任何现有功能
- 设置页「检查功能完整性」可查看 AnyDoc / pdf-inspector 的安装状态与功能完整性

## 回归验证

```bash
python -m py_compile .\AnyToMD_main.py .\AnyToMD_build.py .\regression_smoke.py
python .\regression_smoke.py
```

> 说明：回归中包含真实样本级校验（PDF/Word/PPT/HTML/MHTML 各输出模式、书签链接保留等），部分用例结果依赖本机实际引擎能力（如无 EXIF 元数据的纯图片经 MarkItDown 可能返回空输出），请结合本机环境判断。

## 许可证

- 当前仓库尚未确定最终开源许可证，正式公开前请先补充许可证文件与授权说明
