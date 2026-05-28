# White Hole Ghost Horn Observatory / 白洞幽角天文台

> **Repository name / 仓库名：** `whitehole-ghost-horn-observatory`  
> **Current version / 当前版本：** `v2.1.0`  
> **Suggested release tag / 建议发布标签：** `v2.1.0`  
> **License / 许可证：** MIT

---

## 中文说明

**White Hole Ghost Horn Observatory（白洞幽角天文台）** 是一个用于论文、报告、文献集合的交互式可视化工具。它会读取 PDF、DOCX、TXT、MD 文件，从文件名或文本中识别年份，从正文中提取关键词，并把文献集合映射成多种可交互图形：3D 幽角结构、关键词星场、关键词地形、棋盘展开、褶皱云、A/B 对照图、差分图、Oreo 双层展开图等。

这个项目适合用来：

- 观察一批论文在时间轴上的密度变化；
- 比较两篇或两组文献之间的关键词差异；
- 用更直观的 3D/2D 图形展示文献主题、关键词权重和聚类；
- 为课程展示、研究汇报、资料整理或数据探索生成可视化结果；
- 在中英文界面之间切换，处理中文或英文材料。

### 主要功能

| 功能 | 说明 |
|---|---|
| 文件读取 | 支持 PDF、DOCX、TXT、MD；可以上传文件，也可以扫描本地文件夹。 |
| 年份识别 | 优先从文件名识别 `19xx` / `20xx` 年份，找不到时从正文中提取年份。 |
| 关键词提取 | 中文使用 `jieba`，英文使用内置停用词和词频统计；支持自定义停用词。 |
| 3D Ghost Horn | 把文献时间、权重、密度映射成可旋转的 3D “幽角”结构。 |
| A/B 对比 | 支持 Dual Horn、ΔHORN 差分图和 Oreo 双层可视化。 |
| 报告导出 | Oreo 模式支持导出 PDF 报告。 |
| 双语界面 | 内置中文 / English 切换。 |
| 启动方式 | 支持 Streamlit 浏览器模式，也支持可选 PyQt6 桌面壳。 |

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/whitehole-ghost-horn-observatory.git
cd whitehole-ghost-horn-observatory

# 2. 创建虚拟环境，推荐但不是必须
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动浏览器版
python launcher.py run
# 或者
streamlit run streamlit_app.py
```

Windows 用户也可以直接双击：

```text
run.bat
```

### 可选：启动桌面壳

桌面壳会用 PyQt6 WebEngine 嵌入 Streamlit 页面。若只想用浏览器版，可以不管这一部分。

```bash
pip install "PyQt6>=6.5" "PyQt6-WebEngine>=6.5"
python launcher.py desktop
```

Windows 用户可以双击：

```text
desktop.bat
```

### 命令行

```bash
python launcher.py          # 默认等同于 python launcher.py run
python launcher.py run      # 启动 Streamlit 浏览器版
python launcher.py desktop  # 启动 PyQt6 桌面壳
python launcher.py info     # 输出项目元数据
```

### 项目结构

```text
whitehole-ghost-horn-observatory/
├── constants.py             # 双语 UI 文本、模式 ID、说明文案
├── launcher.py              # GitHub 友好启动器，无授权墙，默认可直接运行
├── main.py                  # 可选 PyQt6 桌面入口
├── streamlit_app.py         # Streamlit 主应用
├── utils.py                 # 文件读取、年份识别、关键词提取、确定性随机工具
├── plot_functions.py        # 绘图函数统一导出
├── plot/
│   ├── core_helpers.py      # Ghost Horn 网格、曲面投影等核心几何工具
│   ├── single_modes.py      # 单体可视化：Single Horn、Starfield、Terrain、Wrinkle Cloud
│   ├── comparison_modes.py  # A/B 对比、ΔHORN、Oreo、PDF 报告
│   └── special_modes.py     # Chessboard、Cao Analysis、Postal-Möbius
├── requirements.txt
├── pyproject.toml
├── CHANGELOG.md
├── LICENSE
├── .gitignore
├── run.bat / run.sh
└── desktop.bat / desktop.sh
```

### GitHub 发布建议

建议仓库信息这样填写：

- **Repository name:** `whitehole-ghost-horn-observatory`
- **Description:** `Bilingual Streamlit/Plotly toolkit for visualizing academic-paper corpora as 3D Ghost Horn structures and keyword maps.`
- **Topics:** `streamlit`, `plotly`, `bibliometrics`, `knowledge-visualization`, `academic-papers`, `keyword-extraction`, `python`, `chinese-nlp`, `research-tools`, `data-visualization`
- **Release tag:** `v2.1.0`
- **Release title:** `White Hole Ghost Horn Observatory v2.1.0`

### 从原始包到本发布包的清理

本 ZIP 已经做过这些清理：

- 删除 `__pycache__` 和 `.pyc` 编译缓存；
- 移除本地授权 key，避免把私有授权文件发到公开仓库；
- 去掉运行授权墙，让 `python launcher.py` 可以直接启动；
- 将混淆壳还原成可读源码，方便 GitHub 审阅和二次开发；
- 补齐 `README.md`、`LICENSE`、`CHANGELOG.md`、`.gitignore`、`pyproject.toml`；
- 修复启动器行为：现在直接运行 `python launcher.py` 不再报缺少 `cmd` 参数，而是默认启动应用。

---

## English

**White Hole Ghost Horn Observatory** is an interactive visualization toolkit for academic papers, reports, and document collections. It reads PDF, DOCX, TXT, and MD files, extracts publication years and keywords, and maps the corpus into several interactive views: 3D Ghost Horn structures, keyword starfields, keyword terrains, chessboard unfolds, wrinkle clouds, A/B comparison maps, differential maps, and Oreo-style dual-layer visualizations.

It is useful for:

- exploring temporal density patterns in a paper collection;
- comparing keyword differences between two papers or two document groups;
- presenting document topics, keyword weights, and clusters through 2D/3D visualizations;
- preparing classroom demos, research presentations, literature reviews, and exploratory reports;
- switching between Chinese and English UI while processing Chinese or English documents.

### Features

| Feature | Description |
|---|---|
| File ingestion | Supports PDF, DOCX, TXT, and MD. Upload files or scan a local folder. |
| Year extraction | Detects `19xx` / `20xx` years from filenames first, then from document text. |
| Keyword extraction | Uses `jieba` for Chinese and built-in stopword/frequency extraction for English. |
| 3D Ghost Horn | Maps document time, mass, and density into an interactive 3D horn surface. |
| A/B comparison | Includes Dual Horn, ΔHORN differential view, and Oreo dual-layer visualization. |
| PDF export | Oreo mode can export an observation report as PDF. |
| Bilingual UI | Built-in Chinese / English toggle. |
| Launch modes | Streamlit browser mode plus an optional PyQt6 desktop shell. |

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/whitehole-ghost-horn-observatory.git
cd whitehole-ghost-horn-observatory

# 2. Create a virtual environment, recommended but optional
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the browser app
python launcher.py run
# or
streamlit run streamlit_app.py
```

Windows users can also double-click:

```text
run.bat
```

### Optional Desktop Shell

The desktop shell embeds the Streamlit page in a PyQt6 WebEngine window. You can ignore this section if the browser version is enough.

```bash
pip install "PyQt6>=6.5" "PyQt6-WebEngine>=6.5"
python launcher.py desktop
```

Windows users can double-click:

```text
desktop.bat
```

### CLI

```bash
python launcher.py          # same as python launcher.py run
python launcher.py run      # launch Streamlit browser mode
python launcher.py desktop  # launch the PyQt6 desktop shell
python launcher.py info     # print project metadata
```

### Repository Publishing Metadata

Recommended GitHub fields:

- **Repository name:** `whitehole-ghost-horn-observatory`
- **Description:** `Bilingual Streamlit/Plotly toolkit for visualizing academic-paper corpora as 3D Ghost Horn structures and keyword maps.`
- **Topics:** `streamlit`, `plotly`, `bibliometrics`, `knowledge-visualization`, `academic-papers`, `keyword-extraction`, `python`, `chinese-nlp`, `research-tools`, `data-visualization`
- **Release tag:** `v2.1.0`
- **Release title:** `White Hole Ghost Horn Observatory v2.1.0`

### Release Cleanup Notes

This ZIP has been cleaned for GitHub publishing:

- removed `__pycache__` and `.pyc` cache files;
- removed the local license key to avoid publishing private authorization material;
- removed the runtime license gate so the project starts directly;
- restored readable source files from the protected wrapper format;
- added `README.md`, `LICENSE`, `CHANGELOG.md`, `.gitignore`, and `pyproject.toml`;
- changed the launcher so `python launcher.py` now launches the app by default instead of failing with a missing `cmd` argument.

## Citation / Acknowledgement

If this tool helps your course project, research presentation, or dataset exploration, please cite or link back to the repository.
