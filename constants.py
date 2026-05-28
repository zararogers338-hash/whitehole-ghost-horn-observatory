# constants.py
# Bilingual (EN / ZH) UI text and configuration
# ─────────────────────────────────────────────────────────────────────────

APP_TITLE = "White Hole Project — Kalim Ghost Horn Observatory"

# ── Internal mode IDs (language-agnostic, used for logic matching) ───────
MODE_IDS = [
    "single_horn",
    "dual_horn",
    "delta_horn",
    "starfield",
    "chessboard",
    "cao",
    "keyword_terrain",
    "wrinkle_cloud",
    "postal",
    "postal_mobius",
    "oreo",
]

# Modes that require A/B group selection
AB_MODES = {"dual_horn", "delta_horn", "oreo", "postal_mobius"}

# Modes that support custom stopwords
STOPWORD_MODES = {"cao", "keyword_terrain", "wrinkle_cloud", "postal", "postal_mobius"}

# Modes that support highlight year slider
HIGHLIGHT_MODES = {"single_horn", "starfield"}

CAO_SUBMODE_IDS = ["fusion", "weight", "cube_3d"]

# ── Bilingual text pack ─────────────────────────────────────────────────

LANG_PACK = {
    # ── General ──
    "sidebar_title": {
        "en": "🌌 White Hole · Kalim Observatory",
        "zh": "🌌 白洞 · 卡利姆天文台",
    },
    "lang_toggle": {
        "en": "🌐 中文",
        "zh": "🌐 English",
    },
    "upload_header": {
        "en": "📄 Upload Papers",
        "zh": "📄 上传论文",
    },
    "scan_folder": {
        "en": "📁 Scan Local Folder",
        "zh": "📁 扫描本地文件夹",
    },
    "folder_path": {
        "en": "Path",
        "zh": "路径",
    },
    "scan_btn": {
        "en": "🔍 Scan",
        "zh": "🔍 开始扫描",
    },
    "scan_found": {
        "en": "Found **{n}** papers",
        "zh": "发现 **{n}** 篇论文",
    },
    "invalid_folder": {
        "en": "Invalid folder path",
        "zh": "无效的文件夹路径",
    },
    "loaded_papers": {
        "en": "Loaded Papers",
        "zh": "已加载论文",
    },
    "clear_cache": {
        "en": "🗑  Clear Cache",
        "zh": "🗑  清除缓存",
    },
    "mode_header": {
        "en": "#### 🛡️ Observation Mode",
        "zh": "#### 🛡️ 观测模式",
    },
    "time_range": {
        "en": "⏱ Time Range",
        "zh": "⏱ 时间范围",
    },
    "highlight_year": {
        "en": "🔴 Highlight Year",
        "zh": "🔴 高亮年份",
    },
    "group_selection": {
        "en": "#### 🅰️🅱️ Group Selection",
        "zh": "#### 🅰️🅱️ 分组选择",
    },
    "stopwords_label": {
        "en": "🚫 Custom Stopwords (comma-separated)",
        "zh": "🚫 自定义停用词（逗号分隔）",
    },
    "chart_type": {
        "en": "Chart Type",
        "zh": "图表类型",
    },
    "perm_labels": {
        "en": "Permanent Paper Labels (3-D)",
        "zh": "永久论文标签（3D 模式）",
    },
    "no_data_hint": {
        "en": "👈 Upload files or scan a folder to begin observation.",
        "zh": "👈 请上传文件或扫描文件夹以开始观测。",
    },
    "parsing": {
        "en": "Parsing papers…",
        "zh": "正在解析论文……",
    },
    "parse_fail": {
        "en": "⚠ {n} file(s) failed to parse",
        "zh": "⚠ {n} 个文件解析失败",
    },
    "no_data_range": {
        "en": "No data in current time window — adjust range.",
        "zh": "当前时间窗口无数据，请调整范围。",
    },
    "generate_pdf": {
        "en": "📄 Generate PDF Report",
        "zh": "📄 生成 PDF 报告",
    },
    "download_pdf": {
        "en": "⬇ Download Report PDF",
        "zh": "⬇ 下载报告 PDF",
    },
    "pdf_fail": {
        "en": "PDF generation failed: {e}",
        "zh": "PDF 生成失败：{e}",
    },
    "oreo_done": {
        "en": "Oreo Unfold complete — Dual-layer wrinkle cloud · Fibre connections · Report export",
        "zh": "Oreo 展开完成 — 双层褶皱云 · 纤维连接 · 报告导出",
    },
    "none": {
        "en": "None",
        "zh": "无",
    },

    # ── Mode display names ──
    "mode_single_horn": {
        "en": "Single Horn (Structure)",
        "zh": "单号角（结构）",
    },
    "mode_dual_horn": {
        "en": "Dual Horn Comparison (A/B)",
        "zh": "双号角对比（A/B）",
    },
    "mode_delta_horn": {
        "en": "ΔHORN Differential Map",
        "zh": "ΔHORN 差分图",
    },
    "mode_starfield": {
        "en": "Pseudo-3D Starfield (Keywords)",
        "zh": "伪 3D 星场（关键词）",
    },
    "mode_chessboard": {
        "en": "Chessboard + King Zone",
        "zh": "棋盘 + 王区",
    },
    "mode_cao": {
        "en": "Cao Keyword Analysis",
        "zh": "曹氏关键词分析",
    },
    "mode_keyword_terrain": {
        "en": "Keyword Square Terrain (3D)",
        "zh": "关键词方形地形（3D）",
    },
    "mode_wrinkle_cloud": {
        "en": "Wrinkle Cloud Map",
        "zh": "褶皱云图",
    },
    "mode_postal": {
        "en": "Postal Unfold",
        "zh": "邮政展开",
    },
    "mode_postal_mobius": {
        "en": "Postal-Möbius Unfold (3D)",
        "zh": "邮政-莫比乌斯展开（3D）",
    },
    "mode_oreo": {
        "en": "Oreo Unfold (Dual-Layer)",
        "zh": "Oreo 展开（双层）",
    },

    # ── Cao sub-modes ──
    "cao_fusion": {
        "en": "Fusion Bar",
        "zh": "融合柱状图",
    },
    "cao_weight": {
        "en": "Weight Bar",
        "zh": "权重柱状图",
    },
    "cao_cube_3d": {
        "en": "3D Cube View",
        "zh": "3D 立方体视图",
    },

    # ── Captions ──
    "cap_single_horn": {
        "en": "Dark regions ≈ high density ≈ structural compression",
        "zh": "暗色区域 ≈ 高密度 ≈ 结构压缩",
    },
    "cap_dual_horn": {
        "en": "Side-by-side comparison · Red highlight = A · Blue = B",
        "zh": "并排对比 · 红色高亮 = A · 蓝色 = B",
    },
    "cap_delta_horn": {
        "en": "Red = A advantage · Blue = B advantage · Gray = consensus",
        "zh": "红色 = A 优势 · 蓝色 = B 优势 · 灰色 = 共识",
    },
    "cap_starfield": {
        "en": "Yellow keyword stars embedded on horn surface (size ∝ importance)",
        "zh": "黄色关键词星点嵌入号角表面（大小 ∝ 重要性）",
    },
    "cap_chessboard": {
        "en": "Mid-section 2-D unfolding · Red box = King Zone",
        "zh": "中段二维展开 · 红色框 = 王区",
    },
    "cap_cao": {
        "en": "Cao Series — Weight + Sensitivity + Clustering",
        "zh": "曹氏系列 — 权重 + 敏感度 + 聚类",
    },
    "cap_keyword_terrain": {
        "en": "Horn cylinder unfolded to square terrain · Height & color reflect keyword density",
        "zh": "号角圆柱展开为方形地形 · 高度和颜色反映关键词密度",
    },
    "cap_wrinkle_cloud": {
        "en": "Binomial unfold — wrinkles show contraction / expansion & structural reorganisation",
        "zh": "二项式展开 — 褶皱展现收缩/扩张与结构重组",
    },
    "cap_postal": {
        "en": "Spatial discretisation + Manhattan fence denoising + blue-cold / yellow-warm spectrum",
        "zh": "空间离散化 + 曼哈顿围栏降噪 + 蓝冷/黄暖光谱",
    },
    "cap_postal_mobius": {
        "en": "Postal grid + Möbius chirality twist + dynamic wrinkles",
        "zh": "邮政网格 + 莫比乌斯手性扭转 + 动态褶皱",
    },
    "cap_oreo": {
        "en": "Dual-layer cookie · Upper = expansion · Lower = compression · Yellow keywords + fibre connections",
        "zh": "双层饼干结构 · 上层 = 扩张褶皱 · 下层 = 压缩收缩 · 黄色关键词 + 纤维连接",
    },

    # ── Footer ──
    "footer": {
        "en": "Principle: Not a scorer · Relative conclusions only · Must interpret with graphics",
        "zh": "原则：不是评分器 · 仅做相对结论 · 必须结合图形解读",
    },
}


# ── Convenience helpers ──────────────────────────────────────────────────

def T(key: str, lang: str = "en", **kwargs) -> str:
    """Get translated text.  Falls back to English if key/lang missing."""
    entry = LANG_PACK.get(key, {})
    text = entry.get(lang, entry.get("en", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text


def get_mode_display_names(lang: str = "en") -> list[str]:
    """Return ordered list of mode display names in the given language."""
    return [T(f"mode_{mid}", lang) for mid in MODE_IDS]


def get_cao_display_names(lang: str = "en") -> list[str]:
    """Return Cao sub-mode display names."""
    return [T(f"cao_{sid}", lang) for sid in CAO_SUBMODE_IDS]


def get_caption(mode_id: str, lang: str = "en") -> str:
    """Return caption for the given mode ID."""
    return T(f"cap_{mode_id}", lang)
