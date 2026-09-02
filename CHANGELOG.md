# 变更记录

## v0.1.6-test1

### 已完成

- 完成主界面选项卡样式与布局优化
- 调整单文件页面布局，修复浏览按钮遮挡问题
- 完成 PDF 专用图文混排转换路径修复
- 恢复默认智能转换思路，确保 PDF 与 Word 更符合图文混合预期
- 完成 HTML / HTM / MHTML 图文混排、主内容优先与书签导出专用解析修复
- 增强回归脚本，补充 MHTML 与书签 HTML 验证
- 完成一轮工程级审核与仓库文档整理

## 2026-09-01 更新（v0.1.6 增强版）

### 新增功能

- **AnyDoc 兜底引擎**（Firecrawl AnyDoc，纯 Rust）：对 Office 文档（DOC/DOCX/XLS/XLSX/PPT/PPTX）在其他转换方法均失败时自动启用，保留标题层级与表格结构
- **pdf-inspector 引擎**（Firecrawl pdf-inspector，纯 Rust）：纯文本型 PDF 的智能识别与高质量 Markdown 输出
- 设置页新增「PDF 引擎策略」下拉：自动(默认) / 图文混排优先 / pdf-inspector优先（仅作用于智能转换模式，保持版式与扫描件 OCR 路径不变）
- 设置页新增「PDF引擎策略」持久化保存与加载

### 修复与改进

- 修正「功能完整性检查」报告中 `✗ 命令行DOCX不支持` 的误导性显示，补充说明"本软件通过API直接支持DOCX，无需命令行"
- 「功能完整性检查」新增 AnyDoc / pdf-inspector 引擎检测项、格式支持项与缺失建议
- 新增体积审计脚本 `build_size_audit.py`（打包后观察 EXE 体积与各模块贡献，不强制大小）
- 标题栏、关于页版本日期更新为 20260901
- 关于页内容更新：补充 AnyDoc / pdf-inspector 增强引擎说明

### 当前维护策略

- PDF 逻辑冻结
- 稳定优先，谨慎改动主转换流程
- 下一阶段重点验证 Word / PPT / Excel / 纯图片类样本效果与设置项边界

## 2026-09-02 更新（v0.1.7）

### 版本与工程结构

- 主程序文件名固定为 `AnyToMD_main.py`，不再随版本号变化；项目版本号统一由源码内 `APP_VERSION` / `APP_VERSION_DATE` 两个常量控制
- 打包脚本从主程序源码读取 `APP_VERSION` 生成 EXE 名（`AnyToMD_v{APP_VERSION}_{打包当日YYYYMMDD}.exe`），版本号升级只需改常量
- 打包命令统一为 `sys.executable -m PyInstaller`，从机制上杜绝“依赖收集解释器与 PyInstaller 解释器不一致”导致的双环境混用问题

### 新增功能

- 文件选择框与“添加文件夹”补充旧版格式类型：Excel 支持 `.xlsx;*.xls`、PowerPoint 支持 `*.pptx;*.ppt`（旧版 Office 兜底依赖 AnyDoc 引擎）

### 修复

- 修复浏览器书签 HTML 转 MD 链接丢失：书签文件改为 HTMLParser 事件流 + DL 栈结构化解析（不依赖 DOM 树容错，真实 Chrome 导出 4558 条链接完整还原），并绕开 markitdown 0.1.7 对深层 HTML 的纯文本回退；解析异常时自动以 HTML 内嵌形式兜底
- 修复书签 MD 深层条目被渲染为代码块的问题：书签渲染改为“标题承载层级 + 0 缩进分组列表”（不再按 DL 深度缩进 + 空行分隔，杜绝“空行后 ≥4 空格”被 Markdown 判为缩进代码块而显示为原始代码）；链接文本内 `[`/`]` 转义、URL 用尖括号包裹、`javascript:` 等危险协议降级为“标题 + 行内代码”展示
- PPT 智能（图文并存）增强：检测到 Office（PowerPoint）时先将 .ppt/.pptx 渲染为 PDF，再复用现有 PDF 图文混排引擎按页输出“文字 + 图块”混排（无 Office 自动回退 markitdown/anydoc 原路径）
- 修复 PPT 旧格式（.ppt）无法使用“保持版式”：.ppt 与 .pptx 一并接入 Office COM→PDF→整页图链路（需本机安装 PowerPoint）
- 修复打包后 AnyDoc / pdf-inspector 提示“未安装”：二者为 PyO3 单模块扩展，`--collect-all` 对其无效，改为按实际安装位置收集原生 `.pyd` 加入包内

### 打包优化

- onnxruntime 由整包 `--collect-all` 改为仅收集原生二进制（`--collect-binaries`），并排除 `onnxruntime.transformers / tools / datasets / quantization` 与 `transformers` 等巨型子模块，EXE 体积预计回落约 40+ MiB、构建时间显著缩短，同时降低打包分析阶段触发本机 torch/torchvision 等无关二进制加载的概率

### 维护策略

- PDF 逻辑冻结不变
- 打包环境建议固定单一 Python（推荐干净虚拟环境），避免多版本 Python 与无关科学计算库干扰
- 下一阶段：在统一环境下重建 EXE 实测体积与功能完整性，并继续补强 Excel / 旧版 Office / 纯图片类真实样本验证
