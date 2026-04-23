import os
import sys
import re
import time
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE

# --- 專業視覺參數 ---
VECTOR_BLUE = RGBColor(0, 51, 102)
TEXT_DARK = RGBColor(33, 33, 33)
FONT_MAIN = 'Microsoft JhengHei'

def clean_md_syntax(text):
    """徹底清除 Markdown 語法符號"""
    if not text: return ""
    # 移除粗體/斜體 **, __, *, _
    text = re.sub(r'[\*_]{1,2}(.*?)[\*_]{1,2}', r'\1', text)
    # 移除單獨殘留的星號
    text = text.replace('*', '').strip()
    return text

def apply_text_style(paragraph, size=Pt(18), is_bold=False):
    """統一設定內文樣式"""
    paragraph.font.name = FONT_MAIN
    paragraph.font.size = size
    paragraph.font.bold = is_bold
    paragraph.font.color.rgb = TEXT_DARK

def get_body_placeholder(slide):
    """精準獲取投影片的內容區塊"""
    for shape in slide.placeholders:
        if shape.placeholder_format.type == 2 or shape.placeholder_format.idx == 1:
            return shape
    return None

def set_title_style(title_shape, title_text):
    """動態調整標題，防止字數過多導致溢出邊界"""
    title_text = clean_md_syntax(title_text)
    title_shape.text = title_text
    tf = title_shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.font.name = FONT_MAIN
    p.font.bold = True
    p.font.color.rgb = VECTOR_BLUE
    
    # 根據字數自動縮放
    length = len(title_text)
    if length > 35: p.font.size = Pt(18)
    elif length > 25: p.font.size = Pt(22)
    else: p.font.size = Pt(28)

def add_table_slide(prs, title, table_data):
    """建立專業的表格投影片"""
    slide = prs.slides.add_slide(prs.slide_layouts[1]) # Title and Content
    set_title_style(slide.shapes.title, f"{title} (數據對應)")
    
    # 移除原本的內容預留位置，改用實體表格
    body = get_body_placeholder(slide)
    if body:
        sp = body.element
        sp.getparent().remove(sp)

    rows, cols = len(table_data), len(table_data[0])
    left, top, width = Inches(0.5), Inches(1.4), Inches(9.0)
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, Inches(0.5))
    table = table_shape.table

    for r, row in enumerate(table_data):
        for c, cell_text in enumerate(row):
            cell = table.cell(r, c)
            cell.text = clean_md_syntax(cell_text)
            for p in cell.text_frame.paragraphs:
                p.font.name = FONT_MAIN
                if r == 0: # 標題列
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = VECTOR_BLUE
                    p.font.color.rgb = RGBColor(255, 255, 255)
                    p.font.size = Pt(11)
                    p.font.bold = True
                else:
                    p.font.size = Pt(10)

def create_pptx_from_md(md_file="report.md", output_file="Vector_Presentation.pptx"):
    if not os.path.exists(md_file): return
    
    prs = Presentation()
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # --- 1. 處理封面 ---
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Vector Informatik\n技術研究與硬體對應報告"
    slide.placeholders[1].text = f"自動生成報告\n日期：{time.strftime('%Y-%m-%d')}"

    # --- 2. 解析區域 (以 ## 或 ### 作為換頁點) ---
    sections = re.split(r'\n(?=###? )', content)
    
    for section in sections:
        lines = section.strip().split('\n')
        if not lines: continue
        
        raw_title = lines[0].strip('# ')
        body_lines = lines[1:]
        
        # 過濾出表格與純文字
        table_data = []
        text_content = []
        for line in body_lines:
            line = line.strip()
            if not line or line.startswith('---'): continue
            if line.startswith('|'):
                if '---' in line: continue
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if cells: table_data.append(cells)
            else:
                text_content.append(line)

        # 🚀 處理內容投影片
        if text_content:
            # 如果內容太多，自動分段
            chunk_size = 8
            for i in range(0, len(text_content), chunk_size):
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                set_title_style(slide.shapes.title, raw_title)
                
                body = get_body_placeholder(slide)
                if body:
                    tf = body.text_frame
                    tf.clear() # 關鍵：清除預設的 "Click to add text"
                    for text_line in text_content[i:i+chunk_size]:
                        p = tf.add_paragraph()
                        p.text = clean_md_syntax(text_line)
                        p.space_after = Pt(10)
                        # 根據內容密度自動縮放字體
                        apply_text_style(p, size=Pt(16) if len(text_content) > 5 else Pt(20))

        # 🚀 處理表格投影片
        if table_data:
            add_table_slide(prs, raw_title, table_data)

    prs.save(output_file)
    print(f"✅ 優化版 PPT 已成功產生：{output_file}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "reports/report_001.md"
    create_pptx_from_md(target)
