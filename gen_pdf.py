# -*- coding: utf-8 -*-
"""
摄像机硬件科普系列 第001-007期 PDF生成脚本
- 使用 Windows 中文字体，彻底解决乱码问题
"""
import os, sys, re

# ── 桌面路径 ──────────────────────────────────────────────
DESKTOP  = os.path.join(os.path.expanduser("~"), "Desktop")
OUTPUT   = os.path.join(DESKTOP, "摄像机硬件科普系列_第001-007期.pdf")

# ── 文章目录 ──────────────────────────────────────────────
ARTICLES = [
    ("第001期", "传感器全解析",
     "c:/Users/Administrator/WorkBuddy/20260323171354/摄像机硬件科普_第001期_传感器全解析.md"),
    ("第002期", "像素与分辨率的真相",
     "c:/Users/Administrator/WorkBuddy/20260323171354/摄像机硬件科普_第002期_像素与分辨率的真相.md"),
    ("第003期", "光学变焦vs数字变焦vsAI超分辨率变焦",
     "c:/Users/Administrator/WorkBuddy/20260323171354/摄像机硬件科普_第003期_光学变焦vs数字变焦vsAI超分辨率变焦.md"),
    ("第004期", "帧率的秘密",
     "c:/Users/Administrator/WorkBuddy/20260323171354/摄像机硬件科普_第004期_帧率的秘密.md"),
    ("第005期", "光圈与景深",
     "c:/Users/Administrator/WorkBuddy/20260323171354/摄像机硬件科普_第005期_光圈与景深.md"),
    ("第006期", "快门与曝光",
     "c:/Users/Administrator/WorkBuddy/20260323171354/摄像机硬件科普_第006期_快门与曝光.md"),
    ("第007期", "低噪声与高信噪比",
     "c:/Users/Administrator/WorkBuddy/20260323171354/摄像机硬件科普_第007期_低噪声与高信噪比.md"),
]

# ── 颜色常量 ──────────────────────────────────────────────
COLOR_NAVY   = (0x1a, 0x3a, 0x6c)
COLOR_BLUE   = (0x2e, 0x86, 0xc1)
COLOR_ACCENT = (0xe8, 0x6c, 0x2a)
COLOR_GRAY   = (0.40, 0.40, 0.40)
COLOR_LGRAY  = (0.92, 0.92, 0.92)
COLOR_DKGRAY = (0.22, 0.22, 0.22)
COLOR_WHITE  = (1, 1, 1)

def rgb_hex(t):
    return t[0]/255.0, t[1]/255.0, t[2]/255.0

# ══════════════════════════════════════════════════════════
#  中文字体注册（必须在任何 canvas 操作前完成）
# ══════════════════════════════════════════════════════════
FONT_DIR = "C:/Windows/Fonts"

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as cv
from reportlab.lib.pagesizes import A4

# 注册字体（取别名方便引用）
pdfmetrics.registerFont(TTFont("CN_Song",  f"{FONT_DIR}/STSONG.TTF"))       # 宋体（正文）
pdfmetrics.registerFont(TTFont("CN_Hei",   f"{FONT_DIR}/simhei.ttf"))       # 黑体（标题粗体）
pdfmetrics.registerFont(TTFont("CN_Kai",   f"{FONT_DIR}/STKAITI.TTF"))      # 楷体（引用）
pdfmetrics.registerFont(TTFont("CN_Mono",  f"{FONT_DIR}/simsun.ttc"))       # 宋体（代码区，等宽）

# 加粗版本（ReportLab 用 B + 字体名自动合成，或手动注册）
pdfmetrics.registerFont(TTFont("CN_Song_B",  f"{FONT_DIR}/STSONG.TTF"))
pdfmetrics.registerFont(TTFont("CN_Hei_B",   f"{FONT_DIR}/simhei.ttf"))

# 字体别名（贯穿全文）
FONT_BODY   = "CN_Song"    # 正文
FONT_TITLE  = "CN_Hei"     # 标题
FONT_BOLD   = "CN_Hei"     # 粗体（正文内强调）
FONT_QUOTE  = "CN_Kai"    # 引用
FONT_MONO   = "CN_Song"   # 代码（中文宋体兼顾英文等宽）

# ══════════════════════════════════════════════════════════
#  工具函数
# ══════════════════════════════════════════════════════════

def read_md(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def wrap_text(canvas, text, x, y, width, font, size, color, line_h=None):
    """在 canvas 上逐字/逐词渲染中文文本，自动换行，返回最终 y。"""
    if line_h is None:
        line_h = size * 1.75
    canvas.saveState()
    canvas.setFont(font, size)
    canvas.setFillColor(color)

    # 中文字符宽度估算（按字面宽度）
    def text_width(s):
        return sum(1.0 if '\u4e00' <= c <= '\u9fff' else 0.55
                   for c in s) * size * 0.48

    lines = []
    cur   = ""
    cur_w = 0
    for ch in text:
        w = (1.0 if '\u4e00' <= ch <= '\u9fff' else 0.55) * size * 0.48
        if cur_w + w <= width:
            cur   += ch
            cur_w += w
        else:
            if cur:
                lines.append(cur)
            cur   = ch
            cur_w = w
    if cur:
        lines.append(cur)

    cur_y = y
    for l in lines:
        canvas.drawString(x, cur_y, l)
        cur_y -= line_h
    canvas.restoreState()
    return cur_y - 2

# ══════════════════════════════════════════════════════════
#  PDF 渲染引擎
# ══════════════════════════════════════════════════════════

PAGE_W    = A4[0]     # 595.27
PAGE_H    = A4[1]     # 841.89
MARGIN_L  = 60
MARGIN_R  = 60
MARGIN_T  = 65
MARGIN_B  = 60
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R   # 475

class PDFRenderer:
    def __init__(self, path):
        self.cv         = cv.Canvas(path, pagesize=A4)
        self.page_h     = PAGE_H
        self.y          = PAGE_H - MARGIN_T
        self.x          = MARGIN_L
        self.w          = CONTENT_W
        self._page_num  = 0

    def check_page(self, needed=25):
        if self.y - needed < MARGIN_B:
            self.new_page()

    def new_page(self):
        self.cv.showPage()
        self.y = self.page_h - MARGIN_T
        self._page_num += 1

    # ── 段落 ───────────────────────────────────────────────
    def add_paragraph(self, text, font=None, size=10, color=None,
                       indent=0, space_before=0, space_after=6):
        font   = font   or FONT_BODY
        color  = color  or COLOR_GRAY
        if not text.strip():
            self.y -= space_after
            return
        self.check_page(space_before + size * 2)
        self.y -= space_before
        self.y = wrap_text(self.cv, text.strip(),
                           self.x + indent, self.y,
                           self.w - indent, font, size, color)
        self.y -= space_after

    # ── 标题 ───────────────────────────────────────────────
    def add_heading1(self, text):
        self.y -= 10
        self.check_page(35)
        self.cv.saveState()
        self.cv.setFillColorRGB(*rgb_hex(COLOR_NAVY))
        # 左侧装饰条
        self.cv.setFillColorRGB(*rgb_hex(COLOR_BLUE))
        self.cv.rect(self.x, self.y - 4, 4, 20, fill=1, stroke=0)
        self.cv.setFillColorRGB(*rgb_hex(COLOR_NAVY))
        self.y -= 6
        self.y = wrap_text(self.cv, text,
                           self.x + 12, self.y,
                           self.w - 12, FONT_TITLE, 15, COLOR_NAVY, 15 * 1.6)
        self.y -= 6
        # 下划线
        self.cv.setStrokeColorRGB(*rgb_hex(COLOR_BLUE))
        self.cv.setLineWidth(1.5)
        self.cv.line(self.x + 12, self.y, self.x + self.w, self.y)
        self.cv.restoreState()
        self.y -= 16

    def add_heading2(self, text):
        self.y -= 7
        self.check_page(28)
        self.y = wrap_text(self.cv, text,
                           self.x, self.y,
                           self.w, FONT_TITLE, 12, COLOR_BLUE)
        self.y -= 6
        self.cv.saveState()
        self.cv.setStrokeColorRGB(*rgb_hex(COLOR_BLUE))
        self.cv.setLineWidth(1)
        self.cv.line(self.x, self.y, self.x + 60, self.y)
        self.cv.restoreState()
        self.y -= 12

    def add_heading3(self, text):
        self.y -= 5
        self.check_page(22)
        self.y = wrap_text(self.cv, text,
                           self.x, self.y,
                           self.w, FONT_BOLD, 10.5, COLOR_ACCENT)
        self.y -= 10

    # ── 分割线 ─────────────────────────────────────────────
    def add_separator(self, color=None):
        color = color or COLOR_BLUE
        self.y -= 6
        self.cv.saveState()
        self.cv.setStrokeColorRGB(*rgb_hex(color))
        self.cv.setLineWidth(0.8)
        self.cv.line(self.x, self.y, self.x + self.w, self.y)
        self.cv.restoreState()
        self.y -= 8

    def add_divider(self):
        self.y -= 4

    # ── 表格 ───────────────────────────────────────────────
    def add_table(self, rows):
        if not rows:
            return
        col_cnt   = len(rows[0])
        col_w     = self.w / col_cnt
        row_h     = 18
        hdr_h     = 22

        def cell_lines(text, cw):
            if not text:
                return 1
            chars = int(cw / (9.5 * 0.55))
            return max(1, len(text) // chars + 1)

        def calc_row_h(row_vals):
            return max(cell_lines(v, col_w - 6) for v in row_vals) * row_h + 4

        cur_i = 0
        while cur_i < len(rows):
            batch, bh = [], 0
            while cur_i < len(rows) and bh + calc_row_h(rows[cur_i]) < self.y - MARGIN_B:
                h = calc_row_h(rows[cur_i])
                batch.append((cur_i, rows[cur_i], h))
                bh += h
                cur_i += 1
            if not batch:
                self.new_page()
                continue

            y0 = self.y
            for ri, (oi, row, rh) in enumerate(batch):
                is_hdr = (oi == 0)
                y1 = y0 - rh

                # 背景
                self.cv.saveState()
                bg = rgb_hex(COLOR_NAVY) if is_hdr else (0.97, 0.97, 0.97)
                self.cv.setFillColorRGB(*bg)
                self.cv.rect(self.x, y1, self.w, rh, fill=1, stroke=0)
                self.cv.restoreState()

                # 边框线
                self.cv.saveState()
                self.cv.setStrokeColorRGB(0.78, 0.78, 0.78)
                self.cv.setLineWidth(0.3)
                self.cv.rect(self.x, y1, self.w, rh, fill=0, stroke=1)
                self.cv.restoreState()

                # 文字
                tx = self.x + 4
                for ci, cell in enumerate(row):
                    cx = self.x + ci * col_w + 4
                    cw2 = col_w - 8
                    fclr = COLOR_WHITE if is_hdr else COLOR_DKGRAY
                    fsz  = 9 if not is_hdr else 9.5
                    fnt  = FONT_TITLE  if is_hdr else FONT_BODY
                    # 多行
                    lines_raw = []
                    line_buf  = ""
                    lx = 0
                    for ch in (cell or ""):
                        w = (1.0 if '\u4e00' <= ch <= '\u9fff' else 0.55) * fsz * 0.55
                        if lx + w <= cw2:
                            line_buf += ch
                            lx += w
                        else:
                            lines_raw.append(line_buf)
                            line_buf = ch
                            lx = w
                    if line_buf:
                        lines_raw.append(line_buf)
                    if not lines_raw:
                        lines_raw = [""]
                    for li, ln in enumerate(lines_raw[:int(rh / row_h)]):
                        ty = y1 + rh - row_h + 4 - li * (fsz * 1.6)
                        if ty > y1:
                            self.cv.saveState()
                            self.cv.setFont(fnt, fsz)
                            self.cv.setFillColorRGB(*fclr)
                            self.cv.drawString(cx, ty, ln)
                            self.cv.restoreState()
                y0 = y1
            self.y = y0 - 3
            if cur_i < len(rows):
                self.new_page()

    # ── 代码块 ─────────────────────────────────────────────
    def add_code_block(self, lines):
        lh    = 11
        pad   = 8
        bh    = len(lines) * lh + pad * 2
        self.check_page(bh + 6)
        self.y -= 4

        self.cv.saveState()
        self.cv.setFillColorRGB(0.97, 0.97, 0.97)
        self.cv.rect(self.x, self.y - bh, self.w, bh, fill=1, stroke=0)
        self.cv.restoreState()

        # 左边蓝线
        self.cv.saveState()
        self.cv.setFillColorRGB(*rgb_hex(COLOR_BLUE))
        self.cv.rect(self.x, self.y - bh, 3, bh, fill=1, stroke=0)
        self.cv.restoreState()

        ty = self.y - pad
        for line in lines:
            if ty - lh < self.y - bh:
                break
            self.cv.saveState()
            self.cv.setFont(FONT_MONO, 8.5)
            self.cv.setFillColor(COLOR_DKGRAY)
            self.cv.drawString(self.x + 10, ty - lh + 2, line[:120])
            self.cv.restoreState()
            ty -= lh
        self.y -= bh

    # ── 页脚 ───────────────────────────────────────────────
    def footer(self):
        self.cv.saveState()
        self.cv.setFont(FONT_BODY, 8)
        self.cv.setFillColorRGB(0.55, 0.55, 0.55)
        self.cv.drawCentredString(PAGE_W / 2, MARGIN_B - 18,
                                  "摄像机硬件科普系列 · 第001-007期  |  2026年3月")
        # 页码
        pg = self._page_num + 1
        self.cv.drawRightString(PAGE_W - MARGIN_R, MARGIN_B - 18, f"{pg}")
        self.cv.restoreState()

    def save(self, total_pages):
        self.footer()
        self.cv.save()
        print(f"[OK] PDF 已生成: {OUTPUT}")
        print(f"   共 {self._page_num + 1} 页（含封面）")

# ══════════════════════════════════════════════════════════
#  Markdown → PDF 解析
# ══════════════════════════════════════════════════════════

def strip_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[end+4:].lstrip("\n")
    return text

def parse_and_render(renderer, article_id, article_title, md_text):
    # ── 本期封面页 ─────────────────────────────────────────
    renderer.new_page()

    # 顶部深蓝区
    renderer.cv.saveState()
    renderer.cv.setFillColorRGB(*rgb_hex(COLOR_NAVY))
    renderer.cv.rect(0, PAGE_H - 130, PAGE_W, 130, fill=1, stroke=0)
    renderer.cv.restoreState()

    # 左侧蓝条
    renderer.cv.saveState()
    renderer.cv.setFillColorRGB(*rgb_hex(COLOR_BLUE))
    renderer.cv.rect(0, PAGE_H - 130, 7, 130, fill=1, stroke=0)
    renderer.cv.restoreState()

    # 系列名
    renderer.cv.saveState()
    renderer.cv.setFont(FONT_BODY, 11)
    renderer.cv.setFillColorRGB(0.8, 0.8, 0.8)
    renderer.cv.drawString(MARGIN_L + 12, PAGE_H - 55, "摄 像 机 硬 件 科 普 系 列")
    renderer.cv.restoreState()

    # 橙色装饰条
    renderer.cv.saveState()
    renderer.cv.setFillColorRGB(*rgb_hex(COLOR_ACCENT))
    renderer.cv.rect(MARGIN_L + 12, PAGE_H - 63, 45, 4, fill=1, stroke=0)
    renderer.cv.restoreState()

    # 本期大标题
    renderer.cv.saveState()
    renderer.cv.setFont(FONT_TITLE, 24)
    renderer.cv.setFillColorRGB(1, 1, 1)
    title_str = f"{article_id}  {article_title}"
    renderer.cv.drawString(MARGIN_L + 12, PAGE_H - 92, title_str)
    renderer.cv.restoreState()

    # 正文开始位置
    renderer.y = PAGE_H - 170

    # ── 解析 Markdown ─────────────────────────────────────
    md    = strip_frontmatter(md_text)
    lines = md.split("\n")
    i     = 0
    in_code   = False
    code_buf  = []

    while i < len(lines):
        raw     = lines[i]
        stripped = raw.strip()
        i += 1

        # 代码块
        if stripped.startswith("```"):
            if not in_code:
                in_code, code_buf = True, []
            else:
                in_code = False
                renderer.add_code_block(code_buf)
            continue
        if in_code:
            code_buf.append(stripped)
            continue

        # 忽略 markdown 分隔符
        if stripped in ("---", "***", "___"):
            renderer.add_divider()
            continue

        # 表格
        if stripped.startswith("|") and "|" in stripped[1:]:
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.match(r"^-+$", c) for c in row):
                    table_rows.append(row)
                i += 1
            if table_rows:
                renderer.add_table(table_rows)
            renderer.y -= 6
            continue

        # 标题
        if stripped.startswith("# "):
            renderer.add_heading1(stripped[2:].strip())
        elif stripped.startswith("## "):
            renderer.add_heading2(stripped[3:].strip())
        elif stripped.startswith("### "):
            renderer.add_heading3(stripped[4:].strip())
        # 引用
        elif stripped.startswith(">"):
            renderer.add_paragraph(stripped[1:].strip(),
                                    font=FONT_QUOTE, size=9.5,
                                    color=(0.30, 0.30, 0.50),
                                    indent=8, space_before=4, space_after=4)
        elif re.match(r"^---+$", stripped):
            renderer.add_separator()
        elif stripped:
            renderer.add_paragraph(stripped, size=9.5, color=COLOR_GRAY,
                                   space_after=5)
        else:
            renderer.y -= 4

# ══════════════════════════════════════════════════════════
#  主流程
# ══════════════════════════════════════════════════════════

def build_pdf():
    renderer = PDFRenderer(OUTPUT)

    # ── 全册封面 ───────────────────────────────────────────
    renderer.new_page()

    # 顶部深蓝大区
    renderer.cv.saveState()
    renderer.cv.setFillColorRGB(*rgb_hex(COLOR_NAVY))
    renderer.cv.rect(0, PAGE_H - 310, PAGE_W, 310, fill=1, stroke=0)
    renderer.cv.restoreState()

    # 左侧橙色竖条
    renderer.cv.saveState()
    renderer.cv.setFillColorRGB(*rgb_hex(COLOR_ACCENT))
    renderer.cv.rect(0, PAGE_H - 310, 9, 310, fill=1, stroke=0)
    renderer.cv.restoreState()

    # 系列副标题
    renderer.cv.saveState()
    renderer.cv.setFont(FONT_BODY, 13)
    renderer.cv.setFillColorRGB(0.72, 0.72, 0.72)
    renderer.cv.drawString(MARGIN_L + 20, PAGE_H - 62, "摄 像 机 硬 件 科 普 系 列")
    renderer.cv.restoreState()

    # 橙色装饰条
    renderer.cv.saveState()
    renderer.cv.setFillColorRGB(*rgb_hex(COLOR_ACCENT))
    renderer.cv.rect(MARGIN_L + 20, PAGE_H - 70, 55, 4, fill=1, stroke=0)
    renderer.cv.restoreState()

    # 主标题（分两行）
    renderer.cv.saveState()
    renderer.cv.setFont(FONT_TITLE, 32)
    renderer.cv.setFillColorRGB(1, 1, 1)
    renderer.cv.drawString(MARGIN_L + 20, PAGE_H - 112, "从 传 感 器 到 SOC")
    renderer.cv.restoreState()

    renderer.cv.saveState()
    renderer.cv.setFont(FONT_TITLE, 26)
    renderer.cv.setFillColorRGB(1, 1, 1)
    renderer.cv.drawString(MARGIN_L + 20, PAGE_H - 152, "摄像机硬件知识全解")
    renderer.cv.restoreState()

    # 底部信息
    renderer.cv.saveState()
    renderer.cv.setFont(FONT_BODY, 11)
    renderer.cv.setFillColorRGB(0.55, 0.55, 0.55)
    renderer.cv.drawString(MARGIN_L + 20, PAGE_H - 200, "第001期 ~ 第007期  |  2026年3月")
    renderer.cv.restoreState()

    # 目录
    renderer.y = PAGE_H - 340
    renderer.add_heading2("目  录")
    for _, (art_id, art_title, _) in enumerate(ARTICLES, 1):
        renderer.add_paragraph(f"  {art_id}    {art_title}", size=10,
                                color=COLOR_GRAY, space_after=5)

    # 底部关键词
    kw = ("传感器 · 像素 · 分辨率 · 光学变焦 · 帧率 · 快门 · 光圈 · "
          "ISP · 降噪 · 信噪比 · 传输协议 · SOC")
    renderer.y = 110
    renderer.cv.saveState()
    renderer.cv.setFont(FONT_BODY, 8.5)
    renderer.cv.setFillColorRGB(0.5, 0.5, 0.5)
    renderer.cv.drawCentredString(PAGE_W / 2, 92, kw)
    renderer.cv.restoreState()

    # ── 逐期渲染 ───────────────────────────────────────────
    for art_id, art_title, path in ARTICLES:
        print(f"  [*] 处理中: {art_id} {art_title}")
        md_text = read_md(path)
        parse_and_render(renderer, art_id, art_title, md_text)

    renderer.save(len(ARTICLES))
    return OUTPUT

if __name__ == "__main__":
    p = build_pdf()
    print(f"\n[OK] 文件已保存至: {p}")
